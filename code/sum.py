import csv
import re

# Input and output file paths
input_file = "final.txt"
output_file = "output.tsv"  # Use .tsv for tab-separated values

# Open the input file and process it line by line
with open(input_file, "r") as infile, open(output_file, "w", newline="") as outfile:
    # Initialize CSV writer with tab delimiter
    csv_writer = csv.writer(outfile, delimiter="\t")

    # Write the header row
    csv_writer.writerow(["Group", "Test", "Last_Digit", "TOTAL", "CORRECT_1", "CORRECT_2"])

    # Process each line in the input file
    for line in infile:
        # Extract filename and counts using regex
        match = re.match(r"(.+?) - TOTAL: (\d+) CORRECT_1: (\d+) CORRECT_2: (\d+)", line.strip())
        if match:
            # Split the filename into parts
            filename = match.group(1)
            total = match.group(2)
            correct_1 = match.group(3)
            correct_2 = match.group(4)

            # Parse filename into components
            name_parts = re.match(r"(gpt-\d+)_test_(\d+_\d+)_(\d+)", filename)
            if name_parts:
                group = name_parts.group(1)  # e.g., "gpt-0"
                test = name_parts.group(2)   # e.g., "test_0_0"
                last_digit = name_parts.group(3)  # e.g., "1"

                # Write the parsed data to the TSV file
                csv_writer.writerow([group, test, last_digit, total, correct_1, correct_2])

print(f"TSV file created: {output_file}")
