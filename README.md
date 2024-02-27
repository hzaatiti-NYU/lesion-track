# lesion-track



Load two .nii.gz images

For each image, we find connected white regions, every region is attributed an ID.
Note: the connected set can be non-convex, w're only looking for a connected set
If 1's are on the diagonal of the matrix, they are considered a connected set

Then, a mapping is defined to map one region from the first image, to one region of the second image.
The mapping is done as follows:
- for each region in the first image, we will compute the overlap with regions of the second image
- the highest overlapping region from the second image, will be mapped to that region of the first image

Way forward:
- have the raw image for a better visualisation of the position of lesions
- have images for different slices (currently slice 130, middle one is plotted)
- have images for each lesion, and plot it at its center slice
- add qualitative attribute to each lesion (increased, decreased, disappeared, appeared)
