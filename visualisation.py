import matplotlib.pyplot as plt
from matplotlib import patches
import numpy as np
from utils import get_mapped_id

def plot_region_center_zoom(image_data, region_properties, region_id, out_number, zoom_size=100):
    """
    Plot the region centered at its mean coordinate with a zoom-in effect.

    :param image_data: The 3D image data array.
    :param labeled_image: The 3D labeled image array.
    :param region_properties: Properties of the regions.
    :param region_id: The ID of the region to plot.
    :param zoom_size: The size around the center to zoom into.
    """
    center = region_properties[region_id]['center']
    #we need to round to the nearest integer

    slice_index = int(center[2])
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(image_data[:, :, slice_index], cmap='gray')
    ax.set_xlim(center[0] - zoom_size, center[0] + zoom_size)
    ax.set_ylim(center[1] - zoom_size, center[1] + zoom_size)
    ax.invert_yaxis()  # Invert the y-axis to match image coordinates
    ax.set_title(f"Region {region_id} at Slice {slice_index}")
    plt.savefig('lesions_out/lesions_' + str(out_number) + '/lesion' + str(region_id))
    plt.show()


def plot_region_center_full_size(image_data, region_properties, region_id, out_number, zoom_size=10):
    """
    Plot the region centered at its mean coordinate, highlighting the area with a red square
    without zooming in, maintaining the full image context.

    :param image_data: The 3D image data array.
    :param region_properties: Properties of the regions, including their centers.
    :param region_id: The ID of the region to plot.
    :param out_number: Output number for file naming.
    :param zoom_size: The size around the center to create the red square.
    """
    # Get the center of the region of interest
    center = region_properties[region_id]['center']

    # Calculate the coordinates for the red square
    y_min = max(center[0] - zoom_size, 0)
    y_max = min(center[0] + zoom_size, image_data.shape[1])
    x_min = max(center[1] - zoom_size, 0)
    x_max = min(center[1] + zoom_size, image_data.shape[0])

    # Get the slice index and ensure it's within the bounds
    slice_index = int(center[2])
    slice_index = max(min(slice_index, image_data.shape[2] - 1), 0)

    # Create a plot
    fig, ax = plt.subplots(figsize=(6, 6))
    temp_im = image_data[:, :, slice_index]
    ax.imshow(temp_im, cmap='gray')

    # Create a red rectangle to highlight the region
    rect = patches.Rectangle((x_min, y_min), x_max - x_min, y_max - y_min,
                             linewidth=1, edgecolor='r', facecolor='none')
    ax.add_patch(rect)

    # Ensure the full image is displayed
    ax.set_xlim(0, image_data.shape[1])
    ax.set_ylim(image_data.shape[0], 0)  # Inverted y-axis to match image coordinates

    # Set title and save the plot
    ax.set_title(f"Region {region_id} at Slice {slice_index}")
    plt.savefig(f'lesions_out/lesions_{out_number}/lesion{region_id}.png')
    plt.show()


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


def plot_region_center_full_size_bg(background_data, lesion_data, region_properties, region_id, out_number, zoom_size=100):
    """
    Plot the lesion region highlighted on the background image.

    :param background_data: The 3D background image data array.
    :param lesion_data: The 3D lesion image data array.
    :param region_properties: Properties of the lesion regions.
    :param region_id: The ID of the lesion region to plot.
    :param out_number: Output number for file naming.
    :param zoom_size: The size around the center to create the highlight.
    """
    """
       Plot the lesion region highlighted on the background image.

       :param background_data: The 3D background image data array.
       :param lesion_data: The 3D lesion image data array.
       :param region_properties: Properties of the lesion regions.
       :param region_id: The ID of the lesion region to plot.
       :param out_number: Output number for file naming.
       :param zoom_size: The size around the center to create the highlight.
       """
    # Get the center of the lesion region; adjusting center coordinates for image dimensions
    center = region_properties[region_id]['centroid']
    x_center, y_center = center[1], center[0]  # Adjusting x and y based on image coordinate system

    # Determine the bounding box for the lesion region
    x_min = max(x_center - zoom_size, 0)
    x_max = min(x_center + zoom_size, background_data.shape[1])
    y_min = max(y_center - zoom_size, 0)
    y_max = min(y_center + zoom_size, background_data.shape[0])

    # Get the appropriate slice from the background and lesion data
    slice_index = int(center[2])
    background_slice = background_data[:, :, slice_index]
    lesion_slice = np.zeros_like(background_slice)
    lesion_slice[lesion_data[:, :, slice_index] == region_id] = 1  # Isolate the region

    # Plotting
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(background_slice, cmap='gray')  # Show the background
    ax.imshow(np.ma.masked_where(lesion_slice == 0, lesion_slice), cmap='autumn', alpha=0.7)  # Overlay the lesion

    # Highlight the lesion region with a rectangle
    rect = patches.Rectangle((x_min, y_min), x_max - x_min, y_max - y_min,
                             linewidth=1, edgecolor='r', facecolor='none')
    ax.add_patch(rect)

    # Finalize plot
    ax.set_xlim(0, background_data.shape[1])
    ax.set_ylim(background_data.shape[0], 0)
    ax.set_title(f"Region {region_id} at Slice {slice_index}")
    plt.savefig(f'lesions_out/lesions_{out_number}/lesion{region_id}.png')
    plt.show()


# def plot_region_center(image_data, region_properties, region_id, number, zoom_size=100):
#     """
#     Plot the region centered at its mean coordinate with a zoom-in effect.
#
#     :param image_data: The 3D image data array.
#     :param region_properties: Properties of the regions.
#     :param region_id: The ID of the region to plot.
#     :param number: Identifier for the output image set.
#     :param zoom_size: The size around the center to zoom into.
#     """
#     center = region_properties[region_id]['center']
#     slice_index = int(center[2])
#
#     # Define plot limits, ensuring they stay within the image boundaries
#     x_min = max(center[0] - zoom_size, 0)
#     x_max = min(center[0] + zoom_size, image_data.shape[0])
#     y_min = max(center[1] - zoom_size, 0)
#     y_max = min(center[1] + zoom_size, image_data.shape[1])
#
#     fig, ax = plt.subplots(figsize=(6, 6))
#     # Use vmin and vmax to enhance contrast, setting them based on non-background pixels
#     non_background = image_data[image_data > 0]
#     if non_background.size > 0:
#         vmin, vmax = non_background.min(), non_background.max()
#     else:
#         vmin, vmax = image_data.min(), image_data.max()
#     ax.imshow(image_data[:, :, slice_index], cmap='gray', vmin=vmin, vmax=vmax)
#     ax.set_xlim(x_min, x_max)
#     ax.set_ylim(y_max, y_min)  # Inverted y-axis
#     ax.set_title(f"Region {region_id} at Slice {slice_index}")
#     plt.savefig(f'lesions_out/lesions_{number}/lesion{region_id}.png')
#     plt.close()  # Close the plot to free memory


