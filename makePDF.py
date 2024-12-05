from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import json


def make_pdf(file_path, clean_file_path):
    with open('output/extracted_text.txt', 'r') as f:
        instructions = f.readlines()

    with open('output/ambiguous.txt', 'r') as f:
        ambiguous_lines = f.readlines()

    with open('output/response.json', 'r') as f:
        spellingData = json.load(f)

    instructions = [line.strip() for line in instructions]
    ambiguous_lines = [line.strip() for line in ambiguous_lines]

    spellingWords = set()

    for section in spellingData.get("processed_lines", []):
        ambiguous_words = section.get("ambiguous_words", [])
        if ambiguous_words:
            spellingWords.update(ambiguous_words)

    pdf_filename = file_path

    chosenFont = "Helvetica"
    c = canvas.Canvas(pdf_filename, pagesize=letter)

    c.setFont(chosenFont, 10)
    x, y = 40, 750

    def write_text(text, x, y, highlight=False, highlight_color=colors.red):
        if highlight:
            text_width = c.stringWidth(text, chosenFont, 10)
            c.setFillColor(highlight_color)
            c.rect(x, y - 2, text_width, 12, fill=1)
            c.setFillColor(colors.black)
        c.drawString(x, y, text)

    for line in instructions:

        words = line.split()
        current_x = x

        is_ambiguous = any(amb_line.lower() == line.lower() for amb_line in ambiguous_lines)

        for word in words:

            is_spelling_error = word.lower() in spellingWords
            if is_spelling_error:
                write_text(word, current_x, y, highlight=True, highlight_color=colors.red)


            else:
                write_text(word, current_x, y, highlight=is_ambiguous, highlight_color=colors.yellow)

            word_width = c.stringWidth(word, chosenFont, 10)
            current_x += word_width + 5

        y -= 14
        if y < 50:
            c.showPage()
            c.setFont(chosenFont, 10)
            y = 750

    c.save()

    pdf_filename = clean_file_path

    chosenFont = "Helvetica"
    c = canvas.Canvas(pdf_filename, pagesize=letter)

    c.setFont(chosenFont, 10)
    x, y = 40, 750

    def write_text(text, x, y, highlight=False, highlight_color=colors.red):
        if highlight:
            text_width = c.stringWidth(text, chosenFont, 10)
            c.setFillColor(highlight_color)
            c.rect(x, y - 2, text_width, 12, fill=1)
            c.setFillColor(colors.black)
        c.drawString(x, y, text)

    for line in instructions:

        words = line.split()
        current_x = x

        for word in words:
            write_text(word, current_x, y, highlight=False, highlight_color=colors.red)

            word_width = c.stringWidth(word, chosenFont, 10)
            current_x += word_width + 5

        y -= 14
        if y < 50:
            c.showPage()
            c.setFont(chosenFont, 10)
            y = 750

    c.save()
