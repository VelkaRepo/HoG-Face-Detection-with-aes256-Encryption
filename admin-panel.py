import os
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
import subprocess

# Kunci password untuk admin
ADMIN_PASSWORD = "administrator"

# Fungsi untuk menjalankan skrip add.py (menambah Mahasiswa)
def run_add_employee():
    try:
        subprocess.run(["python", "add.py"], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Gagal menjalankan add.py: {e}")

# Fungsi untuk menjalankan skrip decrypt.py (mendekripsi attendance.csv)
def run_decrypt_file():
    try:
        subprocess.run(["python", "decrypt.py"], check=True)
        messagebox.showinfo("Sukses", "File attendance.csv berhasil didekripsi.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Gagal menjalankan decrypt.py: {e}")

# Fungsi untuk memverifikasi password admin
def verify_admin_password():
    password = simpledialog.askstring("Password", "Masukkan password admin:", show="*")
    if password == ADMIN_PASSWORD:
        messagebox.showinfo("Akses Diberikan", "Password benar! Anda dapat mengakses fungsi admin.")
        add_employee_button.config(state=NORMAL)  # Aktifkan tombol tambah Mahasiswa
        decrypt_file_button.config(state=NORMAL)  # Aktifkan tombol decrypt file
    else:
        messagebox.showerror("Akses Ditolak", "Password salah! Akses ditolak.")
        root.quit()  # Keluar dari program jika password salah

# GUI utama menggunakan Tkinter
root = Tk()
root.title("Admin Panel - Absensi Mahasiswa")
root.geometry("400x300")

# Label untuk judul
label = Label(root, text="Admin Polibest", font=("Arial", 18))
label.pack(pady=20)

# Tombol untuk menambah Mahasiswa (add.py)
add_employee_button = Button(root, text="Tambah Mahasiswa", command=run_add_employee, font=("Arial", 14), padx=20, pady=10, state=DISABLED)
add_employee_button.pack(pady=10)

# Tombol untuk mendekripsi attendance.csv (decrypt.py)
decrypt_file_button = Button(root, text="Dekripsi File Absensi", command=run_decrypt_file, font=("Arial", 14), padx=20, pady=10, state=DISABLED)
decrypt_file_button.pack(pady=10)

# Verifikasi password sebelum mengakses fitur
root.after(100, verify_admin_password)

# Menjalankan GUI
root.mainloop()
