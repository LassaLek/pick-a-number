import os
import json
import re

# Initialize the output file
output_file = "final.txt"

# Get the current working directory
current_dir = os.getcwd()

# Initialize the summary list
summary = []

# Process each .txt file in the current directory
for filename in os.listdir(current_dir):
    if filename.endswith(".txt"):
        file_path = os.path.join(current_dir, filename)

        total_lines = 0
        correct_1 = 0
        correct_2 = 0

        # Open and process the file line by line
        with open(file_path, "r") as file:
            for line in file:
                total_lines += 1

                # Count lines with "number_yes": true
                if '"number_yes": true' in line:
                    correct_1 += 1

                # Count lines matching the full condition
                pattern = r'{"number_yes": true, "numbe_no": false}, {"answers_yes": true, "answers_no": false}'
                if re.search(pattern, line):
                    correct_2 += 1

        # Add results for this file
        summary.append(f"{filename} - TOTAL: {total_lines} CORRECT_1: {correct_1} CORRECT_2: {correct_2}")

# Write the summary to the output file
with open(output_file, "w") as out_file:
    out_file.write("\n".join(summary))

print(f"Summary written to {output_file}")
