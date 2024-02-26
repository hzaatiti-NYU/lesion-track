import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage


# Assuming load_nifti_image and find_and_label_regions functions are defined as above.


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

def map_regions(image1_labels, image2_labels):
    """
    Map regions from image1 to image2 based on the overlap of labeled regions.

    :param image1_labels: Labeled regions of the first image.
    :param image2_labels: Labeled regions of the second image.
    :return: Dictionary mapping region IDs from image1 to the closest region IDs in image2.
    """
    mapping = {}
    #Assuming that when label = 0, it means it is the background in black
    #np.unique provides a sorted list of the id's of the regions
    for region1_id in np.unique(image1_labels)[1:]:  # Skip background
        region1_mask = image1_labels == region1_id
        overlapping_regions = image2_labels[region1_mask]

        # Count occurrences of each region ID in the overlap area
        region2_id, counts = np.unique(overlapping_regions, return_counts=True)

        # Ignore background
        valid_idx = np.where(region2_id != 0)
        region2_id = region2_id[valid_idx]
        counts = counts[valid_idx]

        if len(counts) == 0:
            # No corresponding region in image2
            mapping[region1_id] = None
        else:
            # Map to the most overlapping region ID in image2
            mapping[region1_id] = region2_id[np.argmax(counts)]

    return mapping


# Load and label regions for both images
file_path1 = 'data/tp001_lesions_manual.nii.gz'  # Image at the first time point
file_path2 = 'data/tp002_lesions_manual.nii.gz' # Image at the second time point

image1_data = load_nifti_image(file_path1)
image1_labels, _ = find_and_label_regions(image1_data)

image2_data = load_nifti_image(file_path2)
image2_labels, _ = find_and_label_regions(image2_data)

# Build the mapping based on the spatial overlap
region_mapping = map_regions(image1_labels, image2_labels)

# Now, region_mapping contains the associations between regions in image1 and image2
print(region_mapping)

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


# Assuming you have your images loaded and processed with labels and mapping obtained
# Adjust slice_index as needed for your specific images
slice_index = image1_data.shape[2] // 2  # Example slice index for visualization
plot_labeled_regions_with_mapping(image1_data, image1_labels, image2_data, image2_labels, region_mapping, slice_index)


from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_pdf_report(tracking_info, output_path='tracking_report.pdf'):
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter  # Get the width and height of the page
    c.setFont("Helvetica", 12)

    # Title
    c.drawCentredString(width / 2.0, height - 50, "Lesion Tracking Report")

    # Subtitle or additional info
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2.0, height - 70, "Comparative analysis between two time points")

    # Initialize the y position for the first item
    y_position = height - 100

    # Loop through each item in tracking_info and add it to the report

    for region_id, info in tracking_info.items():
        text = f"Region ID {region_id}: Status - {info['status']}"
        if 'new_id' in info:
            text += f", New ID in the second image: {info.get('new_id', 'N/A')}"
        c.drawString(40, y_position, text)
        y_position -= 20

        # Check to avoid writing beyond the bottom of the page
        if y_position < 40:  # Margin
            c.showPage()
            c.setFont("Helvetica", 10)
            y_position = height - 40

    c.save()

# Assuming tracking_info is defined and populated
# Call the function with the tracking_info dictionary
generate_pdf_report(tracking_info, 'tracking_report.pdf')