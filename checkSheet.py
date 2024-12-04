#Currently takes a txt file and outputs a txt file (tested with output from pdfplumber)
#Check boxes are put next to lines with verbs

import spacy

# Load the small English model for spaCy
nlp = spacy.load("en_core_web_sm")

# List of blocked phrases (you can add more phrases as needed)
blocked_phrases = [
    "At any time if the tool has a fault or you have a question STOPand get a Technician", 
    "***Printed copies are NOTcontrolled documents***",
    "BBaacckk ttoo IInnddeexx",
]

def contains_verb(line):
    
    doc = nlp(line)
    
    for token in doc:
        if token.pos_ == "VERB":  # token.pos_ is the part of speech tag
            return True
    return False

def contains_blocked_phrase(line):
    """Check if the line contains any of the blocked phrases."""
    for phrase in blocked_phrases:
        if phrase.lower() in line.lower():  # Case-insensitive check
            return True
    return False

def process_file(input_file, output_file):
    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    # This will hold the processed lines with proper formatting
    processed_lines = []

    current_line = ""
    for line in lines:
        stripped_line = line.strip()

        # If the line starts with spaces or tabs, it's part of a previous sentence
        if stripped_line and line[0] in " \t" and current_line:
            
            current_line += " " + line.strip()  # Add the continuation of the sentence
        else:
            if current_line:
                processed_lines.append(current_line)

            current_line = line.rstrip()  # Keep the indentation and strip only trailing spaces

    # Add the last line if there was any content left
    if current_line:
        processed_lines.append(current_line)

    # Write the processed content with checkboxes to the output file
    with open(output_file, 'w') as outfile:
        for line in processed_lines:
            # Skip lines containing blocked phrases
            if contains_blocked_phrase(line):
                continue

            # Check if the line contains a verb using spaCy
            if contains_verb(line):
                #outfile.write(f"[ ] {line}\n")
                # Right-justify the checkbox `[ ]` at the max width
                # First, remove any leading/trailing spaces from the line
                stripped_line = line.strip()

                # Calculate the position where the checkbox should appear
                space_needed = 80 - len(stripped_line) - 4  # 4 accounts for "[ ] " part
                if space_needed > 0:
                    # Right-justify the checkbox `[ ]`
                    line_with_checkbox = stripped_line + " " * space_needed + "[ ]"
                else:
                    # In case the line is too long, place it immediately after the line
                    line_with_checkbox = stripped_line + " [ ]"
                outfile.write(f"{line_with_checkbox}\n")
            else:
                # Otherwise, just write the line as it is, preserving indentation
                outfile.write(f"{line}\n")

input_file = "output/extracted_text.txt"  
output_file = "checkOut.txt"  

process_file(input_file, output_file)
