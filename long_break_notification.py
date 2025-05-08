# from PyQt5 import uic
# from PyQt5.QtWidgets import QDialog, QPushButton, QLabel
# from PyQt5.QtCore import QTimer
# import os

# class LongBreakNotification(QDialog):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         script_dir = os.path.dirname(os.path.abspath(__file__))
#         ui_path = os.path.join(script_dir, 'Long notification design.ui')
#         uic.loadUi(ui_path, self)

#         self.messageLabel = self.findChild(QLabel, 'messageLabel')
#         self.remindLaterButton = self.findChild(QPushButton, 'remindLaterButton')
#         self.closeButton = self.findChild(QPushButton, 'closeButton')

#         self.reminder_timer = QTimer() # Timer within the notification (optional)
#         self.reminder_timer.timeout.connect(self.close)

#         if self.remindLaterButton:
#             self.remindLaterButton.clicked.connect(self.remind_later)
#         if self.closeButton:
#             self.closeButton.clicked.connect(self.close)

#         self.reminder_callback = None # To be set by the main app

#     def set_message(self, message):
#         if self.messageLabel:
#             self.messageLabel.setText(message)

#     def set_remind_callback(self, callback):
#         self.reminder_callback = callback

#     def remind_later(self):
#         print("Remind later clicked!")
#         if self.reminder_callback:
#             self.reminder_callback()
#         self.accept()

#     def close(self):
#         self.reject()

from PyQt5.QtWidgets import QDialog
from notification_dialog import Ui_Dialog

class NotificationDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None, message="", icon=None):
        super().__init__(parent)
        self.setupUi(self)
        self.messageLabel.setText(message)
        # if icon:
            # self.icon_label.setPixmap(icon) # Assuming icon is a QPixmap
        self.closeButton.clicked.connect(self.accept)
        self.remindLaterButton.clicked.connect(self.reject)