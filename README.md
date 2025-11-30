# **Canvas Auto-Downloader: Setup Guide**

## **Prerequisites**
- **Browser:** One of the following:
  - Google Chrome
  - Firefox
  - Safari
  - Microsoft Edge
  - Opera
- **Python 3.x** installed on your system

---

## **Installation & Setup**

### **1. Install the Cookie Editor Extension**
- Download and install the **Cookie Editor** extension for your browser:
    - [Cookie Editor for Chrome](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
    - [Cookie Editor for Firefox](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/)
    - [Cookie Editor for Safari](https://apps.apple.com/us/app/cookie-editor/id6446215341)
    - [Cookie Editor for Edge](https://microsoftedge.microsoft.com/addons/detail/cookieeditor/neaplmfkghagebokkhpjpoebhdledlfi)
    - [Cookie Editor for Opera](https://addons.opera.com/en/extensions/details/cookie-editor-2/)


### **2. Export Your Canvas Cookies**
- Open your browser and log in to your Canvas account.
- Open the **Cookie Editor** extension.
- Click **"Export"** and export your cookies as a `.json` file.
- **Rename the file** to `canvas_cookies.json`.

### **3. Prepare the Project Folder**
- Place the `canvas_cookies.json` file in the **main project folder** (where `canvas_auto_downloader.py` is located).

### **4. Run the Downloader**
- Open a terminal or command prompt.
- Navigate to the project folder.
- Run the script:
  ```bash
  python3 canvas_auto_downloader.py
  ```
  *(On Windows, use `python` instead of `python3` if needed.)*

---

## **Notes**
- This script is for **educational purposes only**. Always respect your institution's terms of service.
- Do **not** share your `canvas_cookies.json` file with anyone!

---
