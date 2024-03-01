import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import nibabel as nib
import os


class NiiImageViewerApp:
    def __init__(self, root, bg1_path, mask1_path, bg2_path, mask2_path, lesions_folder1, lesions_folder2):
        self.root = root
        root.title("NII Image Viewer")

        # Displaying the first set of NII images (background and mask)
        self.display_nii_image(bg1_path, mask1_path, side="left")

        # Displaying the second set of NII images (background and mask)
        self.display_nii_image(bg2_path, mask2_path, side="right")

        # Initialize and pack the lesion images display area for the first set
        self.lesion_image_label1 = tk.Label(root)
        self.lesion_image_label1.pack(side="left", fill="both", expand=True)

        # Dropdown for selecting lesion images for the first set
        self.initialize_lesion_dropdown(lesions_folder1, self.lesion_image_label1, side="left")

        # Initialize and pack the lesion images display area for the second set
        self.lesion_image_label2 = tk.Label(root)
        self.lesion_image_label2.pack(side="right", fill="both", expand=True)

        # Dropdown for selecting lesion images for the second set
        self.initialize_lesion_dropdown(lesions_folder2, self.lesion_image_label2, side="right")

    def display_nii_image(self, bg_path, mask_path, side):
        bg_img = self.load_nii_image(bg_path)
        mask_img = self.load_nii_image(mask_path)
        combined_img = self.overlay_images(bg_img, mask_img)
        img_tk = ImageTk.PhotoImage(image=Image.fromarray(combined_img))

        label = tk.Label(self.root, image=img_tk)
        label.image = img_tk  # Keep a reference!
        label.pack(side=side, padx=10, pady=10)

    def load_nii_image(self, path):
        img = nib.load(path)
        data = img.get_fdata()
        mid_index = data.shape[0] // 2
        return np.rot90(data[mid_index, :, :])

    def overlay_images(self, bg, mask, mask_color=[255, 0, 0]):
        mask_rgb = np.zeros((bg.shape[0], bg.shape[1], 3), dtype=np.uint8)
        for i in range(3):
            mask_rgb[:, :, i] = mask * mask_color[i]
        overlay = np.where(mask_rgb > 0, mask_rgb, np.stack((bg,) * 3, -1))
        return overlay.astype(np.uint8)

    def initialize_lesion_dropdown(self, folder, label, side):
        lesion_images = sorted([f for f in os.listdir(folder) if f.endswith('.png')])
        selected_lesion_var = tk.StringVar(self.root)
        selected_lesion_var.set(lesion_images[0])  # default value

        lesion_dropdown = tk.OptionMenu(self.root, selected_lesion_var, *lesion_images,
                                        command=lambda selection: self.update_lesion_image(folder, selection, label))
        lesion_dropdown.pack(side=side, fill="x")

    def update_lesion_image(self, folder, selection, label):
        image_path = os.path.join(folder, selection)
        image = Image.open(image_path).resize((300, 200))  # Resize to fit
        photo = ImageTk.PhotoImage(image)

        label.configure(image=photo)
        label.image = photo  # Keep a reference!

# Paths to your .nii.gz files - placeholder values
bg1_path = 'data/tp001_mode02_bias_corrected.nii.gz'
mask1_path = 'data/tp001_lesions_manual.nii.gz'
bg2_path = 'data/tp002_mode02_bias_corrected.nii.gz'
mask2_path = 'data/tp002_lesions_manual.nii.gz'
lesions_folder1 = 'lesions_out/lesions_1'
lesions_folder2 = 'lesions_out/lesions_2'

root = tk.Tk()
app = NiiImageViewerApp(root, bg1_path, mask1_path, bg2_path, mask2_path, lesions_folder1, lesions_folder2)
root.mainloop()
