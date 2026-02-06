
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from pathlib import Path
from PIL import Image, ImageTk

from scripts.fluent_processing import FluentPostProcesser

class FluentProcessingUI():
    def __init__(self):
        self.fluent_exe_path = Path(r"C:\Program Files\ANSYS Inc\v252\fluent\ntbin\win64\fluent.exe")
        self.root = tk.Tk()
        self.root.geometry("800x400")
        self.root.title("Fluent Post-Processing")

        try:
            img_path = Path("data\logo_brt.png") # Chemin de ton image
            img = Image.open(img_path)
            img = img.resize((200, 200)) # Redimensionnement
            self.photo = ImageTk.PhotoImage(img)
            self.img_label = tk.Label(self.root, image=self.photo)
            self.img_label.grid(row=2, column=0, rowspan=3, padx=20, pady=20)
        except Exception as e:
            print(f"Image not found: {e}")
            self.img_label = tk.Label(self.root, text="[Image Missing]")
            self.img_label.grid(row=1, column=0)

        # create buttons and lables
        self.bt_select_folder = tk.Button(self.root, text="Add new Case", command=self.select_folder)
        self.bt_view_images = tk.Button(self.root, text="View Images", command=self.view_images)
        self.lb_selected_folder = tk.Label(self.root, text="No Folder Selected")
        # place buttons and lables
        self.bt_view_images.grid(row=1, column=1)
        self.bt_select_folder.grid(row=1, column=2)
        self.lb_selected_folder.grid(row=2, column=2)
        self.root.mainloop()

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.lb_selected_folder.config(text=f"Selected folder:\n{folder}")
            self.case_file_path = Path(folder)
            self.bt_run_post_processing = tk.Button(self.root, text="Run Post-Processing", command=self.run_post_processing)
            self.bt_run_post_processing.grid(row=1, column=3)

    def view_images(self):
        folder = filedialog.askdirectory()
        if folder:
            self.image_slider = ImageSlider(self.root, folder)
            self.root.mainloop()


    def run_post_processing(self):
        fluent_processer = FluentPostProcesser(self.fluent_exe_path, self.case_file_path, self)
        self.lb_progress = tk.Label(self.root, text="Initialising Fluent Ansys...")
        self.lb_progress.grid(row=2, column=3)
        self.root.update_idletasks()
        fluent_processer.create_jou_content()
        fluent_processer.run_jou_file()
        fluent_processer.get_excel_data()
        self.lb_progress.config(text=f"done!")
    
    def show_progress(self, progress):
        self.lb_progress.config(text=f"Progress: {progress}%")
        self.root.update_idletasks()

class ImageSlider():
    def __init__(self, root: tk.Tk, folder: Path):
        self.root = root
        self.viewer_frame = ttk.Frame(self.root)
        self.viewer_frame.grid(row=0, column=0, sticky="nsew")
        self.root.title = "Image Viewer"
        self.folder = Path(folder)
        image_files = sorted(self.folder.glob("*.png"))
        if not image_files:
            raise RuntimeError(f"No .png files found in {folder}")

        # Images
        self.images = []
        for f in image_files:
            img = Image.open(f)
            tk_img = ImageTk.PhotoImage(img)
            self.images.append(tk_img)
        
        self.n_images = len(self.images)
        self.current_idx = 0

        self.lb_image = ttk.Label(self.viewer_frame)
        self.lb_image.pack(expand=True, fill="both")

        self.show_image(0) # show first image

        # Slider
        self.slider = ttk.Scale(
            self.viewer_frame,
            from_=0,
            to=self.n_images - 1,
            orient="horizontal",
            command=self.on_slider_move
        )
        self.slider.pack(fill="x", padx=10, pady=10)

        # Keyboard shortcuts
        self.viewer_frame.bind("<Left>", self.prev_image)
        self.viewer_frame.bind("<Right>", self.next_image)

    def show_image(self, index: int):
        self.current_idx = index
        img = self.images[index]
        self.lb_image.configure(image=img)
        self.lb_image.image = img

    def on_slider_move(self, value):
        index = int(float(value))
        if index != self.current_idx:
            self.show_image(index)
    
    def prev_image(self, event=None):
        idx = max(0, self.current_idx - 1)
        self.slider.set(idx)  # this will trigger on_slider_move

    def next_image(self, event=None):
        idx = min(self.n_images - 1, self.current_idx + 1)
        self.slider.set(idx)  # this will trigger on_slider_move