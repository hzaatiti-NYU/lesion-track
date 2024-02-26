import nibabel as nib
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt

# Load NIfTI images
file_path1 = 'data/tp001_lesions_manual.nii.gz'  # Image at the first time point
file_path2 = 'data/tp002_lesions_manual.nii.gz' # Image at the second time point

nifti_image1 = nib.load(file_path1)
nifti_image2 = nib.load(file_path2)

image_data1 = nifti_image1.get_fdata() > 0  # Binary thresholding
image_data2 = nifti_image2.get_fdata() > 0

# Label connected components in each image
labelled_image1, num_features1 = ndimage.label(image_data1)
labelled_image2, num_features2 = ndimage.label(image_data2)

# Initialize a mapping dictionary
region_mapping = {}

# Iterate over each region in the first image
for region_id1 in range(1, num_features1 + 1):
    region_mask1 = labelled_image1 == region_id1
    overlapping_regions = labelled_image2[region_mask1]

    # Identify the most common non-zero region in the second image that overlaps with the current region
    if overlapping_regions.size > 0 and np.any(overlapping_regions > 0):
        region_id2 = np.bincount(overlapping_regions[overlapping_regions > 0]).argmax()
        if region_id2 > 0:
            region_mapping[region_id1] = region_id2
        else:
            # Handle the case where there is no overlapping region
            region_mapping[region_id1] = None


# Plotting function with region IDs annotated
def plot_image_with_labels(image_data, labeled_image, title, ax):
    ax.imshow(image_data, cmap='gray', interpolation='none')
    ax.set_title(title)
    ax.axis('off')

    # Annotate region IDs
    for region_id in np.unique(labeled_image):
        if region_id == 0:  # Skip background
            continue

        region_coords = np.where(labeled_image == region_id)
        center_x, center_y = np.mean(region_coords[1]), np.mean(region_coords[0])

        ax.annotate(str(region_id), (center_x, center_y), color='red', weight='bold',
                    fontsize=12, ha='center', va='center')


# Plotting the images with annotations
fig, axes = plt.subplots(1, 2, figsize=(12, 6))

plot_image_with_labels(image_data1, labelled_image1, 'Image 1 with Region IDs', axes[0])
plot_image_with_labels(image_data2, labelled_image2, 'Image 2 with Region IDs', axes[1])

plt.tight_layout()
plt.show()

# Print the mapping
print("Region ID Mapping from Image 1 to Image 2:")
for k, v in region_mapping.items():
    print(f"Region {k} in Image 1 is mapped to Region {v} in Image 2.")