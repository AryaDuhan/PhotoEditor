import tkinter
import customtkinter as ctk
import numpy as np
import os
from PIL import Image, ImageTk
import tkinter.filedialog
import cv2
import sys

current_image_pil = None
current_image_array = None
original_file_name = None

image_display_label = None

history_stack = []
redo_stack = []

original_loaded_image_pil = None


def update_Image_preview(image_pil):
    global image_display_label

    image_resized = image_pil.copy()
    image_resized.thumbnail((650, 450))

    tk_image = ImageTk.PhotoImage(image_resized)
    image_display_label.configure(image=tk_image)
    image_display_label.image = tk_image

def push_history():
    if current_image_pil is not None:
        history_stack.append(current_image_pil.copy())
        redo_stack.clear()


def undo_action():
    global current_image_pil, current_image_array
    if history_stack:
        redo_stack.append(current_image_pil.copy())
        current_image_pil = history_stack.pop()
        current_image_array = np.array(current_image_pil)
        update_Image_preview(current_image_pil)
        print("Undo Applied")
        update_revert_state()
    else:
        print("Nothing to Undo")


def redo_action():
    global current_image_pil, current_image_array
    if redo_stack:
        history_stack.append(current_image_pil.copy())
        current_image_pil = redo_stack.pop()
        current_image_array = np.array(current_image_pil)
        update_Image_preview(current_image_pil)
        print("Redo applied.")
        update_revert_state()
    else:
        print("Nothing to redo.")


#text for GUI
class TextGenerator(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, str_to_write):
        self.widget.insert(tkinter.END, str_to_write)
        self.widget.see(tkinter.END)

    def flush(self):
        pass


#grayscale photo
def colortogray(photo_array):
    if photo_array.ndim == 3 and photo_array.shape[2] >= 3:
        return np.dot(photo_array[..., :3], [0.2989, 0.5870, 0.1140])
    else:
        print("Image is grayscale or has fewer than 3 channels. Skipping grayscale")
        return photo_array


#blurred photo
def blur_photo(photo_array, kernel_size):
    if kernel_size <= 0:
        print("Blur strength must be a positive integer. Using 5 as default.")
        kernel_size = 5
    if kernel_size % 2 == 0:
        kernel_size += 1
        print(f"Adjusted blur strength to {kernel_size} (odd is better blurring)")
    return cv2.blur(photo_array.astype(np.uint8), (kernel_size, kernel_size))


#revert function
def update_revert_state():
    #undo
    if history_stack:
        undo_button.configure(state="normal")
    else:
        undo_button.configure(state="disabled")

    #redo
    if redo_stack:
        redo_button.configure(state="normal")
    else:
        redo_button.configure(state="disabled")

    #revert
    if original_loaded_image_pil is not None and current_image_pil is not None:
        if not np.array_equal(np.array(original_loaded_image_pil), np.array(current_image_pil)):
            revert_button.configure(state="normal")
        else:
            revert_button.configure(state="disabled")
    else:
        revert_button.configure(state="disabled")

def revert_action():
    global current_image_pil, current_image_array
    if original_loaded_image_pil is not None:
        current_image_pil = original_loaded_image_pil.copy()
        current_image_array = np.array(current_image_pil)
        update_Image_preview(current_image_pil)
        print("Reverted to Original")
        update_revert_state()
    else:
        print("No original image loaded to revert to.")


def browse_file():
    global current_image_pil, current_image_array, original_file_name, original_loaded_image_pil
    tempfile = tkinter.filedialog.askopenfile(title='Please select a file', filetypes=[('Image Files', '*.png;*.jpg;*.jpeg;*.gif;*.bmp')])
    if tempfile:
        original_file_name = tempfile.name
        try:
            photo_pil = Image.open(tempfile.name).convert('RGB')

            original_loaded_image_pil = photo_pil.copy()
            current_image_pil = photo_pil
            current_image_array = np.array(photo_pil)

            rotate_frame.pack(pady=10, anchor="n")
            filters_frame.pack(pady=10, anchor="n")
            history_frame.pack(pady=10, anchor="n")
            save_button.pack(pady=10, anchor="n")

            print(f"Loaded Image: {original_file_name}")
            update_Image_preview(current_image_pil)
            update_revert_state()
        except Exception as e:
            print(f"Error Opening Image: {e}")
            current_image_pil = None
            current_image_array = None
            original_file_name = None
            original_loaded_image_pil = None
            update_revert_state()
    else:
        print("No file Selected")


def rotate_left():
    global current_image_pil, current_image_array
    if current_image_pil:
        push_history()
        rotated_image_pil = current_image_pil.rotate(90, expand=True)
        current_image_pil = rotated_image_pil
        current_image_array = np.array(rotated_image_pil)
        update_Image_preview(current_image_pil)
        print("Image rotated left.")
        update_revert_state()
    else:
        print("No image loaded to rotate.")


def rotate_right():
    global current_image_pil, current_image_array
    if current_image_pil:
        push_history()
        rotated_image_pil = current_image_pil.rotate(-90, expand=True)
        current_image_pil = rotated_image_pil
        current_image_array = np.array(rotated_image_pil)
        update_Image_preview(current_image_pil)
        print("Image rotated right.")
        update_revert_state()
    else:
        print("No image loaded to rotate.")


def apply_grayscale():
    global current_image_pil, current_image_array
    if current_image_array is not None:
        push_history()
        processed_array = colortogray(current_image_array)

        if processed_array.ndim == 2:
            current_image_pil = Image.fromarray(processed_array.astype(np.uint8), mode="L")
        else:
            current_image_pil = Image.fromarray(processed_array.astype(np.uint8))

        current_image_array = processed_array.astype(np.uint8)
        update_Image_preview(current_image_pil)
        print("Grayscale filter applied.")
        update_revert_state()
    else:
        print("No image to grayscale.")


def apply_blur():
    global current_image_pil, current_image_array
    if current_image_array is not None:
        try:
            blur_strength = int(blur_strength_entry.get())
        except ValueError:
            print("Invalid blur strength. Using default 5")
            blur_strength = 5

        if blur_strength <= 0:
            print("Blur strength must be positive. Using 5.")
            blur_strength = 5

        print(f"Applied Blur with strength: {blur_strength}")
        push_history()
        processed_array = blur_photo(current_image_array, blur_strength)

        display_array = processed_array.astype(np.uint8)
        current_image_pil = Image.fromarray(display_array)
        current_image_array = display_array
        update_Image_preview(current_image_pil)
        update_revert_state()
    else:
        print("No image to apply blur.")


def save_file():
    global current_image_pil, original_file_name
    if current_image_pil and original_file_name:
        file_extension = os.path.splitext(original_file_name)[1]
        save_path = tkinter.filedialog.asksaveasfilename(
            defaultextension=file_extension,
            title="Save file as",
            filetypes=[('Image Files', f'*{file_extension}')]
        )
        if save_path:
            try:
                current_image_pil.save(save_path)
                print(f"Image saved to: {save_path}")
            except Exception as e:
                print(f"Error saving file: {e}")
    else:
        print("No Image to save")


#GUI
app = ctk.CTk()
app.title("Photo Editor")
app.geometry("1000x700")


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


main_frame = ctk.CTkFrame(app)
main_frame.pack(fill="both", expand=True)


tools_frame = ctk.CTkFrame(main_frame, width=320)
tools_frame.pack(side="left", fill="y", padx=10, pady=10)
tools_frame.pack_propagate(False)



preview_frame = ctk.CTkFrame(main_frame, width=700, height=500)
preview_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)


custom_font1 = ctk.CTkFont(family='Segoe UI Semibold', size=25, weight="bold")
custom_font2 = ctk.CTkFont(family='Segoe UI', size=15,weight="bold")
console_font = ctk.CTkFont(family='Consolas', size=11)


#tittle
title = ctk.CTkLabel(tools_frame, text="Simple Photo Editor", font=custom_font1)
title.pack(pady=5)


#browse files
browse_button = ctk.CTkButton(tools_frame, text="Browse Image", command=browse_file, font=custom_font2)
browse_button.pack(pady=10)


#frame for rotate button
rotate_frame = ctk.CTkFrame(tools_frame)
rotate_frame.pack_forget()

rotate_left_button = ctk.CTkButton(rotate_frame, text="Rotate Left", command=rotate_left, font=custom_font2)
rotate_left_button.pack(side="left", padx=5)

rotate_right_button = ctk.CTkButton(rotate_frame, text="Rotate Right", command=rotate_right, font=custom_font2)
rotate_right_button.pack(side="left", padx=5)



#frame for filter buttons
filters_frame = ctk.CTkFrame(tools_frame)
filters_frame.pack_forget()

grayscale_button = ctk.CTkButton(filters_frame, text="Grayscale", command=apply_grayscale, font=custom_font2)
grayscale_button.pack(side="top", pady=5)

blur_controls = ctk.CTkFrame(filters_frame)
blur_controls.pack(side="top", pady=5)

blur_strength_entry = ctk.CTkEntry(blur_controls, width=60, placeholder_text="Eg: 3-15")
blur_strength_entry.pack(side="left", padx=(0, 5))

blur_button = ctk.CTkButton(blur_controls, text="Apply Blur", command=apply_blur, font=custom_font2)
blur_button.pack(side="left")


#for history buttons
history_frame = ctk.CTkFrame(tools_frame)
history_frame.pack_forget()

undo_redo_frame = ctk.CTkFrame(history_frame)
undo_redo_frame.pack(pady=5)

undo_button = ctk.CTkButton(undo_redo_frame, text="Undo", command=undo_action, font=custom_font2, fg_color="gray", hover_color="darkgray", state="disabled")
undo_button.pack(side="left", padx=5)

redo_button = ctk.CTkButton(undo_redo_frame, text="Redo", command=redo_action, font=custom_font2, fg_color="gray", hover_color="darkgray", state="disabled")
redo_button.pack(side="left", padx=5)

save_button = ctk.CTkButton(tools_frame, text="Save", command=save_file, font=custom_font2)
save_button.pack(pady=10)

image_display_label = ctk.CTkLabel(preview_frame, text="")
image_display_label.pack(expand=True)

revert_button = ctk.CTkButton(history_frame, text="Revert to Original", command=revert_action, font=custom_font2, fg_color="#c0392b", hover_color="#a93226", state="disabled")
revert_button.pack(pady=5)

output_textbox = ctk.CTkTextbox(app, height=80, font=console_font)
output_textbox.pack(pady=(0, 10), padx=20, fill="x")

sys.stdout = TextGenerator(output_textbox)

update_revert_state()

app.mainloop()
