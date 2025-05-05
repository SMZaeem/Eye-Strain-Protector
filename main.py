from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QLCDNumber, QGraphicsView # Import QMainWindow and QGraphicsView
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer
import cv2
import time
from plyer import notification
import os

class EyeTrackingApp(QMainWindow):  # Inherit from QMainWindow
    def __init__(self):
        super().__init__()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(script_dir, 'Eye strain protector design.ui')
        uic.loadUi(ui_path, self)

        # Now you can access your widgets using their object names
        self.graphicsView = self.findChild(QGraphicsView, 'graphicsView') # Use QGraphicsView
        self.thresholdTimeLCD = self.findChild(QLCDNumber, 'thresholdTimeLCD')
        self.increaseThresholdButton = self.findChild(QPushButton, 'increaseThresholdButton')
        self.decreaseThresholdButton = self.findChild(QPushButton, 'decreaseThresholdButton')
        self.currentTimeLCD = self.findChild(QLCDNumber, 'currentTimeLCD')
        self.label = self.findChild(QLabel, 'label') # You have a QLabel named 'label' as well

        self.cap = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

        self.staring_time = 0
        self.start_time = time.time()
        self.threshold = 15
        self.thresholdTimeLCD.display(self.threshold)
        self.is_looking = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.increaseThresholdButton.clicked.connect(self.increase_threshold)
        self.decreaseThresholdButton.clicked.connect(self.decrease_threshold)

    def increase_threshold(self):
        self.threshold += 5
        self.thresholdTimeLCD.display(self.threshold)

    def decrease_threshold(self):
        if self.threshold > 5:
            self.threshold -= 5
            self.thresholdTimeLCD.display(self.threshold)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            eyes_detected = False
            for (x, y, w, h) in faces:
                roi_gray = gray[y:y + h, x:x + w]
                eyes = self.eye_cascade.detectMultiScale(roi_gray)
                if len(eyes) > 0:
                    eyes_detected = True
                    break

            if eyes_detected:
                if not self.is_looking:
                    self.is_looking = True
                    self.start_time = time.time()
                self.staring_time = time.time() - self.start_time
                self.currentTimeLCD.display(int(self.staring_time))
                if self.staring_time > self.threshold:
                    self.send_notification("Take a break!", f"You've been looking at the screen for {int(self.staring_time)} seconds.")
                    self.start_time = time.time()
            else:
                self.is_looking = False
                self.staring_time = 0
                self.currentTimeLCD.display(0)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.graphicsView.setScene(QtWidgets.QGraphicsScene()) # You need to create a scene to add items to GraphicsView
            item = QtWidgets.QGraphicsPixmapItem(pixmap)
            self.graphicsView.scene().addItem(item)

    def send_notification(self, title, message):
        success = notification.notify(
            title=title,
            message=message,
            timeout=10
        )
        print(f"Notification sent successfully: {success}")

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == '__main__':
    from PyQt5 import QtWidgets # Import QtWidgets for QGraphicsScene and QGraphicsPixmapItem
    app = QApplication([])
    window = EyeTrackingApp()
    window.show()
    app.exec_()