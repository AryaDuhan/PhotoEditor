# 🖼️ Simple Photo Editor (Python + CustomTkinter)

A lightweight yet powerful **desktop photo editor** built with Python’s `Tkinter`, `CustomTkinter`, `Pillow`, and `OpenCV`.  
It features real-time image adjustments like **brightness**, **sharpness**, **contrast**, **saturation**, and **temperature**, plus **blur**, **grayscale**, **undo/redo**, and more — all packed into a clean, user-friendly interface.

---

## 🚀 Features

### 🎛️ Real-Time Image Adjustments
- **Brightness**
- **Contrast**
- **Saturation**
- **Sharpness**
- **Temperature** (Warm/Cool tone)

### 🧩 Filters & Effects
- **Grayscale**
- **Blur** (customizable intensity)

### 🔄 Image Tools
- **Rotate Left / Right**
- **Undo & Redo**
- **Revert to Original**
- **Reset All Adjustments**
- **Save Edited Image**

### 🖥️ Smart Preview Panel
- Scales images to fit a fixed display area
- Real-time preview on slider change

### 🧠 Intelligent Design
- Stack-based **undo/redo history**
- Output console embedded in GUI for logs
- Modular design for easy extensibility

---

## ✨ Planned Features
- ✂️ **Crop Tool** (drag-to-select cropping)
- 🪄 **Auto-Enhance** (balance lighting/colors automatically)
- 🧠 **Upscale/Enhance Resolution** (with AI image scaling)
- 🎨 **Upload Custom Filter Image** (transfer tone/color grading)
- 🔁 **Batch Editing Support**

---

## 🛠 Tech Stack

- Python 3.8+
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- Pillow (PIL Fork)
- NumPy
- OpenCV

---

## 📦 Installation

```bash
git clone https://github.com/your-username/photo-editor.git
cd photo-editor
pip install -r requirements.txt
# or individually:
pip install customtkinter pillow numpy opencv-python
python main.py
