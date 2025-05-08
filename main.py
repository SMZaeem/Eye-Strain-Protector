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
        self.thresholdTimeLCD_2 = self.findChild(QLCDNumber, 'thresholdTimeLCD_2')
        self.increaseThresholdButton = self.findChild(QPushButton, 'increaseThresholdButton')
        self.decreaseThresholdButton = self.findChild(QPushButton, 'decreaseThresholdButton')
        self.increaseThresholdButton_2 = self.findChild(QPushButton, 'increaseThresholdButton_2')
        self.decreaseThresholdButton_2 = self.findChild(QPushButton, 'decreaseThresholdButton_2')
        self.currentTimeLCD = self.findChild(QLCDNumber, 'currentTimeLCD')

        self.restingTimeLCD = self.findChild(QLCDNumber, 'currentTimeLCD_2')

        self.label = self.findChild(QLabel, 'label') # You have a QLabel named 'label' as well

        self.cap = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

        self.staring_time = 0
        self.start_time = time.time()
        self.shortTermThreshold = 10  #20 mins
        self.shortTermRest = 5  #20 secs
        self.longTermThreshold = 20  #2 hrs
        self.longTermRest = 1200  #20 mins

        self.short_break_start_time = 0
        self.short_break_time = 0

        self.looking_away_start_time = 0 
        self.looking_away_duration = 0
        self.should_reset_time = True
        self.reset_staring_timer = False  # Added this line

        # Add to __init__():
        self.total_staring_time = 0
        self.start_time = None

        self.total_resting_time = 0
        self.rest_start_time = None
        self.x = 0


        # self.thresholdTimeLCD.display(self.shortTermThreshold/60)
        # self.thresholdTimeLCD_2.display(self.longTermThreshold/3600)
        self.thresholdTimeLCD.display(self.shortTermThreshold)
        self.thresholdTimeLCD_2.display(self.longTermThreshold)
        self.is_looking = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.increaseThresholdButton.clicked.connect(self.increase_threshold)
        self.decreaseThresholdButton.clicked.connect(self.decrease_threshold)
        
        self.increaseThresholdButton_2.clicked.connect(self.increase_threshold_2)
        self.decreaseThresholdButton_2.clicked.connect(self.decrease_threshold_2)

    def increase_threshold(self):
        self.shortTermThreshold += 300
        self.thresholdTimeLCD.display(self.shortTermThreshold/60)

    def decrease_threshold(self):
        if self.shortTermThreshold > 1200:
            self.shortTermThreshold -= 300
            self.thresholdTimeLCD.display(self.shortTermThreshold/60)
    
    def increase_threshold_2(self):
        self.longTermThreshold += 1800
        self.thresholdTimeLCD_2.display(self.longTermThreshold/3600)

    def decrease_threshold_2(self):
        if self.longTermThreshold > 3600:
            self.longTermThreshold -= 1800
            self.thresholdTimeLCD_2.display(self.longTermThreshold/3600)

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
                    # User just looked back
                    self.is_looking = True
                    self.looking_away_start_time = 0
                    self.looking_away_duration = 0

                    # If reset flag is True, start a new staring session
                    if self.should_reset_time:
                        self.start_time = time.time()
                        self.staring_time = 0
                        self.should_reset_time = False

                # While looking
                self.staring_time = time.time() - self.start_time
                self.currentTimeLCD.display(int(self.staring_time))
                self.restingTimeLCD.display(0)

                
                if self.staring_time > self.shortTermThreshold:
                    self.x += self.shortTermThreshold                 
                    if self.x >= self.longTermThreshold:
                        self.x=0
                        self.send_notification("Take a long break!", f"You've been looking at the screen for {int(self.staring_time)} seconds.")
                    else:
                        self.send_notification("Take a short break!", f"You've been looking at the screen for {int(self.staring_time)} seconds.")
                    self.staring_time = 0  # Reset after notification
                    self.start_time = time.time()



            else:  # Not looking
                if self.is_looking:
                    # User just looked away
                    self.is_looking = False
                    self.looking_away_start_time = time.time()

                if self.looking_away_start_time != 0:
                    self.looking_away_duration = time.time() - self.looking_away_start_time
                    self.restingTimeLCD.display(int(self.looking_away_duration))

                    if self.looking_away_duration >= self.shortTermRest:
                        # Reset staring time after resting long enough
                        self.should_reset_time = True
                        self.staring_time = 0
                        self.currentTimeLCD.display(0)
                        self.looking_away_start_time = 0
                        self.looking_away_duration = 0


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

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == '__main__':
    from PyQt5 import QtWidgets # Import QtWidgets for QGraphicsScene and QGraphicsPixmapItem
    app = QApplication([])
    window = EyeTrackingApp()
    window.show()
    app.exec_()