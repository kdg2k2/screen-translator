# Screen Text Detector and Translator

A Python application that creates a transparent window and detects English text within it, translates it to Vietnamese, and displays the translation in a separate window.

## Features

-   Transparent window (Window A) that can be positioned and resized using standard window controls
-   Detects English text in the area covered by the transparent window
-   Translates detected text to Vietnamese and displays it in a separate window (Window B)
-   Translation window is automatically updated when new text is detected
-   Logs detected text to the terminal
-   Press Escape key to close the application

## Requirements

-   Python 3.6+
-   Tesseract OCR engine
-   Internet connection for translation

## Installation

### 1. Install Tesseract OCR:

#### Windows:

1. Download and install from https://github.com/UB-Mannheim/tesseract/wiki
2. **IMPORTANT:** During installation, check the option "Add to PATH"
3. If you forgot to check "Add to PATH" during installation, you can manually add it:
    - Find the Tesseract installation directory (typically `C:\Program Files\Tesseract-OCR`)
    - Add this to your PATH environment variable:
        - Right-click on This PC/My Computer → Properties → Advanced system settings → Environment Variables
        - Under System Variables, find "Path" and click Edit
        - Click New and add the Tesseract installation directory
        - Click OK to close all dialogs

#### Linux:

```
sudo apt install tesseract-ocr
```

#### macOS:

```
brew install tesseract
```

### 2. Install Python dependencies:

```
pip install -r requirements.txt
```

### 3. Verify Tesseract installation:

Run this command in your terminal/command prompt to check if Tesseract is correctly installed:

```
pytesseract
```

You should see the usage information. If you get a "command not found" error, Tesseract is not properly installed or not in your PATH.

## Usage

Run the application:

```
python screen_translator.py
```

-   Two windows will appear: a transparent window (Window A) with a red border and a translation window (Window B)
-   Position and resize Window A using standard window controls (title bar, edges, corners)
-   Place Window A over the English text you want to detect and translate
-   The Vietnamese translation will appear in Window B
-   The application will scan for text every second and update the translation when new text is detected
-   The original detected English text is logged to the terminal
-   Press Escape to exit the application

## Troubleshooting

### Tesseract not found

If you see an error message about Tesseract not being installed or not in your PATH:

1. Make sure you've installed Tesseract OCR
2. Verify that the Tesseract executable directory is in your PATH
3. Try restarting your terminal/command prompt or computer after adding to PATH
4. If you continue having issues, you can specify the Tesseract path directly in the code:
    - Open screen_translator.py
    - Add this line before using pytesseract: `pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'` (adjust the path to match your installation)

### Translation errors

If you encounter translation errors:

1. Make sure you have an active internet connection
2. The googletrans library might have rate limiting, so if you're making too many requests in a short time, some might fail
3. Try running the application again later
