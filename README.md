# Canvas Auto-Downloader

**A Python script to automatically download all course materials from Canvas LMS with intelligent caching and progress tracking.**

---

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
  - [1. Install Dependencies](#1-install-dependencies)
  - [2. Install the Cookie Editor Extension](#2-install-the-cookie-editor-extension)
  - [3. Export Your Canvas Cookies](#3-export-your-canvas-cookies)
  - [4. Configure the Program](#4-configure-the-program)
  - [5. Run the Downloader](#5-run-the-downloader)
- [Configuration Options](#configuration-options)
- [Static Mode](#static-mode)
- [Notes](#notes)
- [License](#license)

---

## Features

- **Intelligent Caching** - Uses index files to avoid re-downloading existing files
- **Static Mode** - Run without user prompts for automation
- **Efficient** - Only downloads new or updated files

---

## Prerequisites

- **Browser**: One of the following:
  - Google Chrome
  - Firefox
  - Safari
  - Microsoft Edge
  - Opera
- **Python 3.7+** installed on your system
- **pip** for installing Python packages

---

## Installation & Setup

### 1. Install Dependencies

First, install the required Python packages:

```bash
pip install -r requirements.txt
```

### 2. Install the Cookie Editor Extension

Download and install the **Cookie Editor** extension for your browser:

- [Cookie Editor for Chrome](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
- [Cookie Editor for Firefox](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/)
- [Cookie Editor for Safari](https://apps.apple.com/us/app/cookie-editor/id6446215341)
- [Cookie Editor for Edge](https://microsoftedge.microsoft.com/addons/detail/cookieeditor/neaplmfkghagebokkhpjpoebhdledlfi)
- [Cookie Editor for Opera](https://addons.opera.com/en/extensions/details/cookie-editor-2/)

### 3. Export Your Canvas Cookies

1. Open your browser and log in to your Canvas account
2. Open the **Cookie Editor** extension
3. Click **"Export"** and save your cookies in a `.json` file
4. **Rename the file** to `canvas_cookies.json`
5. Place this file in your project folder

⚠️ **Important**: Never share your `canvas_cookies.json` file with anyone!!

### 4. Configure the Program

Edit the `config.json` file to customize the program behavior:

```json
{
    "BASE_URL": "https://yourinstitution.instructure.com",
    "COOKIES_FILE": "canvas_cookies.json",
    "DOWNLOAD_DIR": "CanvasDownloads",
    "WAIT_BETWEEN_REQUESTS": 0.5,
    "SCRIPT_LOG_FILE": "logs/script.log",
    "MAX_LOG_FILES": 5,
    "DATA_FILE": "data/canvas_data.json",
    "static_settings": false,
    "always_reindex": false,
    "always_redownload": false
}
```

See the [Configuration Options](#configuration-options) section for details on each setting.

### 5. Run the Downloader

Open a terminal or command prompt, navigate to the project folder, and run:

```bash
python3 main.py
```

*(On Windows, use `python` instead of `python3` if needed.)*

---

## Configuration Options

| Option | Description | Default Value |
|--------|-------------|---------------|
| `BASE_URL` | The base URL of your Canvas instance | `"https://yourinstitution.instructure.com"` |
| `COOKIES_FILE` | Path to your exported cookies file | `"canvas_cookies.json"` |
| `DOWNLOAD_DIR` | Directory where files will be downloaded | `"CanvasDownloads"` |
| `WAIT_BETWEEN_REQUESTS` | Delay between requests to avoid rate limiting | `0.5` |
| `SCRIPT_LOG_FILE` | Path to the log file | `"logs/script.log"` |
| `MAX_LOG_FILES` | Maximum number of log files to keep | `5` |
| `DATA_FILE` | Path to the index data file | `"data/canvas_data.json"` |
| `static_settings` | Enable static mode (no user prompts) | `false` |
| `always_reindex` | Always re-index courses when in static mode | `false` |
| `always_redownload` | Always re-download files when in static mode | `false` |

---

## Static Mode

When `static_settings` is set to `true` in `config.json`, the program will:

- Not ask for user input
- Use the values from `always_reindex` and `always_redownload`
- Automatically proceed with the configured behavior

---

## Notes

1. **Educational Use Only**: This script is for educational purposes only. Always respect your institution's terms of service.

2. **Security**: Do **NOT** share your `canvas_cookies.json` file with anyone. It contains sensitive authentication information.

3. **Rate Limiting**: If you encounter rate limiting, increase the `WAIT_BETWEEN_REQUESTS` value.

4. **File Organization**: Files are organized by course and module in the download directory.

5. **Logging**: All activity is logged to help with debugging.

---

## License

- This project is licensed under the GNU GPL3 License. See the [LICENSE](LICENSE) file for details.
- Credit to [Jaskejaske1](https://github.com/Jaskejaske1) for the original project.
- Copyright (c) 2025 Jasper Savels
- Copyright (c) 2025 Maxim Huardel

---
