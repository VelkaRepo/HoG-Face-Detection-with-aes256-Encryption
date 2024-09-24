from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, QTimer, QDate
from PyQt5.QtWidgets import QDialog, QMessageBox
import cv2
import face_recognition
import numpy as np
import datetime
import os
import csv
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64

# Fungsi untuk enkripsi AES-256
def encrypt_AES256(data, key):
    key = key.ljust(32)[:32].encode('utf-8')
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    return f"{iv}:{ct}"

# Fungsi untuk dekripsi AES-256
def decrypt_AES256(enc_data, key):
    key = key.ljust(32)[:32].encode('utf-8')
    iv, ct = enc_data.split(':')
    iv = base64.b64decode(iv)
    ct = base64.b64decode(ct)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode('utf-8')


class Ui_OutputDialog(QDialog):
    def __init__(self):
        super(Ui_OutputDialog, self).__init__()
        loadUi("./outputwindow.ui", self)

        now = QDate.currentDate()
        current_date = now.toString('ddd dd MMMM yyyy')
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        self.Date_Label.setText(current_date)
        self.Time_Label.setText(current_time)

        self.image = None

    @pyqtSlot()
    def startVideo(self, camera_name):
        if len(camera_name) == 1:
            self.capture = cv2.VideoCapture(int(camera_name))
        else:
            self.capture = cv2.VideoCapture(camera_name)
        self.timer = QTimer(self)
        path = 'ImagesAttendance'
        if not os.path.exists(path):
            os.mkdir(path)
        images = []
        self.class_names = []
        self.encode_list = []
        self.TimeList1 = []
        self.TimeList2 = []
        attendance_list = os.listdir(path)

        for cl in attendance_list:
            cur_img = cv2.imread(f'{path}/{cl}')
            images.append(cur_img)
            self.class_names.append(os.path.splitext(cl)[0])
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(img)
            encodes_cur_frame = face_recognition.face_encodings(img, boxes)[0]
            self.encode_list.append(encodes_cur_frame)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)

    def face_rec_(self, frame, encode_list_known, class_names):
        secret_key = "d4f7g8h9k0l1m2n3p4q5r6s7t8u9v0w1"  # Ganti dengan kunci rahasia Anda

        def mark_attendance(name):
            if self.ClockInButton.isChecked():
                self.ClockInButton.setEnabled(False)
                with open('Attendance.csv', 'a') as f:
                    if name != 'unknown':
                        buttonReply = QMessageBox.question(self, 'Welcome ' + name, 'Are you Clocking In?',
                                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                        if buttonReply == QMessageBox.Yes:
                            date_time_string = datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
                            data_to_encrypt = f"{name},{date_time_string},Clock In"
                            encrypted_data = encrypt_AES256(data_to_encrypt, secret_key)
                            f.writelines(f'{encrypted_data}\n')

                            self.ClockInButton.setChecked(False)
                            self.NameLabel.setText(name)
                            self.StatusLabel.setText('Clocked In')
                            self.HoursLabel.setText('Measuring')
                            self.MinLabel.setText('')

                            self.Time1 = datetime.datetime.now()
                            self.ClockInButton.setEnabled(True)
                        else:
                            self.ClockInButton.setEnabled(True)
            elif self.ClockOutButton.isChecked():
                self.ClockOutButton.setEnabled(False)
                with open('Attendance.csv', 'a') as f:
                    if name != 'unknown':
                        buttonReply = QMessageBox.question(self, 'Cheers ' + name, 'Are you Clocking Out?',
                                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                        if buttonReply == QMessageBox.Yes:
                            date_time_string = datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
                            data_to_encrypt = f"{name},{date_time_string},Clock Out"
                            encrypted_data = encrypt_AES256(data_to_encrypt, secret_key)
                            f.writelines(f'{encrypted_data}\n')

                            self.ClockOutButton.setChecked(False)
                            self.NameLabel.setText(name)
                            self.StatusLabel.setText('Clocked Out')
                            self.Time2 = datetime.datetime.now()

                            self.ElapseList(name)
                            self.TimeList2.append(datetime.datetime.now())
                            CheckInTime = self.TimeList1[-1]
                            CheckOutTime = self.TimeList2[-1]
                            self.ElapseHours = (CheckOutTime - CheckInTime)
                            self.MinLabel.setText("{:.0f}".format(abs(self.ElapseHours.total_seconds() / 60) % 60) + 'm')
                            self.HoursLabel.setText("{:.0f}".format(abs(self.ElapseHours.total_seconds() / 60 ** 2)) + 'h')
                            self.ClockOutButton.setEnabled(True)
                        else:
                            self.ClockOutButton.setEnabled(True)

        faces_cur_frame = face_recognition.face_locations(frame)
        encodes_cur_frame = face_recognition.face_encodings(frame, faces_cur_frame)

        for encodeFace, faceLoc in zip(encodes_cur_frame, faces_cur_frame):
            match = face_recognition.compare_faces(encode_list_known, encodeFace, tolerance=0.50)
            face_dis = face_recognition.face_distance(encode_list_known, encodeFace)
            name = "unknown"
            best_match_index = np.argmin(face_dis)
            if match[best_match_index]:
                name = class_names[best_match_index].upper()
                y1, x2, y2, x1 = faceLoc
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(frame, (x1, y2 - 20), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            mark_attendance(name)

        return frame

    def ElapseList(self, name):
        secret_key = "d4f7g8h9k0l1m2n3p4q5r6s7t8u9v0w1"
        
        with open('Attendance.csv', "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                decrypted_row = decrypt_AES256(','.join(row), secret_key).split(',')
                if decrypted_row[0] == name:
                    if decrypted_row[2] == 'Clock In':
                        Time1 = datetime.datetime.strptime(decrypted_row[1], '%y/%m/%d %H:%M:%S')
                        self.TimeList1.append(Time1)
                    elif decrypted_row[2] == 'Clock Out':
                        Time2 = datetime.datetime.strptime(decrypted_row[1], '%y/%m/%d %H:%M:%S')
                        self.TimeList2.append(Time2)

    def update_frame(self):
        ret, self.image = self.capture.read()
        self.displayImage(self.image, self.encode_list, self.class_names, 1)

    def displayImage(self, image, encode_list, class_names, window=1):
        image = cv2.resize(image, (640, 480))
        try:
            image = self.face_rec_(image, encode_list, class_names)
        except Exception as e:
            print(e)
        qformat = QImage.Format_Indexed8
        if len(image.shape) == 3:
            if image.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        outImage = QImage(image, image.shape[1], image.shape[0], image.strides[0], qformat)
        outImage = outImage.rgbSwapped()

        if window == 1:
            self.imgLabel.setPixmap(QPixmap.fromImage(outImage))
            self.imgLabel.setScaledContents(True)