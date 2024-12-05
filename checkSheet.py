import spacy

nlp = spacy.load("en_core_web_sm")

blocked_phrases = [
    "At any time if the tool has a fault or you have a question STOPand get a Technician",
    "***Printed copies are NOTcontrolled documents***",
    "BBaacckk ttoo IInnddeexx",
]


def contains_verb(line):
    doc = nlp(line)

    for token in doc:
        if token.pos_ == "VERB":
            return True
    return False


def contains_blocked_phrase(line):
    """Check if the line contains any of the blocked phrases."""
    for phrase in blocked_phrases:
        if phrase.lower() in line.lower():
            return True
    return False


def generate_checksheet(input_file, output_file):
    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    processed_lines = []

    current_line = ""
    for line in lines:
        stripped_line = line.strip()

        if stripped_line and line[0] in " \t" and current_line:

            current_line += " " + line.strip()
        else:
            if current_line:
                processed_lines.append(current_line)

            current_line = line.rstrip()

    if current_line:
        processed_lines.append(current_line)

    with open(output_file, 'w') as outfile:
        for line in processed_lines:

            if contains_blocked_phrase(line):
                continue

            if contains_verb(line):

                stripped_line = line.strip()

                space_needed = 80 - len(stripped_line) - 4
                if space_needed > 0:

                    line_with_checkbox = stripped_line + " " * space_needed + "[ ]"
                else:

                    line_with_checkbox = stripped_line + " [ ]"
                outfile.write(f"{line_with_checkbox}\n")
            else:

                outfile.write(f"{line}\n")
