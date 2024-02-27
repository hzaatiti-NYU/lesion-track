import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.utils import ImageReader

# Load JSON data
def load_data(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

# Generate PDF report
def generate_pdf(data, output_filename, image_filename1, image_filename2):
    c = canvas.Canvas(output_filename, pagesize=LETTER)
    c.drawString(100, 750, "Lesion Tracking Report")

    # Coordinates and line height
    y_position = 725
    line_height = 25

    # Lesion counts
    c.drawString(100, y_position, f"Lesions at Initial Time Point: {data['lesions_initial_time_point']}")
    y_position -= line_height
    c.drawString(100, y_position, f"Lesions at Second Time Point: {data['lesions_second_time_point']}")
    y_position -= line_height * 2  # Extra space before images

    c.drawString(100, y_position, f"Disappeared Lesions: {data['disappeared_lesions']}")
    y_position -= line_height

    c.drawString(100, y_position, f"New Lesions: {data['new_lesions']}")
    y_position -= line_height




    # Embedding images for labeled regions
    c.drawString(100, y_position, "Region IDs for two time points, parentheses in the second time point indicate the")
    y_position -= line_height
    c.drawString(100, y_position,
                 "the ID of the mapped region from the first time point:")

    y_position -= 10  # Small padding above the image
    c.drawImage(ImageReader(image_filename1), 100, y_position - 200, width=400, height=200)
    y_position -= 210  # Space to next section, adjust as needed

    c.drawString(100, y_position, "Color-coded visual track of lesions evolution")
    y_position -= 10  # Small padding above the image
    c.drawImage(ImageReader(image_filename2), 50, y_position - 200, width=500, height=200)
    y_position -= 220  # Space to next section, adjust as needed

    # Forward mapping information
    c.drawString(100, y_position, "Forward Region Mapping (Initial to Second):")
    y_position -= line_height
    for key, value in data['region_mapping_forward'].items():
        c.drawString(100, y_position, f"Region {key} maps to Region {value}")
        y_position -= line_height
        if y_position < 50:
            c.showPage()
            y_position = 750

    # Ensuring a new page for backward mapping for better readability
    c.showPage()
    y_position = 750

    # Backward mapping information
    c.drawString(100, y_position, "Backward Region Mapping (Second to Initial):")
    y_position -= line_height
    for key, value in data['region_mapping_backward'].items():
        c.drawString(100, y_position, f"Region {key} maps to Region {value}")
        y_position -= line_height
        if y_position < 50:
            c.showPage()
            y_position = 750

    c.save()

# Main function to execute the process
def main():

    DIR = "output/"
    json_filename = DIR+'output_data_log.json'
    pdf_filename = DIR+'lesion_tracking_report.pdf'
    image_filename1 = DIR+'labels_lesions.png'  # Path to your generated image for initial time point
    image_filename2 = DIR+'difference_lesions.png'  # Path to your generated image for second time point

    data = load_data(json_filename)
    generate_pdf(data, pdf_filename, image_filename1, image_filename2)

if __name__ == '__main__':
    main()
