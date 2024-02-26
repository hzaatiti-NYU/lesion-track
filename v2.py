import nibabel as nib
import numpy as np
from scipy import ndimage


def load_nifti_image(file_path):
    return nib.load(file_path).get_fdata()


def find_white_regions(image, threshold_ratio=0.5):
    # Assuming the white regions are the higher intensities
    # Adjust threshold based on your image intensity range
    threshold = image.max() * threshold_ratio
    binary_image = image > threshold

    # Apply connected component labeling
    # Use structure defining connectivity for the labeling: this example is for 3D
    # For 2D, you can adjust or omit the 'structure' parameter
    structure = np.ones((3, 3, 3), dtype=int)  # Full connectivity in 3D
    labeled_image, num_features = ndimage.label(binary_image, structure=structure)

    return labeled_image, num_features


def track_region_changes(image1_labels, image2, num_features):
    image2_labels, _ = find_white_regions(image2)

    tracking_info = {i: {'status': '', 'new_id': None} for i in range(1, num_features + 1)}

    for i in range(1, num_features + 1):
        region1 = (image1_labels == i)

        # Find overlap with regions in the second image
        overlap = image2_labels[region1]
        unique, counts = np.unique(overlap, return_counts=True)

        # Corrected filtering: Apply mask to unique and then index counts accordingly
        valid_indices = unique != 0  # Mask for non-zero entries
        unique = unique[valid_indices]
        counts = counts[valid_indices]

        if len(unique) == 0:
            tracking_info[i]['status'] = 'disappeared'
        else:
            # The most overlapped region is the corresponding region
            corresponding_region = unique[np.argmax(counts)]
            tracking_info[i]['status'] = 'found'
            tracking_info[i]['new_id'] = corresponding_region

    return tracking_info


# Paths to your NIfTI files
file_path1 = 'data/tp001_lesions_manual.nii.gz'  # Image at the first time point
file_path2 = 'data/tp002_lesions_manual.nii.gz' # Image at the second time point

# Load images
image1 = load_nifti_image(file_path1)
image2 = load_nifti_image(file_path2)

# Find and label white regions in the first image
image1_labels, num_features = find_white_regions(image1)

# Track how these regions evolved in the second image
tracking_info = track_region_changes(image1_labels, image2, num_features)

print(tracking_info)


# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
#
# def generate_pdf_report(tracking_info, output_path='tracking_report.pdf'):
#     c = canvas.Canvas(output_path, pagesize=letter)
#     width, height = letter  # Get the width and height of the page
#     c.setFont("Helvetica", 12)
#
#     # Title
#     c.drawCentredString(width / 2.0, height - 50, "Lesion Tracking Report")
#
#     # Subtitle or additional info
#     c.setFont("Helvetica", 10)
#     c.drawCentredString(width / 2.0, height - 70, "Comparative analysis between two time points")
#
#     # Initialize the y position for the first item
#     y_position = height - 100
#
#     # Loop through each item in tracking_info and add it to the report
#     for region_id, info in tracking_info.items():
#         text = f"Region ID {region_id}: Status - {info['status']}"
#         if 'new_id' in info:
#             text += f", New ID in the second image: {info.get('new_id', 'N/A')}"
#         c.drawString(40, y_position, text)
#         y_position -= 20
#
#         # Check to avoid writing beyond the bottom of the page
#         if y_position < 40:  # Margin
#             c.showPage()
#             c.setFont("Helvetica", 10)
#             y_position = height - 40
#
#     c.save()
#
# # Assuming tracking_info is defined and populated
# # Call the function with the tracking_info dictionary
# generate_pdf_report(tracking_info, 'tracking_report.pdf')
