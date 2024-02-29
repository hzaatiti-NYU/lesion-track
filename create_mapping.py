
from visualisation import *
from utils import *


# Load and label regions for both images
lesion_mask1 = 'data/tp001_lesions_manual.nii.gz'  # Image at the first time point
lesion_mask2 = 'data/tp002_lesions_manual.nii.gz' # Image at the second time point

background_1 = 'data/tp001_mode02_bias_corrected.nii.gz'
background_2 = 'data/tp002_mode02_bias_corrected.nii.gz'


background1_data = load_nifti_image(background_1)
background2_data = load_nifti_image(background_2)

image1_data = load_nifti_image(lesion_mask1)
image1_labels, _ = find_and_label_regions(image1_data)

image2_data = load_nifti_image(lesion_mask2)
image2_labels, _ = find_and_label_regions(image2_data)


# Compute properties for each labeled image
image1_properties = compute_region_properties(image1_labels)
image2_properties = compute_region_properties(image2_labels)



# Store the dictionaries in an array or list
region_properties_array = [image1_properties, image2_properties]

for region_id1 in image1_properties:
    #plot_region_center_full_size(image1_data, image1_properties, region_id1, 1)
    plot_region_center_full_size_bg(background1_data, image1_labels,  image1_properties, region_id1, 1)

for region_id2 in image2_properties:
    plot_region_center_full_size_bg(background1_data, image2_labels, image2_properties, region_id2, 2)


# Assuming you have two labeled images: image1_labels and image2_labels


# Build the mapping based on the spatial overlap
region_mapping = map_regions(image1_labels, image2_labels)

# Now, region_mapping contains the associations between regions in image1 and image2
print(region_mapping)



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


print('Number of lesions that seems to have disappeared is', count_none_mappings(region_mapping))


#here u can use the same mapping function but in reverse order, to find out if a new lesion exist

region_mapping_backward =  map_regions(image2_labels, image1_labels)

print('Number of new lesions that didnt seem to have a precedent is', count_none_mappings(region_mapping_backward)
      )

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