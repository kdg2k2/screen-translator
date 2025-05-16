import sys
import time
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QMessageBox, QTextEdit, QVBoxLayout, QWidget, QHBoxLayout, QSpinBox, QPushButton
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QRect
from PyQt5.QtGui import QFont, QPainter, QPen, QColor
import numpy as np
from PIL import ImageGrab
from googletrans import Translator

# Check for pytesseract before importing
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
    
    # If Tesseract is not in PATH, you can uncomment and modify the line below
    # to point to your Tesseract installation
    pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract.exe'
    
except ImportError:
    TESSERACT_AVAILABLE = False

class ResultWindow(QMainWindow):
    resize_scanner = pyqtSignal(int, int)
    toggle_scanning = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.translator = Translator()
        self.scanning_active = True
        self.initUI()
        
    def initUI(self):
        # Set window properties
        self.setWindowTitle('Vietnamese Translation')
        self.setGeometry(750, 100, 400, 400)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create layout for width and height controls
        size_layout = QHBoxLayout()
        
        # Width input
        width_label = QLabel("Width:")
        self.width_input = QSpinBox()
        self.width_input.setRange(100, 1200)
        self.width_input.setValue(600)
        self.width_input.valueChanged.connect(self.on_size_changed)
        size_layout.addWidget(width_label)
        size_layout.addWidget(self.width_input)
        
        # Height input
        height_label = QLabel("Height:")
        self.height_input = QSpinBox()
        self.height_input.setRange(100, 1000)
        self.height_input.setValue(400)
        self.height_input.valueChanged.connect(self.on_size_changed)
        size_layout.addWidget(height_label)
        size_layout.addWidget(self.height_input)
        
        layout.addLayout(size_layout)
        
        # Add pause/resume button
        self.scan_button = QPushButton("Pause Scan")
        self.scan_button.clicked.connect(self.toggle_scan)
        layout.addWidget(self.scan_button)
        
        # Create label for the translation
        translated_label = QLabel("Vietnamese Translation:")
        layout.addWidget(translated_label)
        
        # Create text edit for displaying translation
        self.translated_text_display = QTextEdit()
        self.translated_text_display.setReadOnly(True)
        self.translated_text_display.setFont(QFont('Arial', 12))
        layout.addWidget(self.translated_text_display)
        
        # Status label to show scan status
        self.status_label = QLabel("Scanning: Active")
        layout.addWidget(self.status_label)
        
        # Show the window
        self.show()
    
    def toggle_scan(self):
        # Toggle scanning state
        self.scanning_active = not self.scanning_active
        
        # Update button text
        self.scan_button.setText("Resume Scan" if not self.scanning_active else "Pause Scan")
        
        # Emit signal to transparent window
        self.toggle_scanning.emit(self.scanning_active)
    
    def update_scanner_size_inputs(self, width, height):
        # Update the input fields without triggering valueChanged
        self.width_input.blockSignals(True)
        self.height_input.blockSignals(True)
        
        self.width_input.setValue(width)
        self.height_input.setValue(height)
        
        self.width_input.blockSignals(False)
        self.height_input.blockSignals(False)
    
    def on_size_changed(self):
        # Emit signal to resize the scanner window
        width = self.width_input.value()
        height = self.height_input.value()
        self.resize_scanner.emit(width, height)
        
    def update_text(self, text):
        try:
            # Translate the text to Vietnamese
            translated = self.translator.translate(text, src='en', dest='vi')
            # Update the translated text display
            self.translated_text_display.setText(translated.text)
        except Exception as e:
            self.translated_text_display.setText(f"Translation error: {str(e)}")
            print(f"Translation error: {e}")
            
    def update_status(self, is_scanning):
        self.scanning_active = is_scanning
        status = "Active" if is_scanning else "Paused"
        self.status_label.setText(f"Scanning: {status}")
        
        # Update button text to match the current state
        self.scan_button.setText("Pause Scan" if is_scanning else "Resume Scan")

class TrulyTransparentWindow(QWidget):
    text_detected = pyqtSignal(str)
    scan_status_changed = pyqtSignal(bool)
    size_changed = pyqtSignal(int, int)
    
    def __init__(self, result_window):
        super().__init__()
        self.result_window = result_window
        self.last_detected_text = ""
        self.border_width = 3  # Border width for drawing
        self.scanning = True   # Whether scanning is active
        
        # Connect the signals to the result window
        self.text_detected.connect(self.result_window.update_text)
        self.scan_status_changed.connect(self.result_window.update_status)
        self.size_changed.connect(self.result_window.update_scanner_size_inputs)
        self.result_window.resize_scanner.connect(self.set_new_size)
        self.result_window.toggle_scanning.connect(self.set_scanning_state)
        
        # Check for Tesseract installation first
        if TESSERACT_AVAILABLE:
            try:
                # Try to get tesseract version to verify it's working
                pytesseract.get_tesseract_version()
            except Exception as e:
                QMessageBox.critical(
                    None, 
                    "Tesseract Error",
                    "Tesseract OCR is not properly installed or not in your PATH.\n\n"
                    "Please ensure you have Tesseract installed and added to your PATH.\n"
                    "Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki\n"
                    "During installation, check 'Add to PATH'\n\n"
                    "Alternatively, you can open screen_translator.py and uncomment the line:\n"
                    "pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'\n"
                    "and adjust the path to match your installation.\n\n"
                    "The application will continue but OCR will not work."
                )
                print("Tesseract Error: Tesseract is not properly installed or not in your PATH.")
                print("Please see README.md for installation instructions.")
                print("Or uncomment and adjust the tesseract_cmd line in the code.")
        else:
            QMessageBox.critical(
                None, 
                "Import Error",
                "Failed to import pytesseract. Please install it with:\n"
                "pip install pytesseract\n\n"
                "The application will continue but OCR will not work."
            )
            print("Import Error: pytesseract module not found.")
            print("Install it with: pip install pytesseract")
        
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.detect_text)
        self.timer.start(1000)  # Detect text every second
    
    def set_scanning_state(self, is_scanning):
        self.scanning = is_scanning
        self.scan_status_changed.emit(is_scanning)
        self.update()  # Redraw to update border color
        
    def initUI(self):
        # Set window flags
        self.setWindowFlags(
            Qt.FramelessWindowHint |      # No window frame
            Qt.WindowStaysOnTopHint |     # Always on top
            Qt.Tool                       # Don't show in taskbar
        )
        self.setAttribute(Qt.WA_TranslucentBackground)  # Transparent background
        self.setAutoFillBackground(False)  # Disable auto background filling
        
        # Set window properties
        self.setWindowTitle('English Text Detector')
        self.setGeometry(100, 100, 600, 400)
        
        # Emit initial size
        self.size_changed.emit(self.width(), self.height())
        
        # Show the window
        self.show()
    
    def set_new_size(self, width, height):
        # Resize the window while maintaining position
        self.resize(width, height)
    
    def resizeEvent(self, event):
        # When resized, emit the new size
        self.size_changed.emit(self.width(), self.height())
        super().resizeEvent(event)
    
    def paintEvent(self, event):
        # Draw only a red border, nothing else
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set pen for the border
        pen = QPen(Qt.red if self.scanning else Qt.gray)
        pen.setWidth(self.border_width)
        painter.setPen(pen)
        
        # Draw the border rectangle
        painter.drawRect(self.rect().adjusted(
            self.border_width//2, 
            self.border_width//2, 
            -self.border_width//2, 
            -self.border_width//2))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def keyPressEvent(self, event):
        # Alt+P to toggle scanning
        if event.key() == Qt.Key_P and event.modifiers() == Qt.AltModifier:
            self.scanning = not self.scanning
            print(f"Scanning: {'Active' if self.scanning else 'Paused'}")
            self.scan_status_changed.emit(self.scanning)
            self.update()  # Redraw to update border color
        # Close application with Escape key
        elif event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
    
    def detect_text(self):
        if not TESSERACT_AVAILABLE or not self.scanning:
            return
            
        try:
            # Get global position of the window
            window_pos = self.mapToGlobal(self.rect().topLeft())
            
            # Calculate the position for capture (inside the border)
            x = window_pos.x() + self.border_width * 2
            y = window_pos.y() + self.border_width * 2
            width = self.width() - self.border_width * 4
            height = self.height() - self.border_width * 4
            
            # Debug info
            print(f"Capturing area: x={x}, y={y}, width={width}, height={height}")
            
            # Capture the screen area
            screenshot = ImageGrab.grab(bbox=(x, y, x+width, y+height))
            
            # For debugging: save the screenshot to see what's being captured
            # screenshot.save("capture_debug.png")
            
            # Use Tesseract to detect text (English by default)
            text = pytesseract.image_to_string(screenshot)
            
            # Log detected text to terminal (if any)
            if text.strip():
                print("Detected text:")
                print(text.strip())
                print("-------------------")
                
                # Only update if the text is different from the last detection
                if text.strip() != self.last_detected_text:
                    self.last_detected_text = text.strip()
                    self.text_detected.emit(self.last_detected_text)
        except Exception as e:
            print(f"Error detecting text: {e}")
            import traceback
            traceback.print_exc()

def main():
    app = QApplication(sys.argv)
    
    # Create the result window first
    result_window = ResultWindow()
    
    # Create the transparent window and pass the result window
    window = TrulyTransparentWindow(result_window)
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 