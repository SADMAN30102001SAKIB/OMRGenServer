import io
import os

from flask import Flask, request, send_file
from flask_cors import CORS
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

app = Flask(__name__)
CORS(app)


def add_rectangles_to_pdf(
    input_pdf_path,
    output_pdf_path,
    rects_details_1,
    rects_details_2,
    permission,
    text_details_1,
    text_details_2,
):
    def create_pdf_with_rects(rects_details_1, text_details):
        packet = io.BytesIO()
        can = canvas.Canvas(packet)
        for text_detail in text_details:
            x, y, text, font_size, font_family, color, is_underlined = text_detail
            can.setFont(font_family, font_size)
            can.setFillColor(color)
            can.drawString(x, y, text)

            if is_underlined:
                text_width = can.stringWidth(text, font_family, font_size)
                can.line(x, y - 2, x + text_width, y - 2)
        for rect_details in rects_details_1:
            x, y, width, height, color = rect_details
            can.setFillColor(color)
            can.rect(x, y, width, height, fill=1, stroke=0)
        can.save()
        packet.seek(0)
        return PdfReader(packet)

    new_pdf_1 = create_pdf_with_rects(rects_details_1, text_details_1)
    new_pdf_2 = create_pdf_with_rects(rects_details_2, text_details_2)

    existing_pdf = PdfReader(open(input_pdf_path, "rb"))
    output = PdfWriter()

    for i, page in enumerate(existing_pdf.pages):
        if i == 0 and len(new_pdf_1.pages) > 0:
            page.merge_page(new_pdf_1.pages[0])
            output.add_page(page)
        elif i == 1 and len(new_pdf_2.pages) > 0 and permission:
            page.merge_page(new_pdf_2.pages[0])
            output.add_page(page)

    with open(output_pdf_path, "wb") as outputStream:
        output.write(outputStream)


@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    data = request.json
    iName = data.get("iName")
    isIUnderline = data.get("isIUnderline")
    pName = data.get("pName")
    isPUnderline = data.get("isPUnderline", True)
    isName = data.get("isName", True)
    isRoll = data.get("isRoll", True)
    rollDigit = int(data.get("rollDigit"))
    setCount = int(data.get("setCount"))
    questionsCount = int(data.get("questionsCount"))

    text_details_1 = [
        (
            65,
            740,
            iName,
            16,
            "Helvetica-Bold",
            "black",
            isIUnderline,
        ),
        (
            65,
            720,
            pName,
            9,
            "Helvetica-BoldOblique",
            "black",
            isPUnderline,
        ),
    ]
    text_details_2 = [
        (
            70,
            740,
            iName,
            16,
            "Helvetica-Bold",
            "black",
            isIUnderline,
        ),
        (
            70,
            725,
            pName,
            9,
            "Helvetica-BoldOblique",
            "black",
            isPUnderline,
        ),
    ]

    input_pdf_path = "input.pdf"
    output_pdf_path = "output.pdf"

    color = "white"
    rects_details_1 = [
        (
            0,
            0,
            0,
            0,
            "white",
        )
    ]
    rects_details_2 = [
        (
            0,
            0,
            0,
            0,
            "white",
        )
    ]
    if not isName:
        rects_details_1.append(
            (
                382,
                710,
                175,
                20,
                color,
            )
        )
        rects_details_2.append(
            (
                65,
                685,
                255,
                30,
                color,
            )
        )

    eraseRollDigit = 11 - rollDigit
    if not isRoll:
        rects_details_1.append(
            (
                70,
                510,
                220,
                190,
                color,
            )
        )
        rects_details_2.append(
            (
                370,
                690,
                220,
                30,
                color,
            )
        )
    elif eraseRollDigit > 0:
        rects_details_1.append(
            (
                278.60 - (eraseRollDigit * 15.205),
                683,
                eraseRollDigit * 15.24,
                20,
                color,
            )
        )

    eraseSetCount = 4 - setCount
    if eraseSetCount > 2:
        rects_details_1.append((290, 280, 65, 170, color))
    elif eraseSetCount > 0:
        rects_details_1.append((305, 337, 25, eraseSetCount * 22.5, color))
        rects_details_1.append((343, 337, 10, eraseSetCount * 22.5, color))

    permission = True
    eraseQuestionCount = 100 - questionsCount
    if eraseQuestionCount >= 65:
        permission = False
        eraseQuestionCount -= 65
        if eraseQuestionCount >= 20:
            box1Height = eraseQuestionCount - 20
            if box1Height > 0:
                rects_details_1.append((110, 75, 115, box1Height * 23.69, color))
                rects_details_1.append((60, 75, 35, box1Height * 23.69, color))
            rects_details_1.append((385, 65, 240, 22 * 24, color))
        elif eraseQuestionCount > 0:
            rects_details_1.append((425, 75, 115, eraseQuestionCount * 24, color))
            rects_details_1.append((375, 75, 35, eraseQuestionCount * 24, color))
    else:
        if eraseQuestionCount >= 40:
            box1Height = eraseQuestionCount - 40
            if box1Height > 0:
                rects_details_2.append((75, 165, 120, box1Height * 19.2, color))
                rects_details_2.append((25, 164, 35, box1Height * 19.2, color))
            rects_details_2.append((215, 170, 205, 22 * 23, color))
            rects_details_2.append((405, 190, 240, 21 * 22.5, color))
        elif eraseQuestionCount >= 18:
            box2Height = eraseQuestionCount - 18
            if box2Height > 0:
                rects_details_2.append((265, 179, 120, box2Height * 21.2, color))
                rects_details_2.append((215, 179, 35, box2Height * 21.2, color))
            rects_details_2.append((405, 190, 240, 21 * 22.5, color))
        elif eraseQuestionCount > 0:
            rects_details_2.append((455, 210, 115, eraseQuestionCount * 24, color))
            rects_details_2.append((405, 210, 35, eraseQuestionCount * 24, color))

    add_rectangles_to_pdf(
        input_pdf_path,
        output_pdf_path,
        rects_details_1,
        rects_details_2,
        permission,
        text_details_1,
        text_details_2,
    )
    current_dir = os.path.dirname(__file__)
    output_file_path = os.path.join(current_dir, "output.pdf")

    try:
        return_value = send_file(output_file_path, as_attachment=True)
    finally:
        os.remove(output_file_path)

    return return_value


@app.route("/")
def hello():
    return "Hello"
