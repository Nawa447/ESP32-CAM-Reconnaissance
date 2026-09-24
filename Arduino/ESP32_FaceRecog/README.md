# ESP32-CAM — Reconnaissance Faciale (PC + Python)

> **Architecture** : L'ESP32-CAM diffuse un flux vidéo MJPEG en Wi-Fi.
> Un script Python sur ton PC reçoit ce flux, détecte les visages et les reconnaît en temps réel (ou directement via la webcam du PC).

---

## 🎯 Objectif du projet

Ce projet a pour objectif de concevoir un système intelligent de **reconnaissance faciale et de contrôle d'accès biométrique en temps réel**.

Il permet de :

- **Déporter l'intelligence artificielle** : L'ESP32-CAM (ou webcam) capture le flux vidéo, tandis que le PC exécute les calculs lourds de détection et comparaison faciale (HOG / Deep Learning via `face_recognition` et OpenCV).
- **Sécuriser et automatiser l'accès** : Identifier instantanément si une personne se présentant devant la caméra fait partie des personnes autorisées ou s'il s'agit d'un inconnu.
- **Fournir un accueil personnalisé & enrichi** : Afficher un dossier d'information complet (âge estimé, profession, rôle, niveau d'accès) pour des membres clés et profils répertoriés (VIP, intervenants, alumni).

---

## Ce que fait le projet

- **Acquisition vidéo fluide** : Récupération du flux en direct depuis une caméra connectée ESP32-CAM en Wi-Fi ou la webcam intégrée.
- **Reconnaissance biométrique par IA** : Extraction des empreintes faciales (128 descripteurs uniques par visage) et comparaison vectorielle immédiate avec la galerie de référence située dans le dossier `images/`.
- **Fiches d'identité dynamiques (HUD style futuriste)** :
  - Encadrement standard pour les visages identifiés et non identifiés.
  - **Interface biométrique avancée** pour les profils clés (ex. _Julie Valat_, _Julie Montoux_) : viseurs aux coins du visage, badges lumineux et panneau latéral détaillé sans masquer la personne.
- **Performances optimisées anti-lag** : Analyse périodique (1 image sur N) sur version réduite pour préserver un framerate élevé et sans saccade.
- **Journalisation console en direct** : Affichage structuré des détections dans le terminal avec mécanisme anti-spam pour l'historique et l'audit.

---

## Fichiers du projet

```
ESP32_FaceRecog/
├── ESP32_FaceRecog.ino          ← Code à flasher sur l'ESP32-CAM
├── face_recognition_client.py   ← Script Python à lancer sur ton PC
├── requirements.txt             ← Dépendances Python
├── README.md                    ← Guide général du projet
├── README_INSTALLATION.md       ← Guide détaillé d'installation des dépendances (Windows)
└── face_encodings.pkl           ← Base de données des visages (créée automatiquement)
```

---

## PARTIE 1 — Flasher l'ESP32-CAM

### 1.1 — Prérequis Arduino IDE

| Paramètre        | Valeur                               |
| ---------------- | ------------------------------------ |
| Board            | `AI Thinker ESP32-CAM`               |
| Partition Scheme | `Huge APP (3MB No OTA / 1MB SPIFFS)` |
| PSRAM            | `Enabled`                            |
| Upload Speed     | `115200`                             |

> Si tu ne vois pas `AI Thinker ESP32-CAM` dans la liste des boards :
> **Fichier → Préférences → URL gestionnaire de cartes** → ajoute :
> `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
> Puis **Outils → Gestionnaire de cartes** → cherche `esp32` → installer.

---

### 1.2 — Configurer le Wi-Fi

Ouvre `ESP32_FaceRecog.ino` et modifie les lignes 27-28 :

```cpp
const char *ssid     = "TON_WIFI";       // ← Ton réseau Wi-Fi
const char *password = "TON_MOT_DE_PASSE"; // ← Ton mot de passe
```

---

### 1.3 — Câblage pour flasher

L'ESP32-CAM **n'a pas de port USB** natif. Utilise un adaptateur **USB → UART** (CP2102, CH340, FTDI) :

```
Adaptateur USB-UART     ESP32-CAM
      VCC (3.3V ou 5V) → 5V
      GND              → GND
      TX               → U0R  (GPIO3)
      RX               → U0T  (GPIO1)
```

** Avant de cliquer sur "Téléverser" :**
Fais un pont (fil ou pince) entre **IO0** et **GND** — cela met l'ESP32 en mode flash.

**Après le téléversement :**
Enlève le pont IO0-GND, puis appuie sur le bouton **RESET** (ou débranche/rebranche l'alimentation).

---

### 1.4 — Vérifier que ça fonctionne

1. Ouvre le **Moniteur Série** (115200 bauds)
2. Appuie sur **RESET** sur l'ESP32-CAM
3. Tu dois voir :

```
WiFi connecte !
Flux direct sur : http://192.168.X.X
```

4. Ouvre cette URL dans ton navigateur → tu dois voir le flux vidéo en direct

> **Note l'adresse IP** — tu en auras besoin pour le script Python.

---

## PARTIE 2 — Installer Python et les dépendances

> **Consulte le guide dédié pas à pas :** [README_INSTALLATION.md](file:///c:/Users/hassa/Documents/Arduino/ESP32_FaceRecog/README_INSTALLATION.md)
> Ce guide détaille toutes les méthodes d'installation sous Windows (sans compilation, avec CMake, ou avec Conda) pour éviter les erreurs fréquentes avec `dlib`.

### 2.1 — Python 3.9 ou 3.10 recommandé

Télécharge Python sur [python.org](https://www.python.org/downloads/) (3.9 ou 3.10).
Lors de l'installation, coche **"Add Python to PATH"**.

Vérifie l'installation :

```powershell
python --version
```

---

### 2.2 — Installer CMake et les Build Tools (Windows uniquement)

La bibliothèque `face-recognition` utilise **dlib** qui doit être compilé. Il faut :

**Étape A — CMake :**
Télécharge et installe [CMake](https://cmake.org/download/) (version ≥ 3.20).
Lors de l'installation, choisis **"Add CMake to the system PATH"**.

**Étape B — Visual Studio Build Tools :**
Télécharge [Visual Studio Build Tools](https://visualstudio.microsoft.com/fr/visual-cpp-build-tools/).
Lance l'installateur → coche **"Développement Desktop en C++"** → Installer.

> Ces deux étapes sont **obligatoires sur Windows**. Sans elles, `pip install face-recognition` échoue.

---

### 2.3 — Installer les bibliothèques Python

Dans un terminal PowerShell, dans le dossier du projet :

```powershell
cd "C:\Users\hassa\Documents\Arduino\ESP32_FaceRecog"
pip install -r requirements.txt
```

L'installation de `face-recognition` peut prendre **5 à 10 minutes** (compilation de dlib).

---

## PARTIE 3 — Lancer la reconnaissance faciale

### 3.1 — Lancer le script

```powershell
python face_recognition_client.py --url http://192.168.X.X/stream
```

> Remplace `192.168.X.X` par l'IP affichée dans le moniteur série de ton ESP32.

---

### 3.2 — Fenêtre qui s'ouvre

```
┌─────────────────────────────────────────┐
│ FPS: 12.3   Visages: 1   Reconnaissance │
│                                         │
│         [flux vidéo ESP32-CAM]          │
│                                         │
│  E:Enrôler  D:Supprimer  L:Liste  Q:Quit│
└─────────────────────────────────────────┘
```

| Indicateur         | Description                       |
| ------------------ | --------------------------------- |
| 🟩 Boîte **verte** | Visage reconnu — le nom s'affiche |
| 🟥 Boîte **rouge** | Visage inconnu                    |
| FPS                | Images analysées par seconde      |

---

## PARTIE 4 — Enrôler un visage

> Enrôler = apprendre à reconnaître une personne.

1. **Place ton visage** bien centré dans le flux vidéo
2. Assure-toi qu'une **boîte rouge** apparaît (visage détecté)
3. Appuie sur **`E`** dans la fenêtre OpenCV
4. Dans le **terminal**, tape le prénom et appuie sur Entrée :
   ```
   Prénom pour ce visage : Alice
   [ENROLL] 'Alice' enregistré ! Total : 1
   ```
5. La boîte devient **verte** avec le prénom affiché

> **Conseil :** Enrôle la même personne sous plusieurs angles (face, légèrement de côté, avec/sans lunettes) pour améliorer la précision. Il suffit d'utiliser le même prénom plusieurs fois.

---

## PARTIE 5 — Supprimer un visage

1. Appuie sur **`D`** dans la fenêtre OpenCV
2. Dans le terminal :
   ```
   Prénom à supprimer : Alice
   [DELETE] 'Alice' supprimé.
   ```

---

## PARTIE 6 — Lister les visages enregistrés

Appuie sur **`L`** dans la fenêtre OpenCV :

```
[DB] 3 visage(s) : Alice, Bob, Charlie
```

---

## Réglages avancés

### Changer la tolérance de reconnaissance

```powershell
# Plus strict (moins de faux positifs)
python face_recognition_client.py --url http://192.168.X.X/stream --tolerance 0.4

# Plus permissif (reconnaît de plus loin / angles)
python face_recognition_client.py --url http://192.168.X.X/stream --tolerance 0.65
```

| Valeur | Comportement                              |
| ------ | ----------------------------------------- |
| `0.35` | Très strict — uniquement si c'est évident |
| `0.50` | Défaut — bon équilibre                    |
| `0.65` | Permissif — peut avoir des faux positifs  |

### Modifier la vitesse d'analyse

Dans `face_recognition_client.py`, ligne ~35 :

```python
PROCESS_EVERY = 2   # Analyser 1 frame sur 2 (défaut)
                    # Mettre 1 pour analyser chaque frame (plus lent)
                    # Mettre 3 pour être plus fluide (moins précis)
```

---

## Problèmes fréquents

| Problème                                   | Solution                                                                          |
| ------------------------------------------ | --------------------------------------------------------------------------------- |
| `No module named 'face_recognition'`       | Relancer `pip install -r requirements.txt`                                        |
| Erreur de compilation dlib                 | Installer CMake + Visual Studio Build Tools (voir 2.2)                            |
| Fenêtre noire "Connexion au flux..."       | Vérifier l'IP de l'ESP32, que le flux `/stream` est accessible dans le navigateur |
| Visage non détecté                         | Meilleure lumière, visage de face, distance 30–80 cm                              |
| Faux positifs (mauvaise personne reconnue) | Réduire `--tolerance` (ex: `0.4`)                                                 |
| FPS très bas                               | Augmenter `PROCESS_EVERY` à 3 ou 4 dans le script                                 |

---

## Comment ça marche

```
ESP32-CAM (Wi-Fi)
      │
      │  Flux MJPEG (HTTP)
      ▼
face_recognition_client.py
      │
      ├─ Décode chaque frame JPEG
      ├─ Réduit la résolution (×0.5) pour la vitesse
      ├─ face_recognition → localise les visages (HOG)
      ├─ face_recognition → calcule l'encodage (128 dimensions)
      ├─ Compare avec face_encodings.pkl
      │      distance ≤ tolérance → RECONNU
      │      distance > tolérance → inconnu
      └─ Affiche le résultat avec OpenCV
```

---

_Projet : ESP32-CAM Face Recognition | ESP32 core 3.x compatible_
