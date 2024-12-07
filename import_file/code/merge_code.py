import csv

input_file = 'import_file/item/catagory_01.csv'
output_file = 'import_file/item/catagory_01_filtered.csv'

with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # Write the header
    header = next(reader)
    writer.writerow(header)

    for row in reader:
        # Check if CODE ends with '000' or '001'
        if row[0].endswith('000') or row[0].endswith('001'):
            writer.writerow(row)
