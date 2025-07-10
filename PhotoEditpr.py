
import tkinter
import customtkinter as ctk
import numpy as np
import os
import matplotlib.pyplot as plt
from PIL import Image
import tkinter.filedialog
import cv2
import sys

current_image_pil = None
current_image_array = None
original_file_name = None

history_stack=[]
redo_stack=[]

original_loaded_image_pil=None





def push_history():
    if current_image_pil is not None:
        history_stack.append(current_image_pil.copy())
        redo_stack.clear()


def undo_action():
    global current_image_pil, current_image_array
    if history_stack:
        redo_stack.append(current_image_pil.copy())
        current_image_pil=history_stack.pop()
        current_image_array=np.array(current_image_pil)
        show_image(current_image_array, title="Undo", cmap='gray' if current_image_array.ndim==2 else None)
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
        show_image(current_image_array, title="Redo", cmap="gray" if current_image_array.ndim == 2 else None)
        print("Redo applied.")
        update_revert_state()
    else:
        print("Nothing to redo.")


#text for GUI
class TextGenerator(object):
    def __init__(self,widget):
        self.widget=widget
    
    def write(self,str_to_write):
        self.widget.insert(tkinter.END, str_to_write)
        self.widget.see(tkinter.END)
    
    def flush(self):
        pass

#grayscale photo
def colortogray(photo_array):
    if photo_array.ndim == 3 and photo_array.shape[2] >= 3: #only if its a color photo with at least 3 channels
        # Using your exact colortogray as provided
        return np.dot(photo_array[..., :3], [0.2989, 0.5870, 0.1140])
    else:
        print("Image is grayscale or has fewer than 3 channels. Skipping grayscale")
        return photo_array

#blurred photo
def blur_photo(photo_array, kernel_size):
    # kernel = np.ones((kernel_size, kernel_size)) / (kernel_size * kernel_size)
    # h, w = photo_array.shape[:2]
    # padding = kernel_size // 2
    # padded_image = np.pad(photo_array, [(padding, padding), (padding, padding), (0, 0)], mode='constant', constant_values=0)
    # blurred_photo = np.zeros_like(photo_array)

    # for i in range(h):
    #     for j in range(w):
    #         for c in range(3):
    #             blurred_photo[i, j, c] = np.sum(padded_image[i:i+kernel_size, j:j+kernel_size, c] * kernel)
    
    # return blurred_photo.astype(np.uint8)

    if kernel_size <= 0:
        print("Blur strength must be a positive integer. Using 5 as default.")
        kernel_size = 5
    if kernel_size % 2 == 0:
        kernel_size += 1
        print(f"Adjusted blur strength to {kernel_size} (odd is better blurring)")
    return cv2.blur(photo_array.astype(np.uint8), (kernel_size, kernel_size))


#revert function
def update_revert_state():
    if original_loaded_image_pil is not None:
        revert_button.configure(state="normal")
    else:
        revert_button.configure(state="disabled")


def revert_action():
    global current_image_pil, current_image_array
    if original_loaded_image_pil is not None:
        current_image_pil=original_loaded_image_pil.copy()
        current_image_array=np.array(current_image_pil)

        cmap="gray" if current_image_array.ndim==2 or current_image_pil.mode=="L" else None
        show_image(current_image_array, title="Reverted to Original", cmap= cmap)
        print ("Reverted to Original")
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

            original_loaded_image_pil=photo_pil.copy()
            current_image_pil = photo_pil
            current_image_array = np.array(photo_pil)

            rotate_frame.pack(pady=10, anchor="n")
            filters_frame.pack(pady=10, anchor="n")
            history_frame.pack(pady=10, anchor="n")
            save_button.pack(pady=10, anchor="n")

            
            print (f"Loaded Image: {original_file_name}")
            show_image(current_image_array, title="Original Image", cmap=None)
            update_revert_state()
        except Exception as e:
            print(f"Error Opening Image:{e}")
            current_image_pil = None
            current_image_array = None
            original_file_name = None
            original_loaded_image_pil=None
            update_revert_state()

    else:
        print ("No file Selected")

def on_close(event):
    pass

def show_image(image_array, title="Photo Editor", cmap=None):
    plt.imshow(image_array, cmap=cmap)
    plt.axis('off')
    fig = plt.gcf()
    fig.canvas.manager.set_window_title(title)
    fig.canvas.mpl_connect("close_event", on_close)
    plt.show()

def rotate_left():
    global current_image_pil, current_image_array
    if current_image_pil:
        push_history()
        rotated_image_pil = current_image_pil.rotate(90, expand=True)
        current_image_pil = rotated_image_pil
        current_image_array = np.array(rotated_image_pil)

        # check dimension to decide cmap
        if current_image_array.ndim == 2:
            show_image(current_image_array, title="Rotated Left", cmap='gray')
            print("Image rotated left.")
        else:
            show_image(current_image_array, title="Rotated Left", cmap=None)
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


        if current_image_array.ndim == 2:
            show_image(current_image_array, title="Rotated Right", cmap='gray')
            print("Image rotated right.")
        else:
            show_image(current_image_array, title="Rotated Right", cmap=None)
            print("Image rotated right.")
        
        update_revert_state()
        
    else:
        print("No image loaded to rotate.")

def apply_grayscale():
    global current_image_pil, current_image_array
    if current_image_array is not None:
        push_history()
        processed_array = colortogray(current_image_array)

        # making sure that image is correctly grayscale
        # unit8 is needed for Image.fromarray to handle it correctly and displayed with cmap="gray" for matplotlib
        if processed_array.ndim == 2:
            current_image_pil = Image.fromarray(processed_array.astype(np.uint8), mode="L")
        else:
            current_image_pil = Image.fromarray(processed_array.astype(np.uint8))

        current_image_array = processed_array.astype(np.uint8)
        show_image(current_image_array, title="Grayscale Image", cmap='gray')
        print("Grayscale filter applied.")
        update_revert_state()

    else:
        print("No image to grayscale.")

def apply_blur():
    global current_image_pil, current_image_array
    if current_image_array is not None:
        blur_dialog = ctk.CTkInputDialog(text="Enter Blur Strength (3-15 for a good blur):", title="Blur Strength")

        try:
            blur_strength_str = blur_dialog.get_input()
            if blur_strength_str is None:
                print ("Blur Cancelled")
                return
            blur_strength = int(blur_strength_str)
        except ValueError:
            print("Invalid blur strength. Using default 5")
            blur_strength = 5
        
        print("Applied Blur")
        push_history()
        processed_array = blur_photo(current_image_array, blur_strength)

        #convert processed_array to unit8
        display_array = processed_array.astype(np.uint8)
        current_image_pil = Image.fromarray(display_array)
        current_image_array = display_array 

        if current_image_array.ndim == 2:
            show_image(current_image_array, title=f"Blurred Image (Strength: {blur_strength})", cmap='gray')
        else:
            show_image(current_image_array, title=f"Blurred Image (Strength: {blur_strength})", cmap=None)
        
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
                print(f"error saving file: {e}")
    else:
        print("No Image to save")

#GUI setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("Photo Editor")
app.geometry("720x480+1000+50")

custom_font1 = ctk.CTkFont(family='KG Blank Space Sketch', size=20)
custom_font2 = ctk.CTkFont(family='KG Blank Space Sketch', size=10)

title = ctk.CTkLabel(app, text="Simple Photo Editor", font=custom_font1)
title.pack(pady=10)



browse_button = ctk.CTkButton(app, text="Browse Image", command=browse_file, font=custom_font2)
browse_button.pack(pady=10)



rotate_frame = ctk.CTkFrame(app)
rotate_frame.pack_forget()

rotate_left_button = ctk.CTkButton(rotate_frame, text="Rotate Left", command=rotate_left, font=custom_font2)
rotate_left_button.pack(side="left", padx=5)

rotate_right_button = ctk.CTkButton(rotate_frame, text="Rotate Right", command=rotate_right, font=custom_font2)
rotate_right_button.pack(side="left", padx=5)



filters_frame = ctk.CTkFrame(app)
filters_frame.pack_forget()

grayscale_button = ctk.CTkButton(filters_frame, text="Grayscale", command=apply_grayscale, font=custom_font2)
grayscale_button.pack(side="left",padx=5)

blur_button = ctk.CTkButton(filters_frame, text="Apply Blur", command=apply_blur, font=custom_font2)
blur_button.pack(side="left", padx=5)



save_button = ctk.CTkButton(app, text="Save", command=save_file, font=custom_font2)
save_button.pack_forget()



history_frame = ctk.CTkFrame(app)
history_frame.pack_forget()


undo_redo_frame = ctk.CTkFrame(history_frame)
undo_redo_frame.pack(pady=5)



undo_button = ctk.CTkButton(undo_redo_frame, text="Undo", command=undo_action, font=custom_font2, fg_color="gray", hover_color="darkgray")
undo_button.pack(side="left", padx=5)

redo_button = ctk.CTkButton(undo_redo_frame, text="Redo", command=redo_action, font=custom_font2, fg_color="gray", hover_color="darkgray")
redo_button.pack(side="left", padx=5)




revert_button = ctk.CTkButton(history_frame, text="Revert to Original", command=revert_action, font=custom_font2, fg_color="#c0392b", hover_color="#a93226", state="disabled")
revert_button.pack(pady=5)


output_textbox = ctk.CTkTextbox(app, height=100, width=app.winfo_width() - 40, font=custom_font2)
output_textbox.pack(pady=10, padx=20, fill="x", expand=True)


sys.stdout = TextGenerator(output_textbox)

update_revert_state()

app.mainloop()