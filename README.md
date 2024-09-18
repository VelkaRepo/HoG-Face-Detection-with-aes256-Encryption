
# HoG Face Detection with AES-256 Encryption

This project demonstrates a face recognition system using Histogram of Oriented Gradients (HoG) for face detection, combined with AES-256 encryption to secure the recognized face data. It is implemented in Python 3.10.0 and utilizes the DLIB library for face detection.

## Features
- **HoG Face Recognition**: Detects faces using the Histogram of Oriented Gradients method.
- **AES-256 Encryption**: Encrypts the detected face data to enhance security.
  
## Prerequisites
Before running this project, ensure you have Python 3.10.0 installed on your machine. Additionally, the DLIB library must be installed specifically for your Python version.

### Step-by-Step Installation Guide

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/VelkaRepo/HoG-Face-Detection-with-aes256-Encryption.git
   cd HoG-Face-Detection-with-aes256-Encryption
   ```

2. **Install DLIB**:
   DLIB is required for face recognition functionality. Install DLIB according to your Python version before proceeding. Here's how to install it:
   
   - For Python 3.10.0 on Windows:
     ```bash
     pip install dlib
     ```
   
   - For Python 3.10.0 on macOS or Linux:
     Make sure you have CMake installed, then run:
     ```bash
     pip install dlib
     ```
   
   Refer to the official [DLIB installation guide](http://dlib.net/compile.html) for additional instructions if you encounter issues.

3. **Install Dependencies**:
   After installing DLIB, install the remaining dependencies from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Project**:
   Once all dependencies are installed, you can run the main script for face recognition and AES-256 encryption:
   ```bash
   python mainwindow.py
   ```


## Explanation
This project uses the Histogram of Oriented Gradients (HoG) to detect faces in images. Once the face is detected, it can be encrypted using the AES-256 encryption method for secure storage or transmission. HoG is an efficient feature descriptor that captures edge information, while AES-256 is a symmetric encryption algorithm that provides high-level security for sensitive data.
