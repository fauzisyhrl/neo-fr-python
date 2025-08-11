import tkinter as tk
from tkinter import Label, Button, Entry, Text, Frame
import cv2
from PIL import Image, ImageTk
import requests
import base64
import uuid
import json

# ==== KONFIGURASI DASAR ====
API_URL = "https://fr.neoapi.id/risetai/face-api/facegallery"

# ==== UTILITY FUNCTIONS ====
def generate_trx_id():
    return str(uuid.uuid4()).replace('-', '')[:20]

def to_base64(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer).decode('utf-8')

def get_headers():
    token = token_entry.get()
    return {
        "Accesstoken": token,
        "Content-Type": "application/json"
    }

# ==== API CALL FUNCTIONS ====
def create_gallery(gallery_id):
    data = {"facegallery_id": gallery_id, "trx_id": generate_trx_id()}
    return requests.post(f"{API_URL}/create-facegallery", headers=get_headers(), json=data).json()

def list_galleries():
    return requests.get(f"{API_URL}/my-facegalleries", headers=get_headers()).json()

def delete_gallery(gallery_id):
    data = {"facegallery_id": gallery_id, "trx_id": generate_trx_id()}
    return requests.delete(f"{API_URL}/delete-facegallery", headers=get_headers(), json=data).json()

def enroll_face(image_base64, subject_id, subject_name, gallery_id):
    data = {
        "user_id": subject_id,
        "user_name": subject_name,
        "facegallery_id": gallery_id,
        "image": image_base64,
        "trx_id": generate_trx_id()
    }
    return requests.post(f"{API_URL}/enroll-face", headers=get_headers(), json=data).json()

def list_faces(gallery_id):
    url = f"{API_URL}/list-faces"
    headers = get_headers()
    data = {
        "facegallery_id": gallery_id,
        "trx_id": generate_trx_id()
    }
    return requests.request("GET", url, headers=headers, data=json.dumps(data)).json()



def verify_face(image_base64, subject_id, gallery_id):
    data = {
        "user_id": subject_id,
        "facegallery_id": gallery_id,
        "image": image_base64,
        "trx_id": generate_trx_id()
    }
    return requests.post(f"{API_URL}/verify-face", headers=get_headers(), json=data).json()

def identify_face(image_base64, gallery_id):
    data = {
        "facegallery_id": gallery_id,
        "image": image_base64,
        "trx_id": generate_trx_id()
    }
    return requests.post(f"{API_URL}/identify-face", headers=get_headers(), json=data).json()

def delete_face(subject_id, gallery_id):
    data = {
        "user_id": subject_id,
        "facegallery_id": gallery_id,
        "trx_id": generate_trx_id()
    }
    return requests.delete(f"{API_URL}/delete-face", headers=get_headers(), json=data).json()

# ==== GUI SETUP ====
window = tk.Tk()
window.title("Face Recognition GUI")

main_frame = Frame(window)
main_frame.pack(fill="both", expand=True)

# Left: Webcam
left_frame = Frame(main_frame)
left_frame.grid(row=0, column=0, padx=10, pady=10)
video_label = Label(left_frame)
video_label.pack()

# Right: Input and Controls
right_frame = Frame(main_frame)
right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

for i in range(4):
    right_frame.grid_columnconfigure(i, weight=1)

Label(right_frame, text="API Token:").grid(row=0, column=0, sticky="w", pady=2)
token_entry = Entry(right_frame, show="*")
token_entry.grid(row=0, column=1, columnspan=3, sticky="we", pady=2)

Label(right_frame, text="Gallery ID:").grid(row=1, column=0, sticky="w", pady=2)
gallery_entry = Entry(right_frame)
gallery_entry.grid(row=1, column=1, columnspan=3, sticky="we", pady=2)

Label(right_frame, text="User ID:").grid(row=2, column=0, sticky="w", pady=2)
subject_entry = Entry(right_frame)
subject_entry.grid(row=2, column=1, columnspan=3, sticky="we", pady=2)

Label(right_frame, text="User Name:").grid(row=3, column=0, sticky="w", pady=2)
name_entry = Entry(right_frame)
name_entry.grid(row=3, column=1, columnspan=3, sticky="we", pady=2)

# ==== BUTTONS FRAME ====
buttons_frame = Frame(right_frame)
buttons_frame.grid(row=4, column=0, columnspan=4, pady=10)
buttons_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

# Baris 1
Button(buttons_frame, text="📸 Enroll", command=lambda: with_frame(lambda img: enroll_face(img, subject_entry.get(), name_entry.get(), gallery_entry.get()))
).grid(row=0, column=0, padx=5, pady=5, sticky="we")

Button(buttons_frame, text="✅ Verify", command=lambda: with_frame(lambda img: verify_face(img, subject_entry.get(), gallery_entry.get()))
).grid(row=0, column=1, padx=5, pady=5, sticky="we")

Button(buttons_frame, text="🕵 Identify", command=lambda: with_frame(lambda img: identify_face(img, gallery_entry.get()))
).grid(row=0, column=2, padx=5, pady=5, sticky="we")

Button(buttons_frame, text="🗑 Delete Face", command=lambda: show_result(delete_face(subject_entry.get(), gallery_entry.get()))
).grid(row=0, column=3, padx=5, pady=5, sticky="we")

# Baris 2
Button(buttons_frame, text="📋 List Faces", command=lambda: show_result(list_faces(gallery_entry.get()))
).grid(row=1, column=0, padx=5, pady=5, sticky="we")

Button(buttons_frame, text="➕ Create Gallery", command=lambda: show_result(create_gallery(gallery_entry.get()))
).grid(row=1, column=1, padx=5, pady=5, sticky="we")

Button(buttons_frame, text="❌ Delete Gallery", command=lambda: show_result(delete_gallery(gallery_entry.get()))
).grid(row=1, column=2, padx=5, pady=5, sticky="we")

Button(buttons_frame, text="📂 List Galleries", command=lambda: show_result(list_galleries())
).grid(row=1, column=3, padx=5, pady=5, sticky="we")

# Frame pembungkus hasil
result_frame = Frame(right_frame)
result_frame.grid(row=5, column=0, columnspan=4, sticky="w", pady=(10, 5))
result_frame.grid_columnconfigure(0, weight=1)

Label(result_frame, text="🧾 Respons:").grid(row=0, column=0, sticky="w")
result_raw = Text(result_frame, height=15, width=60, bg="#e8e8e8", wrap="word")
result_raw.grid(row=1, column=0, sticky="w")


def show_result(response):
    result_raw.delete(1.0, tk.END)

    try:
        parsed = json.dumps(response, indent=2)
        result_raw.insert(tk.END, parsed)
    except Exception:
        result_raw.insert(tk.END, str(response))




# ==== WEBCAM ====
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

def update_frame():
    ret, frame = cap.read()
    if ret:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)
    video_label.after(10, update_frame)

def with_frame(func):
    if not token_entry.get():
        show_result({"message": "❗ Harap masukkan API Token terlebih dahulu."})
        return
    ret, frame = cap.read()
    if ret:
        image_base64 = to_base64(frame)
        result = func(image_base64)
        show_result(result)

# ==== TUTUP WINDOW ====
window.protocol("WM_DELETE_WINDOW", lambda: (cap.release(), window.destroy()))

update_frame()
window.mainloop()
