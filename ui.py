
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from PIL import Image, ImageTk

from fluent_processing import FluentPostProcesser

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
            self.root.quit()
            self.image_slider = ImageSlider(folder)

    def run_post_processing(self):
        fluent_processer = FluentPostProcesser(self.fluent_exe_path, self.case_file_path, self)
        self.lb_progress = tk.Label(self.root, text="Initialising Fluent Ansys...")
        self.lb_progress.grid(row=2, column=3)
        self.root.update_idletasks()
        fluent_processer.run_jou_file()
        fluent_processer.get_excel_data()
        self.lb_progress.config(text=f"done!")
    
    def show_progress(self, progress):
        self.lb_progress.config(text=f"Progress: {progress}%")
        self.root.update_idletasks()

class ImageSlider():
    def __init__(self, folder: Path):
        self.folder = folder