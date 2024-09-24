import tkinter as tk
from tkinter import messagebox
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

# Fungsi untuk mendekripsi data AES-256
def decrypt_AES256(enc_data, key):
    try:
        # Padding kunci agar tepat 32 karakter
        key = key.ljust(32)[:32].encode('utf-8')
        iv, ct = enc_data.split(':')  # Pastikan ada dua bagian yang dipisahkan oleh ":"
        iv = base64.b64decode(iv)  # Decode IV dari base64
        ct = base64.b64decode(ct)  # Decode ciphertext dari base64
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode('utf-8')  # Mengembalikan plaintext
    except ValueError as e:
        return f"Error: {str(e)}"  # Kesalahan padding atau kunci yang salah
    except Exception as e:
        return f"Error: {str(e)}"

# Fungsi untuk membaca dan mendekripsi file
def decrypt_file():
    key = entry_key.get()  # Mendapatkan kunci dari input pengguna
    if len(key) != 32:
        messagebox.showerror("Error", "Kunci harus 32 karakter untuk AES-256")
        return

    # Set path langsung ke "Attendance.csv"
    file_path = 'Attendance.csv'
    
    try:
        with open(file_path, 'r') as file:
            data = file.readlines()

        decrypted_data = []
        for line in data:
            encrypted_part = line.strip()  # Ambil seluruh baris terenkripsi
            decrypted_line = decrypt_AES256(encrypted_part, key)
            decrypted_data.append(decrypted_line)

        result_text.delete(1.0, tk.END)  # Clear previous results
        result_text.insert(tk.END, "\n".join(decrypted_data))

    except Exception as e:
        messagebox.showerror("Error", f"Gagal membuka file: {str(e)}")

# Setup UI menggunakan tkinter
root = tk.Tk()
root.title("Dekripsi Absensi")

# Label dan input kunci AES-256
label_key = tk.Label(root, text="Masukkan Kunci AES-256 (32 karakter):")
label_key.pack(pady=10)

entry_key = tk.Entry(root, width=50, show="*")
entry_key.pack(pady=5)

# Tombol untuk mendekripsi file
decrypt_button = tk.Button(root, text="Dekripsi File", command=decrypt_file)
decrypt_button.pack(pady=20)

# Area teks untuk menampilkan hasil dekripsi
result_text = tk.Text(root, height=20, width=80)
result_text.pack(pady=10)

root.mainloop()
