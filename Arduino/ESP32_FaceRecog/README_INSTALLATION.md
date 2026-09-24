# Guide Complet : Installation des Dépendances (Windows)

Ce guide t'explique pas à pas comment installer toutes les dépendances pour faire tourner le script Python de reconnaissance faciale [`face_recognition_client.py`](file:///c:/Users/hassa/Documents/Arduino/ESP32_FaceRecog/face_recognition_client.py).

---

## Les dépendances nécessaires

Le script utilise 4 bibliothèques principales listées dans [`requirements.txt`](file:///c:/Users/hassa/Documents/Arduino/ESP32_FaceRecog/requirements.txt) :

1. **`opencv-python`** : Récupère le flux vidéo MJPEG de l'ESP32-CAM et affiche l'interface graphique.
2. **`numpy`** : Gestion des matrices d'images en mémoire.
3. **`requests`** : Communication HTTP avec l'ESP32.
4. **`face-recognition`** : Détecte et compare les visages par intelligence artificielle (basé sur **dlib**).

> [!WARNING]
> **Pourquoi cette installation est spéciale sur Windows ?**
> `face-recognition` utilise la bibliothèque C++ `dlib`. Sur Windows, si tu n'as pas de compilateur C++ ou une version trop récente de Python (comme Python 3.13 ou 3.14), `pip install face-recognition` échouera avec de longs messages d'erreur rouges (**CMake** ou **Visual C++ 14.0** manquant).
> **Pas de panique : suis l'une des solutions ci-dessous !**

---

## Étape 0 : Vérifier ta version de Python

Ouvre un terminal **PowerShell** et tape :

```powershell
py --version
```

### Règle d'or pour la version de Python :

- **Python 3.10 ou 3.11 (Idéal)** : Toutes les dépendances s'installent en quelques secondes sans erreur.
- **Python 3.12** : Fonctionne généralement bien avec les versions récentes.
- **Python 3.14 (trop récent)** : Aucune version précompilée de `dlib` n'existe encore pour Python 3.14. Si tu as installé Python 3.14, il est vivement conseillé d'installer **Python 3.10 ou 3.11** en parallèle depuis [python.org/downloads](https://www.python.org/downloads/) (n'oublie pas de cocher _"Add Python to PATH"_ lors de l'installation).

---

## Option A (Recommandée & Rapide) : Installation Pas-à-Pas

### 1. Se placer dans le dossier du projet

Ouvre PowerShell et navigue dans ton dossier :

```powershell
cd "C:\Users\hassa\Documents\Arduino\ESP32_FaceRecog"
```

### 2. (Conseillé) Créer un environnement virtuel

Pour éviter tout conflit sur ton système Windows :

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

_(Si PowerShell bloque le script d'activation, exécute d'abord `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` puis réessaie)._

### 3. Mettre à jour `pip` et les outils de base

```powershell
py -m pip install --upgrade pip setuptools wheel
```

### 4. Installer d'abord OpenCV, NumPy et Requests

Ces trois-là s'installent immédiatement sans compilation :

```powershell
py -m pip install opencv-python numpy requests
```

### 5. Installer `dlib` et `face-recognition`

#### Cas 1 : Avec une roue précompilée (Sans installer Visual Studio)

C'est le moyen le plus simple sur Windows pour éviter d'installer 10 Go d'outils C++ :

```powershell
py -m pip install cmake
py -m pip install dlib-bin
py -m pip install face-recognition
```

_(Si `dlib-bin` n'est pas disponible pour ta version de Python, passe au Cas 2 ci-dessous)._

---

## Option B (Standard) : Avec CMake et Visual Studio C++

Si l'option A échoue ou si `pip` veut compiler `dlib` depuis les sources :

### 1. Installer CMake

1. Télécharge l'installateur Windows (.msi) sur : [https://cmake.org/download/](https://cmake.org/download/)
2. Pendant l'installation, choisis impérativement :
   **"Add CMake to the system PATH for all users"** (ou for current user).

### 2. Installer Visual Studio Build Tools

1. Télécharge : [Visual Studio C++ Build Tools](https://visualstudio.microsoft.com/fr/visual-cpp-build-tools/)
2. Lance l'installateur.
3. Dans la liste des composants, coche :
   **"Développement Desktop en C++"** (Desktop development with C++).
4. Clique sur **Installer** en bas à droite (environ 2 à 4 Go).
5. Redémarre ton ordinateur une fois l'installation terminée.

### 3. Lancer l'installation des dépendances

Ouvre un terminal dans le dossier et lance :

```powershell
cd "C:\Users\hassa\Documents\Arduino\ESP32_FaceRecog"
py -m pip install -r requirements.txt
```

_(La compilation de dlib peut prendre entre 3 et 8 minutes, laisse tourner sans fermer la fenêtre)._

---

## Option C (La solution magique : Conda / Miniconda)

Si tu as **Anaconda** ou **Miniconda** (ou que tu souhaites l'installer depuis [anaconda.com/download](https://www.anaconda.com/download)), Conda fournit des binaires `dlib` déjà compilés pour Windows qui s'installent en 10 secondes :

```powershell
# 1. Créer un environnement avec Python 3.10
conda create -n esp32cam python=3.10 -y
conda activate esp32cam

# 2. Installer dlib via conda-forge (binaire direct, zéro compilation C++)
conda install -c conda-forge dlib -y

# 3. Installer le reste via pip
pip install face-recognition opencv-python requests
```

---

## Vérification finale : Tout fonctionne-t-il ?

Pour tester en une seule ligne si toutes les bibliothèques sont opérationnelles, exécute cette commande dans ton terminal :

```powershell
py -c "import cv2, numpy, requests, face_recognition; print('\n>>> TOUTES LES DEPENDANCES SONT INSTALLEES AVEC SUCCES ! <<<')"
```

Si tu vois s'afficher :

```
>>> TOUTES LES DEPENDANCES SONT INSTALLEES AVEC SUCCES ! <<<
```

Félicitations, tout est prêt !

---

## Résolution des erreurs fréquentes

### 1. _"Python est introuvable ; exécutez sans arguments..."_

- **Cause** : Windows a un raccourci par défaut vers le Microsoft Store.
- **Solution** :
  1. Utilise `py` au lieu de `python` (ex: `py face_recognition_client.py`).
  2. Ou va dans les paramètres Windows : **Paramètres → Applications → Paramètres d'application avancés → Alias d'exécution d'application**, puis désactive les commutateurs "Python" et "Python3".

### 2. _"CMake must be installed to build dlib"_

- **Solution** : Installe CMake (`py -m pip install cmake` ou via l'installateur officiel sur cmake.org) et assure-toi qu'il est coché dans le PATH.

### 3. _"Microsoft Visual C++ 14.0 or greater is required"_

- **Solution** : Suis l'**Option B** pour installer les Visual Studio Build Tools, ou utilise l'**Option C (Conda)** pour contourner totalement le besoin de compilateur C++.
