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

# Global key untuk enkripsi dan dekripsi (pastikan 32 karakter)
secret_key = "politeknikbhaktisemesta2024sal3"

# Fungsi untuk enkripsi data menggunakan AES-256
def encrypt_AES256(data, key=secret_key):
    key = key.ljust(32)[:32].encode('utf-8')  # Panjangkan key jadi 32 karakter dan konversi ke bytes
    cipher = AES.new(key, AES.MODE_CBC)  # Gunakan mode CBC buat cipher AES
    ct_bytes = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))  # Enkripsi data yang sudah dipad
    iv = base64.b64encode(cipher.iv).decode('utf-8')  # Konversi iv jadi base64 biar bisa disimpan
    ct = base64.b64encode(ct_bytes).decode('utf-8')  # Konversi ciphertext jadi base64 juga
    return f"{iv}:{ct}"  # Format akhir: iv:ciphertext

# Fungsi untuk dekripsi data yang sudah dienkripsi dengan AES-256
def decrypt_AES256(enc_data, key=secret_key):
    key = key.ljust(32)[:32].encode('utf-8')
    iv, ct = enc_data.split(':')  # Pisahkan iv dan ciphertext
    iv = base64.b64decode(iv)  # Decode base64 iv
    ct = base64.b64decode(ct)  # Decode base64 ciphertext
    cipher = AES.new(key, AES.MODE_CBC, iv)  # Buat cipher baru dengan iv yang di-decode tadi
    pt = unpad(cipher.decrypt(ct), AES.block_size)  # Dekripsi ciphertext dan unpad hasilnya
    return pt.decode('utf-8')  # Konversi hasil dekripsi jadi string

class Ui_OutputDialog(QDialog):
    def __init__(self):
        super(Ui_OutputDialog, self).__init__()
        loadUi("./outputwindow.ui", self)  # Load UI dari file .ui

        # Set tanggal dan waktu saat ini di label
        now = QDate.currentDate()
        current_date = now.toString('ddd dd MMMM yyyy')  # Format tanggal
        current_time = datetime.datetime.now().strftime("%I:%M %p")  # Format waktu
        self.Date_Label.setText(current_date)  # Tampilkan tanggal di label
        self.Time_Label.setText(current_time)  # Tampilkan waktu di label

        self.image = None  # Variabel buat nyimpen frame video

    @pyqtSlot()
    def startVideo(self, camera_name):
        # Tentukan input video (bisa dari webcam atau IP camera)
        if len(camera_name) == 1:
            self.capture = cv2.VideoCapture(int(camera_name))  # Kalau dari webcam, pakai indeks
        else:
            self.capture = cv2.VideoCapture(camera_name)  # Kalau dari IP camera, pakai URL
        self.timer = QTimer(self)

        # Load semua gambar wajah dari folder "ImagesAttendance"
        path = 'ImagesAttendance'
        if not os.path.exists(path):
            os.mkdir(path)  # Bikin folder kalau belum ada
        images = []  # Buat nyimpen gambar
        self.class_names = []  # Buat nyimpen nama kelas (nama file)
        self.encode_list = []  # Buat nyimpen encoding wajah
        self.TimeList1 = []  # Buat nyimpen waktu Clock In
        self.TimeList2 = []  # Buat nyimpen waktu Clock Out
        attendance_list = os.listdir(path)  # Ambil daftar file di folder

        for cl in attendance_list:
            cur_img = cv2.imread(f'{path}/{cl}')  # Baca gambar
            images.append(cur_img)
            self.class_names.append(os.path.splitext(cl)[0])  # Ambil nama file (tanpa ekstensi)
        
        # Encode semua gambar wajah
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Ubah format warna ke RGB
            boxes = face_recognition.face_locations(img)  # Ambil lokasi wajah
            encodes_cur_frame = face_recognition.face_encodings(img, boxes)[0]  # Ambil encoding wajah
            self.encode_list.append(encodes_cur_frame)  # Tambah ke list

        # Mulai timer buat update frame
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)  # Update tiap 10ms

    # Fungsi utama buat deteksi dan verifikasi wajah
    def face_rec_(self, frame, encode_list_known, class_names):
        def mark_attendance(name):
            # Kalau button Clock In ditekan, tandai waktu Clock In
            if self.ClockInButton.isChecked():
                self.ClockInButton.setEnabled(False)
                with open('Attendance.csv', 'a') as f:
                    if name != 'unknown':
                        buttonReply = QMessageBox.question(self, 'Welcome ' + name, 'Are you Clocking In?',
                                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                        if buttonReply == QMessageBox.Yes:
                            date_time_string = datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
                            data_to_encrypt = f"{name},{date_time_string},Clock In"  # Format data untuk enkripsi
                            encrypted_data = encrypt_AES256(data_to_encrypt)  # Enkripsi data
                            f.writelines(f'{encrypted_data}\n')  # Simpan ke file CSV

                            self.ClockInButton.setChecked(False)
                            self.NameLabel.setText(name)  # Tampilkan nama di label
                            self.StatusLabel.setText('Clocked In')  # Tampilkan status di label
                            self.HoursLabel.setText('Measuring')  # Placeholder status
                            self.MinLabel.setText('')

                            self.Time1 = datetime.datetime.now()  # Simpan waktu Clock In
                            self.ClockInButton.setEnabled(True)
                        else:
                            self.ClockInButton.setEnabled(True)

            # Kalau button Clock Out ditekan, tandai waktu Clock Out
            elif self.ClockOutButton.isChecked():
                self.ClockOutButton.setEnabled(False)
                with open('Attendance.csv', 'a') as f:
                    if name != 'unknown':
                        buttonReply = QMessageBox.question(self, 'Cheers ' + name, 'Are you Clocking Out?',
                                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                        if buttonReply == QMessageBox.Yes:
                            date_time_string = datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
                            data_to_encrypt = f"{name},{date_time_string},Clock Out"
                            encrypted_data = encrypt_AES256(data_to_encrypt)
                            f.writelines(f'{encrypted_data}\n')

                            self.ClockOutButton.setChecked(False)
                            self.NameLabel.setText(name)
                            self.StatusLabel.setText('Clocked Out')
                            self.Time2 = datetime.datetime.now()  # Simpan waktu Clock Out

                            self.ElapseList(name)  # Hitung selisih waktu
                            self.TimeList2.append(datetime.datetime.now())  # Simpan waktu Clock Out ke list
                            CheckInTime = self.TimeList1[-1]
                            CheckOutTime = self.TimeList2[-1]
                            self.ElapseHours = (CheckOutTime - CheckInTime)  # Hitung total jam kerja
                            # Tampilkan total waktu kerja
                            self.MinLabel.setText("{:.0f}".format(abs(self.ElapseHours.total_seconds() / 60) % 60) + 'm')
                            self.HoursLabel.setText("{:.0f}".format(abs(self.ElapseHours.total_seconds() / 60 ** 2)) + 'h')
                            self.ClockOutButton.setEnabled(True)
                        else:
                            self.ClockOutButton.setEnabled(True)

        faces_cur_frame = face_recognition.face_locations(frame)  # Ambil lokasi wajah dari frame
        encodes_cur_frame = face_recognition.face_encodings(frame, faces_cur_frame)  # Ambil encoding wajah dari frame

        for encodeFace, faceLoc in zip(encodes_cur_frame, faces_cur_frame):
            match = face_recognition.compare_faces(encode_list_known, encodeFace, tolerance=0.50)
            face_dis = face_recognition.face_distance(encode_list_known, encodeFace)  # Hitung jarak wajah
            name = "unknown"
            best_match_index = np.argmin(face_dis)  # Cari kecocokan terbaik
            if match[best_match_index]:
                name = class_names[best_match_index].upper()  # Ambil nama berdasarkan kecocokan
                # Gambarkan kotak dan nama di sekitar wajah
                y1, x2, y2, x1 = faceLoc
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, name, (x1 + 6, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                mark_attendance(name)  # Tandai kehadiran
        return frame  # Return frame yang sudah di-overlay info wajah

    def update_frame(self):
        ret, self.image = self.capture.read()  # Ambil frame dari capture
        self.display_image(self.image, self.encode_list, self.class_names)

    def display_image(self, img, encode_list, class_names):
        # Resize image, convert ke format QImage, dan tampilkan di UI
        img = self.face_rec_(img, encode_list, class_names)
        qformat = QImage.Format_Indexed8

        if len(img.shape) == 3:  # Convert ke format QImage
            if img.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888

        out_image = QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)
        out_image = out_image.rgbSwapped()  # Swap RGB jadi BGR
        self.imgLabel.setPixmap(QPixmap.fromImage(out_image))  # Tampilkan di label UI
        self.imgLabel.setScaledContents(True)

    # Fungsi buat menghitung total jam kerja (misal Clock In dan Clock Out)
    def ElapseList(self, name):
    # Ubah file menjadi 'Attendance.csv' biar konsisten dengan yang lain
    with open('Attendance.csv', 'a') as f:
        nameList = []
        now = datetime.datetime.now()
        self.TimeList2.append(now)  # Tambahkan waktu sekarang ke list TimeList2
        CheckInTime = self.TimeList1[-1]  # Ambil waktu terakhir Clock In
        CheckOutTime = self.TimeList2[-1]  # Ambil waktu terakhir Clock Out
        TotalElapse = CheckOutTime - CheckInTime  # Hitung selisih waktu (total durasi kerja)
        mins = int(TotalElapse.total_seconds() / 60)  # Hitung total menit
        hours = int(mins / 60)  # Hitung total jam
        # Tulis hasil perhitungan durasi ke file 'Attendance.csv' dengan format yang konsisten
        f.writelines(f'Clocked In: {CheckInTime},Clocked Out: {CheckOutTime},Total Time: {hours}h:{mins % 60}m\n')
