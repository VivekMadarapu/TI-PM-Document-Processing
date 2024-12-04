
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import json

# Read input files
with open('output/extracted_text.txt', 'r') as f:
    instructions = f.readlines()

with open('ambiguous.txt', 'r') as f:
    ambiguous_lines = f.readlines()

# Load the spelling errors from a JSON file
with open('response2.json', 'r') as f:
    spellingData = json.load(f)

# Clean up whitespace/newlines
instructions = [line.strip() for line in instructions]
ambiguous_lines = [line.strip() for line in ambiguous_lines]

# Initialize the set of spelling words
spellingWords = set()

#Iterate over the check_sheet and gather all ambiguous_words
for section in spellingData.get("processed_lines", []):
    ambiguous_words = section.get("ambiguous_words", [])
    if ambiguous_words:
        spellingWords.update(ambiguous_words)

#print(spellingWords)

# Create a PDF canvas
pdf_filename = "outputPDF.pdf"
chosenFont = "Helvetica"
c = canvas.Canvas(pdf_filename, pagesize=letter)

# Set up fonts and initial coordinates
c.setFont(chosenFont, 10)
x, y = 40, 750  # Starting position for text

# Function to write text to the PDF with optional highlighting
def write_text(text, x, y, highlight=False, highlight_color=colors.yellow):
    if highlight:
        text_width = c.stringWidth(text, chosenFont, 10)  # Get the actual width of the text (width differs in font sizes)
        c.setFillColor(highlight_color)     # Set background highlight color
        c.rect(x, y - 2, text_width, 12, fill=1)
        c.setFillColor(colors.black)        # Set text color
    c.drawString(x, y, text)

# Iterate through instructions and add to PDF
for line in instructions:
    # Split the line into words and iterate through them
    words = line.split()
    current_x = x   # Start position for the current line

    for word in words:
        # Check if the word is ambiguous (priority 1)
        #is_ambiguous = any(amb_line.lower() == word.lower() for amb_line in ambiguous_lines)
        is_ambiguous = any(amb_line in line for amb_line in ambiguous_lines)
        
        # If the word is ambiguous, highlight it first (yellow, for example)
        if is_ambiguous:
            write_text(word, current_x, y, highlight=True, highlight_color=colors.yellow)
        else:
            # Otherwise, check if it's a spelling error (priority 2)
            is_spelling_error = word.lower() in spellingWords  # Case insensitive comparison
            # Highlight red for spelling errors
            write_text(word, current_x, y, highlight=is_spelling_error, highlight_color=colors.red)
        
        # Move the cursor to the next word's x position
        word_width = c.stringWidth(word, chosenFont, 10)
        current_x += word_width + 5  # Add space between words
    
    # Move to the next line
    y -= 14     # Adjust y for the next line of text
    if y < 50:  # Start a new page if we run out of space
        c.showPage()
        c.setFont(chosenFont, 10)
        y = 750  # Reset y position

# Save the PDF file
c.save()
