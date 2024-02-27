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
    plt.savefig("output/labels_lesions")
    plt.show()
    plt.close()


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

visu = True
if visu:
    plot_labeled_regions_with_mapping(image1_data, image1_labels, image2_data, image2_labels, region_mapping, slice_index)



number_lesions_initial = np.unique(image1_labels)[1:]

print('Number of lesions in first time point', len(number_lesions_initial))

number_lesions_final = np.unique(image2_labels)[1:]

print('Number of lesions in second time point', len(number_lesions_final))

def count_none_mappings(region_mapping):
    """
    Count the number of regions from the first image that are mapped to None.

    :param region_mapping: The dictionary containing the mapping from regions of image1 to image2.
    :return: The count of regions from image1 that are mapped to None.
    """
    none_count = sum(value is None for value in region_mapping.values())
    return none_count

print('Number of lesions that seems to have disappeared is', count_none_mappings(region_mapping))



#here u can use the same mapping function but in reverse order, to find out if a new lesion exist

region_mapping_backward =  map_regions(image2_labels, image1_labels)

print('Number of new lesions that didnt seem to have a precedent is', count_none_mappings(region_mapping_backward)
      )

import json


def convert_numpy_to_python(value):
    """
    Convert a NumPy data type to native Python type for JSON serialization.

    :param value: The value to convert.
    :return: The value converted to a native Python type.
    """
    if isinstance(value, np.generic):
        return value.item()
    elif isinstance(value, dict):
        return {convert_numpy_to_python(key): convert_numpy_to_python(val) for key, val in value.items()}
    elif isinstance(value, list):
        return [convert_numpy_to_python(item) for item in value]
    else:
        return value


def save_mapping_data_to_json(region_mapping, region_mapping_backward, image1_data, image2_data, image1_labels, image2_labels,
                              file_name="region_mapping_log.json"):
    """
    Convert all NumPy data types to Python types and save the region mapping data and lesion counts to a JSON file.

    :param region_mapping: Mapping from the first to the second image.
    :param region_mapping_backward: Mapping from the second back to the first image.
    :param image1_data: Image data for the first time point.
    :param image2_data: Image data for the second time point.
    :param file_name: Name of the file to save the JSON data.
    """
    # Convert NumPy data types to Python for the entire data structure
    region_mapping_python = convert_numpy_to_python(region_mapping)
    region_mapping_backward_python = convert_numpy_to_python(region_mapping_backward)

    data_to_save = {
        "region_mapping_forward": region_mapping_python,
        "region_mapping_backward": region_mapping_backward_python,
        "lesions_initial_time_point": len(np.unique(image1_labels)[1:]),
        "lesions_second_time_point": len(np.unique(image2_labels)[1:]),
        "disappeared_lesions": count_none_mappings(region_mapping),
        "new_lesions": count_none_mappings(region_mapping_backward)
    }

    # Write to JSON file
    with open(file_name, 'w') as outfile:
        json.dump(data_to_save, outfile, indent=4)


save_mapping_data_to_json(region_mapping,
                          region_mapping_backward,
                          image1_data,
                          image2_data,
                          image1_labels,
                          image2_labels, "output/output_data_log.json")

#Now use difference_computation.py to build the difference to see if it increased, or decreased to stayed the same
#Use the same code while adding a condition using the mask label
#Filter on the overlapping regions, i.e. the regions that are mapped to something and not to None



b = 1