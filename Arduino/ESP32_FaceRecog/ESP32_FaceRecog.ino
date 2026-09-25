#include <Arduino.h>
#include "esp_camera.h"
#include <WiFi.h>
#include "esp_http_server.h"

// ─── Broches ESP32-CAM (AI-Thinker / MB) ─────────────────────
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// ─── WiFi ─────────────────────────────────────────────────────
const char *ssid     = "xxxx";
const char *password = "xxxx";

// ─── MJPEG boundary ───────────────────────────────────────────
#define BOUNDARY "123456789000000000000987654321"

// ─────────────────────────────────────────────────────────────
//   Gestionnaire flux MJPEG  GET /stream (Avec anti-freeze)
// ─────────────────────────────────────────────────────────────
static esp_err_t stream_handler(httpd_req_t *req) {
  camera_fb_t *fb       = NULL;
  esp_err_t     res       = ESP_OK;
  size_t        jpg_len  = 0;
  uint8_t     *jpg_buf  = NULL;
  char         part_buf[128];

  res = httpd_resp_set_type(req, "multipart/x-mixed-replace;boundary=" BOUNDARY);
  if (res != ESP_OK) return res;

  while (true) {
    fb = esp_camera_fb_get();
    if (!fb) {
      res = ESP_FAIL;
    } else {
      if (fb->format != PIXFORMAT_JPEG) {
        bool ok = frame2jpg(fb, 80, &jpg_buf, &jpg_len);
        esp_camera_fb_return(fb);
        fb = NULL;
        if (!ok) res = ESP_FAIL;
      } else {
        jpg_buf = fb->buf;
        jpg_len = fb->len;
      }
    }

    if (res == ESP_OK) {
      size_t hlen = snprintf(part_buf, sizeof(part_buf),
        "--" BOUNDARY "\r\n"
        "Content-Type: image/jpeg\r\n"
        "Content-Length: %u\r\n\r\n", jpg_len);
      res = httpd_resp_send_chunk(req, part_buf, hlen);
    }
    if (res == ESP_OK)
      res = httpd_resp_send_chunk(req, (char *)jpg_buf, jpg_len);
    if (res == ESP_OK)
      res = httpd_resp_send_chunk(req, "\r\n", 2);

    if (fb)      { esp_camera_fb_return(fb); fb = NULL; jpg_buf = NULL; }
    else if (jpg_buf) { free(jpg_buf); jpg_buf = NULL; }

    if (res != ESP_OK) break;

    // Pause pour laisser respirer le processeur et la pile Wi-Fi (évite le freeze)
    vTaskDelay(2 / portTICK_PERIOD_MS);
  }
  return res;
}

// ─────────────────────────────────────────────────────────────
//   Gestionnaire page HTML  GET /
// ─────────────────────────────────────────────────────────────
static esp_err_t index_handler(httpd_req_t *req) {
  const char *html =
    "<!DOCTYPE html><html lang='fr'>"
    "<head><meta charset='utf-8'>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>ESP32-CAM Live</title>"
    "<style>"
    "*{margin:0;padding:0;box-sizing:border-box}"
    "body{background:#0d1117;display:flex;flex-direction:column;"
    "align-items:center;justify-content:center;min-height:100vh;gap:12px}"
    "h1{color:#58a6ff;font-family:'Segoe UI',sans-serif;"
    "font-size:1.1rem;letter-spacing:.05em;opacity:.85}"
    "img{width:100%;max-width:640px;border-radius:8px;"
    "border:2px solid #21262d;display:block}"
    ".badge{font-family:monospace;color:#3fb950;font-size:.78rem;"
    "background:#161b22;padding:4px 12px;border-radius:20px;"
    "border:1px solid #238636}"
    "</style></head>"
    "<body>"
    "<h1>ESP32-CAM &nbsp;|&nbsp; Flux Direct</h1>"
    "<img src='/stream' alt='Flux MJPEG'>"
    "<span class='badge'>QVGA 320×240 · MJPEG</span>"
    "</body></html>";

  httpd_resp_set_type(req, "text/html");
  return httpd_resp_send(req, html, strlen(html));
}

// ─────────────────────────────────────────────────────────────
//   Démarrage du serveur HTTP
// ─────────────────────────────────────────────────────────────
void startCameraServer() {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  httpd_handle_t server = NULL;

  httpd_uri_t index_uri = {
    .uri      = "/",
    .method   = HTTP_GET,
    .handler  = index_handler,
    .user_ctx = NULL
  };
  httpd_uri_t stream_uri = {
    .uri      = "/stream",
    .method   = HTTP_GET,
    .handler  = stream_handler,
    .user_ctx = NULL
  };

  if (httpd_start(&server, &config) == ESP_OK) {
    httpd_register_uri_handler(server, &index_uri);
    httpd_register_uri_handler(server, &stream_uri);
  }
}

// ─────────────────────────────────────────────────────────────
//   SETUP
// ─────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  Serial.println();

  camera_config_t config;
  config.ledc_channel  = LEDC_CHANNEL_0;
  config.ledc_timer    = LEDC_TIMER_0;
  config.pin_d0        = Y2_GPIO_NUM;
  config.pin_d1        = Y3_GPIO_NUM;
  config.pin_d2        = Y4_GPIO_NUM;
  config.pin_d3        = Y5_GPIO_NUM;
  config.pin_d4        = Y6_GPIO_NUM;
  config.pin_d5        = Y7_GPIO_NUM;
  config.pin_d6        = Y8_GPIO_NUM;
  config.pin_d7        = Y9_GPIO_NUM;
  config.pin_xclk      = XCLK_GPIO_NUM;
  config.pin_pclk      = PCLK_GPIO_NUM;
  config.pin_vsync     = VSYNC_GPIO_NUM;
  config.pin_href      = HREF_GPIO_NUM;
  config.pin_sccb_sda  = SIOD_GPIO_NUM;
  config.pin_sccb_scl  = SIOC_GPIO_NUM;
  config.pin_pwdn      = PWDN_GPIO_NUM;
  config.pin_reset     = RESET_GPIO_NUM;
  config.xclk_freq_hz  = 20000000;

  config.frame_size    = FRAMESIZE_QVGA;
  config.pixel_format  = PIXFORMAT_JPEG;
  config.grab_mode     = CAMERA_GRAB_LATEST;
  config.fb_location   = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality  = 18;
  config.fb_count      = 2;

  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("Erreur init camera !");
    return;
  }

  sensor_t *s = esp_camera_sensor_get();
  if (s) {
    s->set_framesize(s, FRAMESIZE_QVGA);
    s->set_quality(s, 18);
    s->set_ae_level(s, 0);
    s->set_aec2(s, 0);
    s->set_gain_ctrl(s, 1);
    s->set_exposure_ctrl(s, 1);
    s->set_whitebal(s, 1);
    s->set_awb_gain(s, 1);
    s->set_bpc(s, 0);
    s->set_wpc(s, 1);
    s->set_raw_gma(s, 1);
    s->set_lenc(s, 0);
  }

  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connecte !");

  startCameraServer();

  Serial.print("Flux direct sur : http://");
  Serial.println(WiFi.localIP());
}

// ─────────────────────────────────────────────────────────────
//   LOOP
// ─────────────────────────────────────────────────────────────
void loop() {
  delay(10000);
}
