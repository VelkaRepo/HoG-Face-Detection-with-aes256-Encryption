import cv2
import os
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog

# Buat folder ImagesAttendance jika belum ada
if not os.path.exists('ImagesAttendance'):
    os.makedirs('ImagesAttendance')

# Fungsi untuk mengambil gambar
def take_picture():
    name = simpledialog.askstring("Input", "Masukkan nama untuk file foto:")
    
    if not name:
        messagebox.showerror("Error", "Nama file tidak boleh kosong!")
        return
    
    # Nama file foto yang akan disimpan
    filename = f"ImagesAttendance/{name}.jpg"
    
    # Buka kamera (gunakan 0 untuk kamera default)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        messagebox.showerror("Error", "Tidak dapat mengakses kamera!")
        return
    
    messagebox.showinfo("Instruksi", "Tekan 'q' pada jendela kamera untuk mengambil gambar.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Gagal membaca frame dari kamera.")
            break
        
        cv2.imshow("Tekan 'q' untuk mengambil gambar", frame)
        
        # Tekan 'q' untuk mengambil gambar dan keluar
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.imwrite(filename, frame)
            messagebox.showinfo("Sukses", f"Gambar berhasil disimpan sebagai {filename}")
            break

    cap.release()
    cv2.destroyAllWindows()

# GUI utama menggunakan Tkinter
root = Tk()
root.title("Absensi Wajah - Ambil Gambar")
root.geometry("400x200")

# Tombol untuk mengambil gambar
take_picture_button = Button(root, text="Ambil Gambar", command=take_picture, font=("Arial", 14), padx=20, pady=10)
take_picture_button.pack(pady=50)

# Menjalankan GUI
root.mainloop()
