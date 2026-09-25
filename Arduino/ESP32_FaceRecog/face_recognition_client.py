import os
import time
import cv2
import face_recognition
import numpy as np

# ─── Profils Spéciaux Détaillés (Affichage étendu d'informations) ─────────
julie_montaux_profile = {
    "Nom": "Julie Montoux",
    "Age estime": "38 ans",
    "Profession": "Ex-Alternante Credit Agricole",
    "Profession_courte": "Diplomee EPSI",
    "Etablissement": "Campus EPSI Toulouse",
    "Formation": "Nouvellement diplomee EPSI",
    "Parcours": "Alternance Credit Agricole",
    "Statut": "AUTORISE (Alumni EPSI)",
    "Niveau": "Niveau 4 (Alumni)",
}

SPECIAL_PROFILES = {
    "Julie Valat": {
        "Nom": "Julie Valat",
        "Age estime": "50 ans",
        "Profession": "Coach My DIL / Formatrice",
        "Profession_courte": "Coach My DIL",
        "Etablissement": "Campus EPSI Toulouse",
        "Role": "Accompagnement & Pedagogie",
        "Specialite": "Coaching & Bien-etre",
        "Statut": "AUTORISE (Badge Or VIP)",
        "Niveau": "Niveau 5 (Prioritaire)",
    },
    "Julie Montoux": julie_montaux_profile,
}

last_vip_log_time = 0


def draw_special_hud(frame, person_data, face_box):
    """Dessine une interface futuriste / fiche biométrique complète pour les profils spéciaux"""
    h, w = frame.shape[:2]
    top, right, bottom, left = face_box

    # Couleur dorée pour Julie Valat, cyan/émeraude pour Julie Montaux
    if "Valat" in person_data.get("Nom", ""):
        box_color = (0, 215, 255)  # Or / Ambre (BGR)
        accent_color = (0, 140, 255)  # Orange vif
        badge_title = f"★ VIP : {person_data['Nom']} ★"
    else:
        box_color = (255, 215, 0)  # Cyan clair / Émeraude (BGR)
        accent_color = (180, 105, 255)  # Rose / Violet moderne
        badge_title = f"★ ALUMNI : {person_data['Nom']} ★"

    # 1. Coins renforcés style ciblage biométrique sur le visage
    corner_len = max(12, min(25, (right - left) // 4, (bottom - top) // 4))
    cv2.rectangle(frame, (left, top), (right, bottom), box_color, 1)

    # Coin haut-gauche
    cv2.line(frame, (left, top), (left + corner_len, top), box_color, 3)
    cv2.line(frame, (left, top), (left, top + corner_len), box_color, 3)
    # Coin haut-droit
    cv2.line(frame, (right, top), (right - corner_len, top), box_color, 3)
    cv2.line(frame, (right, top), (right, top + corner_len), box_color, 3)
    # Coin bas-gauche
    cv2.line(frame, (left, bottom), (left + corner_len, bottom), box_color, 3)
    cv2.line(frame, (left, bottom), (left, bottom - corner_len), box_color, 3)
    # Coin bas-droit
    cv2.line(frame, (right, bottom), (right - corner_len, bottom), box_color, 3)
    cv2.line(frame, (right, bottom), (right, bottom - corner_len), box_color, 3)

    # Badge flottant au-dessus du visage
    tag_size, _ = cv2.getTextSize(badge_title, cv2.FONT_HERSHEY_DUPLEX, 0.45, 1)
    tag_y_top = max(0, top - 24)
    tag_y_bot = max(0, top)
    cv2.rectangle(
        frame,
        (left, tag_y_top),
        (left + tag_size[0] + 12, tag_y_bot),
        accent_color,
        -1,
    )
    cv2.putText(
        frame,
        badge_title,
        (left + 6, max(14, top - 8)),
        cv2.FONT_HERSHEY_DUPLEX,
        0.45,
        (255, 255, 255),
        1,
    )

    # Sous-titre sous le visage
    subtag_text = f"Age: {person_data.get('Age estime', 'N/A')} | {person_data.get('Profession_courte', 'Staff')}"
    sub_size, _ = cv2.getTextSize(subtag_text, cv2.FONT_HERSHEY_DUPLEX, 0.40, 1)
    cv2.rectangle(
        frame,
        (left, bottom),
        (left + sub_size[0] + 12, min(h, bottom + 20)),
        (30, 30, 30),
        -1,
    )
    cv2.putText(
        frame,
        subtag_text,
        (left + 6, min(h - 4, bottom + 15)),
        cv2.FONT_HERSHEY_DUPLEX,
        0.40,
        (0, 255, 255),
        1,
    )

    # 2. Fiche d'information détaillée (HUD)
    card_w = 330 if w >= 600 else min(290, w - 20)

    # Lignes d'informations dynamiques
    lines = [
        ("Nom", person_data.get("Nom", "N/A")),
        ("Age estime", person_data.get("Age estime", "N/A")),
    ]
    for k, v in person_data.items():
        if k not in ("Nom", "Age estime", "Profession_courte"):
            lines.append((k, v))

    card_h = 42 + len(lines) * 20 + 8

    # Positionnement intelligent du panneau : à l'opposé du visage pour ne jamais le masquer
    if left > w // 2:
        card_x = 12
    else:
        card_x = max(10, w - card_w - 12)
    card_y = 12
    card_y_end = min(h - 10, card_y + card_h)

    # Fond semi-transparent haute lisibilité
    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (card_x, card_y),
        (card_x + card_w, card_y_end),
        (18, 20, 26),
        -1,
    )
    cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)

    # Cadre et en-tête du panneau
    cv2.rectangle(frame, (card_x, card_y), (card_x + card_w, card_y_end), box_color, 1)
    header_color = (
        (0, 140, 230) if "Valat" in person_data.get("Nom", "") else (160, 90, 220)
    )
    cv2.rectangle(
        frame,
        (card_x, card_y),
        (card_x + card_w, card_y + 28),
        header_color,
        -1,
    )
    cv2.putText(
        frame,
        f"DOSSIER IDENTITE [{person_data['Nom'].upper()}]",
        (card_x + 10, card_y + 19),
        cv2.FONT_HERSHEY_DUPLEX,
        0.42,
        (255, 255, 255),
        1,
    )

    curr_y = card_y + 48
    for label, val in lines:
        if curr_y > card_y_end - 6:
            break
        cv2.putText(
            frame,
            f"{label}:",
            (card_x + 10, curr_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.36,
            (180, 220, 255),
            1,
        )
        val_str = str(val)[:29]
        cv2.putText(
            frame,
            val_str,
            (card_x + 105, curr_y),
            cv2.FONT_HERSHEY_DUPLEX,
            0.36,
            (255, 255, 255),
            1,
        )
        curr_y += 20


# ─── Chargement de la base de données des visages ────────────────
known_face_encodings = []
known_face_names = []

images_dir = "images"
if os.path.exists(images_dir):
    for filename in os.listdir(images_dir):
        if filename.endswith((".jpg", ".jpeg", ".png", ".webp")):
            image_path = os.path.join(images_dir, filename)
            img = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(img)
            if len(encodings) > 0:
                known_face_encodings.append(encodings[0])
                name = os.path.splitext(filename)[0]
                known_face_names.append(name)
                print(f"[INIT] Visage chargé : {name}")
else:
    print(
        "[ATTENTION] Le dossier 'images/' n'existe pas. Créez-le et ajoutez des photos !"
    )

esp32_url = "http://10.204.142.190/stream"
print("Démarrage du client de reconnaissance avec l'ESP32-CAM...")

# ─── Configuration de la fenêtre d'affichage agrandie ──────────
window_name = "ESP32-CAM | Reconnaissance Faciale"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 640, 480)  # Agrandit la fenêtre pour tout voir

# ─── Paramètres d'optimisation anti-lag ────────────────────────
PROCESS_EVERY_N_FRAMES = 6  # Analyse 1 image sur 6
frame_count = 0
face_locations = []
face_names = []

while True:
    print(f"\n[CONNEXION] Tentative de connexion à {esp32_url} ...")
    video_capture = cv2.VideoCapture(esp32_url)

    # Forcer la résolution à 320x240 pour l'ESP32-CAM
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    if not video_capture.isOpened():
        print(
            "[ERREUR] Impossible de joindre l'ESP32. Nouvelle tentative dans 3 secondes..."
        )
        time.sleep(3)
        continue

    print("Flux ouvert avec succès ! Appuyez sur 'q' pour quitter.")

    flux_perdu = False
    while not flux_perdu:
        ret, frame = video_capture.read()

        if not ret or frame is None:
            print("[AVERTISSEMENT] Perte du flux de l'ESP32, reconnexion...")
            flux_perdu = True
            break

        frame_count += 1

        # On effectue le calcul de reconnaissance uniquement une frame sur N
        if frame_count % PROCESS_EVERY_N_FRAMES == 0:
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            current_locations = face_recognition.face_locations(
                rgb_small_frame, model="hog"
            )
            current_encodings = face_recognition.face_encodings(
                rgb_small_frame, current_locations
            )

            current_names = []
            for face_encoding in current_encodings:
                name = "Inconnu"
                if len(known_face_encodings) > 0:
                    matches = face_recognition.compare_faces(
                        known_face_encodings, face_encoding, tolerance=0.6
                    )
                    face_distances = face_recognition.face_distance(
                        known_face_encodings, face_encoding
                    )

                    if True in matches:
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = known_face_names[best_match_index]

                current_names.append(name)

            # Mise à jour des variables globales pour les frames intermédiaires
            face_locations = current_locations
            face_names = current_names

        # Affichage sur le flux en direct
        special_faces_to_draw = []

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2

            # Profils spéciaux (Julie Valat, Julie Montaux)
            if name in SPECIAL_PROFILES:
                profile_data = SPECIAL_PROFILES[name]
                special_faces_to_draw.append((profile_data, (top, right, bottom, left)))

                # Journalisation détaillée dans la console (anti-spam : toutes les 4s)
                current_time = time.time()
                if current_time - last_vip_log_time > 4.0:
                    last_vip_log_time = current_time
                    print("\n" + "=" * 60)
                    print(
                        f"★ [IDENTIFICATION SPECIALE] {profile_data['Nom']} reconnue !"
                    )
                    print("-" * 60)
                    for k, v in profile_data.items():
                        if k != "Profession_courte":
                            print(f"  • {k:<15} : {v}")
                    print("=" * 60 + "\n")
            else:
                # Affichage standard pour toutes les autres personnes
                color = (0, 255, 0) if name != "Inconnu" else (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(
                    frame,
                    name,
                    (left, top - 10),
                    cv2.FONT_HERSHEY_DUPLEX,
                    0.6,
                    color,
                    2,
                )

        # Affichage de la fiche et du HUD pour les profils spéciaux détectés
        for profile_data, face_box in special_faces_to_draw:
            draw_special_hud(frame, profile_data, face_box)

        cv2.imshow(window_name, frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            video_capture.release()
            cv2.destroyAllWindows()
            print("Arrêt du programme.")
            exit()

    video_capture.release()
    time.sleep(2)
