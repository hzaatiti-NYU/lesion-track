import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage


def load_nifti_image(file_path):
    """
    Load a NIfTI image and return its data array.

    :param file_path: Path to the NIfTI file.
    :return: Numpy array containing the image data.
    """
    nifti_img = nib.load(file_path)
    return nifti_img.get_fdata()


def find_and_label_regions(image_data, threshold_ratio=0.5):
    """
    Find and label connected white regions in a binary image.

    :param image_data: Numpy array of the image data.
    :param threshold_ratio: Ratio to determine the threshold based on the maximum intensity.
    :return: Labeled image array, number of features.
    """
    threshold = image_data.max() * threshold_ratio
    binary_image = image_data > threshold
    structure = np.ones((3, 3, 3), dtype=int)  # 3D connectivity
    labeled_image, num_features = ndimage.label(binary_image, structure=structure)
    return labeled_image, num_features


def plot_labeled_regions(image_data, labeled_image, slice_index):
    """
    Plot a 3D image slice with labeled regions annotated.

    :param image_data: 3D numpy array of the original image data.
    :param labeled_image: 3D numpy array with labeled regions.
    :param slice_index: Index of the slice to be plotted.
    """
    fig, ax = plt.subplots()
    ax.imshow(image_data[:, :, slice_index], cmap='gray', interpolation='none')
    ax.set_title(f"Slice {slice_index} with Labeled Regions")

    # Overlay the labeled regions
    for region_id in np.unique(labeled_image)[1:]:  # Skip background
        y, x = np.where(labeled_image[:, :, slice_index] == region_id)
        if len(x) > 0 and len(y) > 0:
            centroid_x = np.mean(x)
            centroid_y = np.mean(y)
            ax.text(centroid_x, centroid_y, str(region_id), color='red', ha='center', va='center')

    ax.axis('off')
    plt.show()


import matplotlib.pyplot as plt


def plot_labeled_regions_with_mapping(image1_data, image1_labels, image2_data, image2_labels, region_mapping,
                                      slice_index):
    """
    Plot slices from both images with labeled regions annotated, including the mapping on the second image.

    :param image1_data: 3D numpy array of the first image data.
    :param image1_labels: 3D numpy array with labeled regions for the first image.
    :param image2_data: 3D numpy array of the second image data.
    :param image2_labels: 3D numpy array with labeled regions for the second image.
    :param region_mapping: Dictionary mapping region IDs from image1 to image2.
    :param slice_index: Index of the slice to be plotted for both images.
    """
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))

    # Plot for Image 1
    axs[0].imshow(image1_data[:, :, slice_index], cmap='gray', interpolation='none')
    axs[0].set_title(f"Image 1 Slice {slice_index} with Region IDs")
    for region_id in np.unique(image1_labels)[1:]:  # Skip background
        y, x = np.where(image1_labels[:, :, slice_index] == region_id)
        if len(x) > 0 and len(y) > 0:
            centroid_x = np.mean(x)
            centroid_y = np.mean(y)
            axs[0].text(centroid_x, centroid_y, str(region_id), color='red', ha='center', va='center')
    axs[0].axis('off')

    # Plot for Image 2 with mapping annotations
    axs[1].imshow(image2_data[:, :, slice_index], cmap='gray', interpolation='none')
    axs[1].set_title(f"Image 2 Slice {slice_index} with Region IDs and Mapped IDs from Image 1")
    for region_id in np.unique(image2_labels)[1:]:  # Skip background
        y, x = np.where(image2_labels[:, :, slice_index] == region_id)
        if len(x) > 0 and len(y) > 0:
            centroid_x = np.mean(x)
            centroid_y = np.mean(y)
            axs[1].text(centroid_x, centroid_y, f"{region_id}\n({get_mapped_id(region_id, region_mapping)})",
                        color='blue', ha='center', va='center')
    axs[1].axis('off')

    plt.tight_layout()
    plt.show()


def get_mapped_id(region_id_image2, region_mapping):
    """
    Get the corresponding region ID from image 1 for a region ID in image 2 based on the mapping.

    :param region_id_image2: The region ID in image 2.
    :param region_mapping: The dictionary containing the mapping from image 1 to image 2.
    :return: The corresponding region ID from image 1 or 'N/A' if not found.
    """
    for region_id_image1, mapped_id in region_mapping.items():
        if mapped_id == region_id_image2:
            return region_id_image1
    return 'N/A'



# Replace 'path/to/image.nii' with your actual file path
file_path = 'data/tp001_lesions_manual.nii.gz'

# Load the image, find regions, and plot a slice
image_data = load_nifti_image(file_path)
labeled_image, num_features = find_and_label_regions(image_data)
#slice_index = image_data.shape[2] // 2  # Middle slice for demonstration

slice_index = 125
plot_labeled_regions(image_data, labeled_image, slice_index)


# Assuming you have your images loaded and processed with labels and mapping obtained
# Adjust slice_index as needed for your specific images
slice_index = image1_data.shape[2] // 2  # Example slice index for visualization
plot_labeled_regions_with_mapping(image1_data, image1_labels, image2_data, image2_labels, region_mapping, slice_index)

