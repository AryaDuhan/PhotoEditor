import tkinter
import customtkinter as ctk
import numpy as np
import os
from PIL import Image, ImageTk, ImageEnhance
import tkinter.filedialog
import cv2
import sys

# Global variables
current_image_pil = None
current_image_array = None
original_file_name = None
image_display_label = None
history_stack = []
redo_stack = []
original_loaded_image_pil = None

# Dropdown state variables
transform_expanded = False
filters_expanded = False
adjustments_expanded = False

# Enhanced color scheme with gradients
COLORS = {
    'primary_dark': '#31013F',
    'primary_mid': '#4A0E5A', 
    'primary_light': '#5D1A6B',
    'accent_purple': '#800080',
    'accent_purple_dark': '#600060',
    'accent_purple_darker': '#400040',
    'accent_gold': '#FFBA00',
    'accent_gold_dark': '#E0A000',
    'accent_gold_darker': '#C88800',
    'text_light': '#FFFFFF',
    'text_secondary': '#E0E0E0'
}

def update_Image_preview(image_pil):
    global image_display_label
    image_resized = image_pil.copy()
    image_resized.thumbnail((1000, 700))
    tk_image = ctk.CTkImage(light_image=image_resized, size=image_resized.size)
    image_display_label.configure(image=tk_image, text="")
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
        log_message("✓ Undo applied", "success")
        update_ui_state()
    else:
        log_message("⚠ Nothing to undo", "warning")

def redo_action():
    global current_image_pil, current_image_array
    if redo_stack:
        history_stack.append(current_image_pil.copy())
        current_image_pil = redo_stack.pop()
        current_image_array = np.array(current_image_pil)
        update_Image_preview(current_image_pil)
        log_message("✓ Redo applied", "success")
        update_ui_state()
    else:
        log_message("⚠ Nothing to redo", "warning")

def colortogray(photo_array):
    if photo_array.ndim == 3 and photo_array.shape[2] >= 3:
        return np.dot(photo_array[..., :3], [0.2989, 0.5870, 0.1140])
    else:
        log_message("⚠ Image is already grayscale", "warning")
        return photo_array

def blur_photo(photo_array, kernel_size):
    if kernel_size <= 0:
        kernel_size = 5
    if kernel_size % 2 == 0:
        kernel_size += 1
    return cv2.blur(photo_array.astype(np.uint8), (kernel_size, kernel_size))

def log_message(message, msg_type="info"):
    status_log.configure(state="normal")
    status_log.insert(tkinter.END, f"{message}\n")
    status_log.see(tkinter.END)
    status_log.configure(state="disabled")

def update_ui_state():
    has_image = current_image_pil is not None
    has_history = len(history_stack) > 0
    has_redo = len(redo_stack) > 0
    has_changes = (original_loaded_image_pil is not None and 
                   current_image_pil is not None and 
                   not np.array_equal(np.array(original_loaded_image_pil), 
                                    np.array(current_image_pil)))
    
    # Update main action buttons
    undo_btn.configure(state="normal" if has_history else "disabled")
    redo_btn.configure(state="normal" if has_redo else "disabled")
    revert_btn.configure(state="normal" if has_changes else "disabled")
    save_btn.configure(state="normal" if has_image else "disabled")

def revert_action():
    global current_image_pil, current_image_array
    if original_loaded_image_pil is not None:
        push_history()
        current_image_pil = original_loaded_image_pil.copy()
        current_image_array = np.array(current_image_pil)
        update_Image_preview(current_image_pil)
        reset_sliders()
        log_message("✓ Reverted to original", "success")
        update_ui_state()

def browse_file():
    global current_image_pil, current_image_array, original_file_name, original_loaded_image_pil
    
    filetypes = [
        ('Image Files', '*.png *.jpg *.jpeg *.gif *.bmp *.tiff'),
        ('PNG files', '*.png'),
        ('JPEG files', '*.jpg *.jpeg'),
        ('All files', '*.*')
    ]
    
    file_path = tkinter.filedialog.askopenfilename(
        title='Select an image file',
        filetypes=filetypes
    )
    
    if file_path:
        try:
            photo_pil = Image.open(file_path).convert('RGB')
            original_loaded_image_pil = photo_pil.copy()
            current_image_pil = photo_pil
            current_image_array = np.array(photo_pil)
            original_file_name = file_path
            
            # Show image info
            width, height = photo_pil.size
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            
            update_Image_preview(current_image_pil)
            reset_sliders()
            log_message(f"✓ Loaded: {os.path.basename(file_path)} ({width}x{height}, {file_size:.1f}MB)", "success")
            update_ui_state()
            
        except Exception as e:
            log_message(f"✗ Error loading image: {str(e)}", "error")

# Transform functions
def rotate_left():
    global current_image_pil, current_image_array
    if current_image_pil:
        push_history()
        current_image_pil = current_image_pil.rotate(90, expand=True)
        current_image_array = np.array(current_image_pil)
        update_Image_preview(current_image_pil)
        log_message("✓ Rotated left 90°", "success")
        update_ui_state()

def rotate_right():
    global current_image_pil, current_image_array
    if current_image_pil:
        push_history()
        current_image_pil = current_image_pil.rotate(-90, expand=True)
        current_image_array = np.array(current_image_pil)
        update_Image_preview(current_image_pil)
        log_message("✓ Rotated right 90°", "success")
        update_ui_state()

def flip_horizontal():
    global current_image_pil, current_image_array
    if current_image_pil:
        push_history()
        current_image_pil = current_image_pil.transpose(Image.FLIP_LEFT_RIGHT)
        current_image_array = np.array(current_image_pil)
        update_Image_preview(current_image_pil)
        log_message("✓ Flipped horizontally", "success")
        update_ui_state()

def flip_vertical():
    global current_image_pil, current_image_array
    if current_image_pil:
        push_history()
        current_image_pil = current_image_pil.transpose(Image.FLIP_TOP_BOTTOM)
        current_image_array = np.array(current_image_pil)
        update_Image_preview(current_image_pil)
        log_message("✓ Flipped vertically", "success")
        update_ui_state()

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
        log_message("✓ Grayscale filter applied", "success")
        update_ui_state()

def apply_blur():
    global current_image_pil, current_image_array
    if current_image_array is not None:
        try:
            blur_strength = int(blur_entry.get() or 5)
            blur_strength = max(1, min(blur_strength, 50))
            
            push_history()
            processed_array = blur_photo(current_image_array, blur_strength)
            current_image_pil = Image.fromarray(processed_array.astype(np.uint8))
            current_image_array = processed_array
            update_Image_preview(current_image_pil)
            log_message(f"✓ Blur applied (strength: {blur_strength})", "success")
            update_ui_state()
            
        except ValueError:
            log_message("✗ Invalid blur strength value", "error")

def apply_adjustments():
    global current_image_pil, current_image_array
    
    if original_loaded_image_pil is not None:
        base_image = original_loaded_image_pil.copy()
        
        # Apply adjustments
        base_image = ImageEnhance.Brightness(base_image).enhance(brightness_var.get())
        
        # Temperature adjustment
        temp_factor = temperature_var.get()
        temp_array = np.array(base_image).astype(np.float32)
        temp_array[..., 0] *= temp_factor
        temp_array[..., 2] *= (2.0 - temp_factor)
        temp_array = np.clip(temp_array, 0, 255).astype(np.uint8)
        base_image = Image.fromarray(temp_array)
        
        base_image = ImageEnhance.Contrast(base_image).enhance(contrast_var.get())
        base_image = ImageEnhance.Sharpness(base_image).enhance(sharpness_var.get())
        base_image = ImageEnhance.Color(base_image).enhance(saturation_var.get())
        
        current_image_pil = base_image
        current_image_array = np.array(base_image)
        update_Image_preview(current_image_pil)
        update_ui_state()

def reset_sliders():
    """Reset all adjustment sliders to default values"""
    brightness_var.set(1.0)
    temperature_var.set(1.0)
    contrast_var.set(1.0)
    sharpness_var.set(1.0)
    saturation_var.set(1.0)

def save_file():
    global current_image_pil, original_file_name
    if current_image_pil and original_file_name:
        save_path = tkinter.filedialog.asksaveasfilename(
            defaultextension=".png",
            title="Save image as...",
            filetypes=[
                ('PNG files', '*.png'),
                ('JPEG files', '*.jpg'),
                ('All files', '*.*')
            ]
        )
        if save_path:
            try:
                if save_path.lower().endswith(('.jpg', '.jpeg')):
                    save_image = current_image_pil.convert('RGB')
                else:
                    save_image = current_image_pil
                    
                save_image.save(save_path, quality=95)
                log_message(f"✓ Saved: {os.path.basename(save_path)}", "success")
            except Exception as e:
                log_message(f"✗ Error saving: {str(e)}", "error")

# Dropdown toggle functions
def toggle_transform_dropdown():
    global transform_expanded
    transform_expanded = not transform_expanded
    if transform_expanded:
        transform_content.pack(fill="x", pady=(5, 0))
        transform_arrow.configure(text="▼")
    else:
        transform_content.pack_forget()
        transform_arrow.configure(text="▶")

def toggle_filters_dropdown():
    global filters_expanded
    filters_expanded = not filters_expanded
    if filters_expanded:
        filters_content.pack(fill="x", pady=(5, 0))
        filters_arrow.configure(text="▼")
    else:
        filters_content.pack_forget()
        filters_arrow.configure(text="▶")

def toggle_adjustments_dropdown():
    global adjustments_expanded
    adjustments_expanded = not adjustments_expanded
    if adjustments_expanded:
        adjustments_content.pack(fill="x", pady=(5, 0))
        adjustments_arrow.configure(text="▼")
    else:
        adjustments_content.pack_forget()
        adjustments_arrow.configure(text="▶")

# Initialize application in fullscreen
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Photo Editor Pro")
app.minsize(1200, 800)

# Configure main grid
app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(0, weight=1)

# Create main frames with enhanced gradient background
sidebar = ctk.CTkFrame(app, width=420, corner_radius=0)
sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 2))
sidebar.grid_propagate(False)

main_area = ctk.CTkFrame(app, corner_radius=0)
main_area.grid(row=0, column=1, sticky="nsew", padx=(2, 0))
main_area.grid_columnconfigure(0, weight=1)
main_area.grid_rowconfigure(0, weight=1)

# Enhanced header section with cleaner design
header_frame = ctk.CTkFrame(sidebar, height=140, fg_color="transparent", corner_radius=0)
header_frame.pack(fill="x", padx=20, pady=20)
header_frame.pack_propagate(False)

# App title with enhanced typography - bigger, bolder, no background
title_label = ctk.CTkLabel(
    header_frame, 
    text="PHOTO EDITOR", 
    font=ctk.CTkFont(family="Impact", size=42, weight="bold"),
    text_color=COLORS['text_light']
)
title_label.pack(pady=(10, 0))

pro_label = ctk.CTkLabel(
    header_frame, 
    text="P R O", 
    font=ctk.CTkFont(family="Arial Black", size=28, weight="bold"),
    text_color=COLORS['accent_gold']
)
pro_label.pack(pady=(0, 5))


# Browse button with purple gradient
browse_btn = ctk.CTkButton(
    sidebar,
    text="📁 Open Image",
    command=browse_file,
    height=55,
    font=ctk.CTkFont(size=20, weight="bold"),
    corner_radius=15,
    fg_color=COLORS['accent_purple'],
    hover_color=COLORS['accent_purple_dark'],
    border_width=2,
    border_color=COLORS['accent_purple_darker']
)
browse_btn.pack(fill="x", padx=20, pady=(0, 20))

# Create scrollable frame for tools with enhanced gradient
tools_scroll = ctk.CTkScrollableFrame(sidebar, corner_radius=15)
tools_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

# Enhanced Transform Tools Panel with better gradients
transform_panel = ctk.CTkFrame(tools_scroll, corner_radius=12, border_width=1, border_color=COLORS['primary_light'])
transform_panel.pack(fill="x", pady=(0, 15))

# Transform header with enhanced styling
transform_header = ctk.CTkFrame(transform_panel, fg_color="transparent")
transform_header.pack(fill="x", padx=15, pady=15)

transform_btn = ctk.CTkButton(
    transform_header,
    text="🔄 Transform",
    font=ctk.CTkFont(size=18, weight="bold"),
    command=toggle_transform_dropdown,
    fg_color="transparent",
    hover_color=COLORS['primary_light'],
    anchor="w",
    height=45
)
transform_btn.pack(side="left", fill="x", expand=True)

# Enhanced arrow button
transform_arrow = ctk.CTkButton(
    transform_header, 
    text="▶", 
    font=ctk.CTkFont(size=18, weight="bold"),
    width=35,
    height=35,
    corner_radius=17,
    fg_color=COLORS['accent_gold'],
    hover_color=COLORS['accent_gold_dark'],
    border_width=2,
    border_color=COLORS['accent_gold_darker'],
    command=toggle_transform_dropdown
)
transform_arrow.pack(side="right", padx=(10, 0))

# Transform content with enhanced buttons
transform_content = ctk.CTkFrame(transform_panel, fg_color="transparent")

def create_transform_button(parent, text, command):
    return ctk.CTkButton(
        parent, 
        text=text, 
        command=command, 
        height=45, 
        corner_radius=10, 
        fg_color=COLORS['accent_gold'], 
        hover_color=COLORS['accent_gold_dark'],
        border_width=2,
        border_color=COLORS['accent_gold_darker'],
        text_color="#000000",
        font=ctk.CTkFont(size=14, weight="bold")
    )

create_transform_button(transform_content, "↶ Rotate Left", rotate_left).pack(fill="x", padx=15, pady=5)
create_transform_button(transform_content, "↷ Rotate Right", rotate_right).pack(fill="x", padx=15, pady=5)
create_transform_button(transform_content, "↔ Flip Horizontal", flip_horizontal).pack(fill="x", padx=15, pady=5)
create_transform_button(transform_content, "↕ Flip Vertical", flip_vertical).pack(fill="x", padx=15, pady=(5, 15))

# Enhanced Filters Panel
filters_panel = ctk.CTkFrame(tools_scroll, corner_radius=12, border_width=1, border_color=COLORS['primary_light'])
filters_panel.pack(fill="x", pady=(0, 15))

filters_header = ctk.CTkFrame(filters_panel, fg_color="transparent")
filters_header.pack(fill="x", padx=15, pady=15)

filters_btn = ctk.CTkButton(
    filters_header,
    text="✨ Filters",
    font=ctk.CTkFont(size=18, weight="bold"),
    command=toggle_filters_dropdown,
    fg_color="transparent",
    hover_color=COLORS['primary_light'],
    anchor="w",
    height=45
)
filters_btn.pack(side="left", fill="x", expand=True)

filters_arrow = ctk.CTkButton(
    filters_header, 
    text="▶", 
    font=ctk.CTkFont(size=18, weight="bold"),
    width=35,
    height=35,
    corner_radius=17,
    fg_color=COLORS['accent_gold'],
    hover_color=COLORS['accent_gold_dark'],
    border_width=2,
    border_color=COLORS['accent_gold_darker'],
    command=toggle_filters_dropdown
)
filters_arrow.pack(side="right", padx=(10, 0))

filters_content = ctk.CTkFrame(filters_panel, fg_color="transparent")

create_transform_button(filters_content, "🎨 Grayscale", apply_grayscale).pack(fill="x", padx=15, pady=5)

# Enhanced blur controls
blur_frame = ctk.CTkFrame(filters_content, fg_color="transparent")
blur_frame.pack(fill="x", padx=15, pady=5)

blur_entry = ctk.CTkEntry(
    blur_frame, 
    placeholder_text="enter blur strength (1-50)", 
    height=45, 
    corner_radius=10,
    text_color="#000000", 
    placeholder_text_color="#A4A0A0",
    border_width=2,
    border_color=COLORS['accent_gold_darker'],
    font=ctk.CTkFont(size=13, weight="bold")
)
blur_entry.pack(fill="x", pady=(0, 10))

create_transform_button(blur_frame, "🌀 Apply Blur", apply_blur).pack(fill="x", pady=(0, 15))

# Enhanced Adjustments Panel
adjustments_panel = ctk.CTkFrame(tools_scroll, corner_radius=12, border_width=1, border_color=COLORS['primary_light'])
adjustments_panel.pack(fill="x", pady=(0, 15))

adjustments_header = ctk.CTkFrame(adjustments_panel, fg_color="transparent")
adjustments_header.pack(fill="x", padx=15, pady=15)

adjustments_btn = ctk.CTkButton(
    adjustments_header,
    text="🎚️ Adjustments",
    font=ctk.CTkFont(size=18, weight="bold"),
    command=toggle_adjustments_dropdown,
    fg_color="transparent",
    hover_color=COLORS['primary_light'],
    anchor="w",
    height=45
)
adjustments_btn.pack(side="left", fill="x", expand=True)

adjustments_arrow = ctk.CTkButton(
    adjustments_header, 
    text="▶", 
    font=ctk.CTkFont(size=18, weight="bold"),
    width=35,
    height=35,
    corner_radius=17,
    fg_color=COLORS['accent_gold'],
    hover_color=COLORS['accent_gold_dark'],
    border_width=2,
    border_color=COLORS['accent_gold_darker'],
    command=toggle_adjustments_dropdown
)
adjustments_arrow.pack(side="right", padx=(10, 0))

adjustments_content = ctk.CTkFrame(adjustments_panel, fg_color="transparent")

# Create slider variables
brightness_var = tkinter.DoubleVar(value=1.0)
temperature_var = tkinter.DoubleVar(value=1.0)
contrast_var = tkinter.DoubleVar(value=1.0)
sharpness_var = tkinter.DoubleVar(value=1.0)
saturation_var = tkinter.DoubleVar(value=1.0)

# Enhanced slider creation with gold gradients
def create_slider(parent, text, variable, min_val, max_val, emoji=""):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="x", padx=15, pady=8)
    
    label = ctk.CTkLabel(frame, text=f"{emoji} {text}", width=120, anchor="w", font=ctk.CTkFont(size=15, weight="bold"))
    label.pack(side="left")
    
    slider = ctk.CTkSlider(
        frame, 
        variable=variable,
        from_=min_val, 
        to=max_val,
        width=180,
        height=22,
        progress_color=COLORS['accent_gold'],
        button_color=COLORS['accent_gold_dark'],
        button_hover_color=COLORS['accent_gold_darker'],
        command=lambda x: apply_adjustments()
    )
    slider.pack(side="left", padx=(10, 10))
    
    value_label = ctk.CTkLabel(frame, width=60, text=f"{variable.get():.2f}", font=ctk.CTkFont(size=12, weight="bold"))
    value_label.pack(side="left")
    
    def update_label(*args):
        value_label.configure(text=f"{variable.get():.2f}")
    
    variable.trace('w', update_label)

# Create enhanced sliders
create_slider(adjustments_content, "Brightness", brightness_var, 0.0, 3.0)
create_slider(adjustments_content, "Temperature", temperature_var, 0.5, 1.5)
create_slider(adjustments_content, "Contrast", contrast_var, 0.0, 3.0)
create_slider(adjustments_content, "Sharpness", sharpness_var, 0.0, 3.0)
create_slider(adjustments_content, "Saturation", saturation_var, 0.0, 3.0)

# Enhanced reset button
reset_adj_btn = ctk.CTkButton(
    adjustments_content, 
    text="🔄 Reset All", 
    command=lambda: (push_history(), reset_sliders(), apply_adjustments()),
    fg_color=COLORS['accent_gold'],
    hover_color=COLORS['accent_gold_dark'],
    border_width=2,
    border_color=COLORS['accent_gold_darker'],
    text_color="#000000",
    height=40,
    corner_radius=10,
    font=ctk.CTkFont(size=14, weight="bold")
)
reset_adj_btn.pack(fill="x", padx=15, pady=(10, 15))

# Enhanced action buttons at bottom
action_frame = ctk.CTkFrame(sidebar, corner_radius=15, border_width=1, border_color=COLORS['primary_light'])
action_frame.pack(fill="x", padx=20, pady=(10, 20))

# History buttons row with enhanced styling
history_row = ctk.CTkFrame(action_frame, fg_color="transparent")
history_row.pack(fill="x", padx=15, pady=(15, 10))

undo_btn = ctk.CTkButton(
    history_row, text="↶ Undo", command=undo_action, 
    width=120, height=45, corner_radius=10,
    fg_color=COLORS['accent_gold'], hover_color=COLORS['accent_gold_dark'],
    border_width=2, border_color=COLORS['accent_gold_darker'], text_color="#000000",
    font=ctk.CTkFont(size=13, weight="bold")
)
undo_btn.pack(side="left", padx=(0, 5))

redo_btn = ctk.CTkButton(
    history_row, text="↷ Redo", command=redo_action, 
    width=120, height=45, corner_radius=10,
    fg_color=COLORS['accent_gold'], hover_color=COLORS['accent_gold_dark'],
    border_width=2, border_color=COLORS['accent_gold_darker'], text_color="#000000",
    font=ctk.CTkFont(size=13, weight="bold")
)
redo_btn.pack(side="left", padx=5)

revert_btn = ctk.CTkButton(
    history_row, text="⟲ Revert", command=revert_action, 
    width=120, height=45, corner_radius=10,
    fg_color="#f44336", hover_color="#d32f2f",
    border_width=2, border_color="#b71c1c",
    font=ctk.CTkFont(size=13, weight="bold")
)
revert_btn.pack(side="left", padx=(5, 0))

# Enhanced save button with purple gradient
save_btn = ctk.CTkButton(
    action_frame,
    text="💾 Save Image",
    command=save_file,
    height=55,
    font=ctk.CTkFont(size=20, weight="bold"),
    fg_color=COLORS['accent_purple'],
    hover_color=COLORS['accent_purple_dark'],
    border_width=2,
    border_color=COLORS['accent_purple_darker'],
    corner_radius=15
)
save_btn.pack(fill="x", padx=15, pady=(0, 15))

# Enhanced main content area
content_frame = ctk.CTkFrame(main_area, corner_radius=18, border_width=2, border_color=COLORS['accent_gold'])
content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
content_frame.grid_columnconfigure(0, weight=1)
content_frame.grid_rowconfigure(0, weight=1)

# Enhanced image preview with gold accent border
preview_frame = ctk.CTkFrame(content_frame, corner_radius=15, border_width=3, border_color=COLORS['accent_gold'])
preview_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 15))
preview_frame.grid_columnconfigure(0, weight=1)
preview_frame.grid_rowconfigure(0, weight=1)

image_display_label = ctk.CTkLabel(
    preview_frame, 
    text="📷 Open an image to start editing\n\nSupported formats: PNG, JPEG, GIF, BMP, TIFF",
    font=ctk.CTkFont(size=15, weight="bold"),
    text_color=("gray50", "gray60")
)
image_display_label.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)

# Enhanced status log with modern design
status_frame = ctk.CTkFrame(content_frame, height=200, corner_radius=15, border_width=2, border_color=COLORS['accent_gold'])
status_frame.grid(row=1, column=0, sticky="ew")
status_frame.grid_propagate(False)
status_frame.grid_columnconfigure(0, weight=1)
status_frame.grid_rowconfigure(1, weight=1)

log_header = ctk.CTkLabel(status_frame, text="📋 Activity Log", font=ctk.CTkFont(size=20, weight="bold"), text_color=COLORS['text_light'])
log_header.grid(row=0, column=0, pady=(15, 5))

status_log = ctk.CTkTextbox(
    status_frame, 
    height=120,
    font=ctk.CTkFont(family="Consolas", size=14),
    corner_radius=10,
    border_width=2,
    border_color=COLORS['accent_gold_dark']
)
status_log.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))

# Initialize UI
update_ui_state()
log_message("🚀 Welcome to Photo Editor! Open an image to get started.", "info")

app.after(1, lambda: app.state('zoomed'))

# Run the application
app.mainloop()