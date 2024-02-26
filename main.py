import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# Replace these paths with the paths to your actual NIfTI files
file_path1 = 'data/tp001_lesions_manual.nii.gz'  # Image at the first time point
file_path2 = 'data/tp002_lesions_manual.nii.gz' # Image at the second time point

# Load the images
nifti_image1 = nib.load(file_path1)
nifti_image2 = nib.load(file_path2)

# Extract the data arrays
image_data1 = nifti_image1.get_fdata()
image_data2 = nifti_image2.get_fdata()

# Compute the difference with specific conditions
difference_volume = np.zeros_like(image_data1)
difference_volume[np.where((image_data1 == 1) & (image_data2 == 1))] = 1  # White to white
difference_volume[np.where((image_data1 == 1) & (image_data2 == 0))] = 2  # White to black
difference_volume[np.where((image_data1 == 0) & (image_data2 == 1))] = 3  # Black to white

# Define the colormap for the difference image
cmap = ListedColormap(['black', 'green', 'blue', 'red'])

# Define the function to display all images
def display_images(slice_index):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Display Image 1
    axes[0].imshow(image_data1[:, :, slice_index], cmap='gray')
    axes[0].set_title(f"Image 1: Slice {slice_index}")
    axes[0].axis('off')

    # Display Image 2
    axes[1].imshow(image_data2[:, :, slice_index], cmap='gray')
    axes[1].set_title(f"Image 2: Slice {slice_index}")
    axes[1].axis('off')

    # Display the Difference Image
    im = axes[2].imshow(difference_volume[:, :, slice_index], cmap=cmap)
    axes[2].set_title(f"Difference: Slice {slice_index}")
    axes[2].axis('off')

    # Add colorbar to explain the difference image, placing it outside the subplot
    fig.subplots_adjust(right=0.85)
    cbar_ax = fig.add_axes([0.88, 0.15, 0.02, 0.7])  # Positioning the colorbar
    cbar = fig.colorbar(im, cax=cbar_ax, ticks=[0, 1, 2, 3])
    cbar.set_ticklabels(['No Change (Black)', 'Unchanged (White to White)', 'Decrease (White to Black)', 'Increase (Black to White)'])
    cbar.ax.set_ylabel('Change Type', rotation=270, labelpad=15)
    plt.title("Showing the ")
    plt.show()

# Example usage for a specific slice
slice_index = difference_volume.shape[2] // 2
display_images(slice_index)
