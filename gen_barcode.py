import os
import pandas as pd
import barcode
from barcode.writer import ImageWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

# Read the CSV file
csv_file_path = 'import_file/item/catagory_01_filtered.csv'
barcode_dir = './barcodes'  # Relative path for the barcodes directory

try:
    df = pd.read_csv(csv_file_path)
    print(f"CSV file '{csv_file_path}' loaded successfully.")
except Exception as e:
    print(f"Error reading CSV file '{csv_file_path}': {e}")
    exit(1)

# Filter rows with 'C1' in the CODE
df_c1 = df[df['CODE'].str.startswith('C1')]

if df_c1.empty:
    print("No rows found with 'C1' in the CODE column.")
    exit(1)

# Create a directory for barcode images
os.makedirs(barcode_dir, exist_ok=True)

# Create a canvas for the PDF
pdf_file_path = "barcodes.pdf"
c = canvas.Canvas(pdf_file_path, pagesize=A4)
width, height = A4

# Set initial position
x = 10 * mm
y = height - 20 * mm

# Generate barcodes and add them to the PDF
for index, row in df_c1.iterrows():
    code = row['CODE']
    print(f"Processing code: {code}")

    if not isinstance(code, str):
        print(f"Invalid CODE format: {code}")
        continue

    try:
        # Generate barcode
        barcode_class = barcode.get_barcode_class('code128')
        barcode_obj = barcode_class(code, writer=ImageWriter())
        barcode_filename = os.path.join(barcode_dir, f"{code}.png")

        print(f"Attempting to save barcode for {code}")
        barcode_obj.save(barcode_filename)

        # Check if the barcode image was saved successfully
        if os.path.exists(barcode_filename):
            print(f"Barcode image saved successfully: {barcode_filename}")
            c.drawImage(barcode_filename, x, y, width=50*mm, height=20*mm)
            c.drawString(x, y - 10, code)
        else:
            print(f"Barcode image not found: {barcode_filename}")

    except Exception as e:
        print(f"Error generating or saving barcode for {code}: {e}")

    # Update position
    y -= 30 * mm
    if y < 20 * mm:
        y = height - 20 * mm
        c.showPage()

# Save the PDF
try:
    c.save()
    print(f"PDF generated successfully at '{pdf_file_path}'")
except Exception as e:
    print(f"Error saving PDF: {e}")

print("Processing completed.")
