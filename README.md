# 🎬 UCA - SubFix (AI Subtitle Studio)

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flet](https://img.shields.io/badge/Flet-Framework-2EA043?style=for-the-badge&logo=flutter&logoColor=white)
![Gemini](https://img.shields.io/badge/AI-Google%20Gemini%201.5-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Status](https://img.shields.io/badge/Status-Production-success?style=for-the-badge)

> **UCA - SubFix** is a specialized desktop application designed to automate the correction of subtitles (`.srt` and `.vtt`) for technical training videos at **Universidade Corporativa Alterdata**.

It combines **Generative AI (Google Gemini 1.5 Flash)** with **Regex-based Rule Enforcement** to fix phonetic errors, specific Rio de Janeiro accents ("Carioca"), and technical product terminology that standard ASR (Automatic Speech Recognition) tools fail to capture.

---

## 📸 Screenshots

<div align="center">
  <img src="assets/screenshots/preview.png" alt="Application Interface" width="100%">
  <br>
</div>

---

## 🚀 The Problem it Solves

Standard transcription services (like Vimeo or YouTube auto-captions) struggle with:

1.  **Technical Jargon:** Confusing "Spice Desktop" with "os pais" or "spi se".
2.  **Brand Names:** Writing "Alter data" instead of "Alterdata".
3.  **Local Accents:** Misinterpreting the "Carioca" accent (Rio de Janeiro), leading to severe phonetic errors.
4.  **Context:** Failing to understand if "comando" refers to the verb or the product "Comanda Mobile".

### 💡 The Solution (Hybrid Engine)
**SubFix solves this by using a two-layer approach:**
* **Layer 1 (AI):** Uses Gemini 1.5 to understand the full context of the lesson, fix grammar, punctuation, and sentence structure.
* **Layer 2 (Code):** Applies a "Brute Force" Regex filter to guarantee 100% accuracy on corporate product names.

---

## ✨ Key Features

* **Context-Aware Correction:** Upload PDF manuals to feed the AI with specific domain knowledge before processing.
* **Smart Batch Processing:** Processes entire folders of subtitles automatically.
* **Hybrid Correction Engine:**
    * Fixes specific product names: *Bimer, Pack, Shop, Spice, Comanda*.
    * Fixes common transcription vices: *vae -> vai*, *eh -> é*.
* **Modern UI:** Built with **Flet** (Flutter for Python), featuring a responsive Dark Mode interface.
* **Security:** API Keys are input by the user at runtime and are not hardcoded.
* **Executable:** Compiles into a single portable `.exe` file.

---

## 🛠️ Tech Stack

* **Language:** Python 3.11+
* **GUI Framework:** [Flet](https://flet.dev/)
* **AI Model:** Google Gemini 1.5 Flash (via `google-generativeai`)
* **Utilities:** `re` (Regex), `sys`, `os`
* **Build Tool:** PyInstaller / Flet Pack

---

## 📦 How to Run (Development)

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/kenjishimizu2411/UCA_SubFix.git](https://github.com/kenjishimizu2411/UCA_SubFix.git)
    cd UCA_SubFix
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    
    # Windows
    .\venv\Scripts\activate
    
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: Ensure `flet`, `google-generativeai` and `pyinstaller` are installed)*

4.  **Run the App:**
    ```bash
    flet run main.py
    ```

---

## 🏗️ How to Build (.EXE)

To generate the standalone executable for Windows distribution:

1.  Ensure you have the assets folder (`assets/`) containing `logo_uca.ico` and `logo_uca.png`.
2.  Run the packing command (using Flet Pack to handle metadata):

```powershell
flet pack main.py --name "UCA_SubFix" --icon "assets/logo_uca.ico" --add-data "assets;assets"
```
> The output file will be located in the `dist/` folder.

---

## 📝 Usage Guide

1.  **Step 1:** Select the folder containing the raw `.srt` or `.vtt` files.
2.  **Step 2 (Optional):** Select PDF manuals to provide context to the AI.
3.  **Step 3:** Enter your **Google AI Studio API Key**.
4.  **Step 4:** Click **EXECUTE CORRECTION**.
5.  **Step 5:** Monitor the "Execution Log". The corrected files will be saved in the same folder with the suffix `_corrigido`.

---

<p align="center">
<strong>Developed for Universidade Corporativa Alterdata</strong><br>
👤 <strong>Kenji Shimizu</strong><br>
<a href="https://github.com/kenjishimizu2411">GitHub Profile</a>
</p>
