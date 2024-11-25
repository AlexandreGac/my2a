import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Table,
    TableStyle,
)


def round_time(time):
    """
    Round a time to the nearest slot.
    """
    minutes = time.minute
    if minutes < 30:
        minutes = 0
    else:
        minutes = 30
    return datetime.time(time.hour, minutes)


def ceil_time(time):
    minutes = time.minute
    if minutes > 30:
        minutes = 30
    else:
        minutes = 0
    return datetime.time(time.hour, minutes)


def date_to_hour_id(date: datetime.time):
    return str(date.hour) + ("h" + str(date.minute)).replace("h0", "h00")


def generate_pdf_from_courses(name, courses, intro):
    """
    Generate a pdf from a list of courses.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, rightMargin=0, leftMargin=0, topMargin=0, bottomMargin=0)
    elements = []

    title_style = getSampleStyleSheet()["Normal"]
    title_text = intro.replace("\n", "<br/>") + "<br/><br/>"
    title = Paragraph(title_text, title_style)

    elements.append(title)
    generate_table(elements, courses, "S3A")
    elements.append(PageBreak())
    generate_table(elements, courses, "S3B")
    elements.append(PageBreak())
    generate_table(elements, courses, "S4A") # 2 more pages
    elements.append(PageBreak())
    generate_table(elements, courses, "S4B")
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


def generate_table(elements, courses, semester,part1 = True, part2 = False):
    hour_to_line = {
        "8h00": 1,
        "8h30": 2,
        "9h00": 3,
        "9h30": 4,
        "10h00": 5,
        "10h30": 6,
        "11h00": 7,
        "11h30": 8,
        "12h00": 9,
        "12h30": 10,
        "13h00": 11,
        "13h30": 12,
        "14h00": 13,
        "14h30": 14,
        "15h00": 15,
        "15h30": 16,
        "16h00": 17,
        "16h30": 18,
        "17h00": 19,
        "17h30": 20,
        "18h00": 21,
        "18h30": 22,
        "19h00": 23,
        "19h30": 24,
        "20h00": 25,
    }

    colors_list = [
        colors.lightcoral,
        colors.lightgreen,
        colors.lightcyan,
    ]

    style = TableStyle(
        [
            ("FONTNAME", (0, 0), (-1, -1), "Times-Bold"),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("LINEABOVE", (0, 0), (-1, 0), 1, colors.black),
            ("LINEABOVE", (0, 0), (0, -1), 1, colors.black),
            ("LINEBELOW", (0, 0), (-1, 0), 1, colors.black),
            ("LINEBELOW", (0, 0), (0, -1), 1, colors.black),
            ("LINEAFTER", (1, 1), (-1, -1), 1, colors.black),
            ("LINEAFTER", (0, 0), (0, -1), 1, colors.black),
            ("LINEAFTER", (0, 0), (-1, 0), 1, colors.black),
            ("BACKGROUND", (1, 1), (-1, -1), colors.whitesmoke),
        ]
    )
    table_data = [
        [" ", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"],
        ["8h", " ", " ", " ", " ", " "],
        ["8h30", " ", " ", " ", " ", " "],
        ["9h", " ", " ", " ", " ", " "],
        ["9h30", " ", " ", " ", " ", " "],
        ["10h", " ", " ", " ", " ", " "],
        ["10h30", " ", " ", " ", " ", " "],
        ["11h", " ", " ", " ", " ", " "],
        ["11h30", " ", " ", " ", " ", " "],
        ["12h", " ", " ", " ", " ", " "],
        ["12h30", " ", " ", " ", " ", " "],
        ["13h", " ", " ", " ", " ", " "],
        ["13h30", " ", " ", " ", " ", " "],
        ["14h", " ", " ", " ", " ", " "],
        ["14h30", " ", " ", " ", " ", " "],
        ["15h", " ", " ", " ", " ", " "],
        ["15h30", " ", " ", " ", " ", " "],
        ["16h", " ", " ", " ", " ", " "],
        ["16h30", " ", " ", " ", " ", " "],
        ["17h", " ", " ", " ", " ", " "],
        ["17h30", " ", " ", " ", " ", " "],
        ["18h", " ", " ", " ", " ", " "],
        ["18h30", " ", " ", " ", " ", " "],
        ["19h", " ", " ", " ", " ", " "],
        ["19h30", " ", " ", " ", " ", " "],
        ["20h", " ", " ", " ", " ", " "],
    ]
    style = TableStyle(
        [
            ("FONTNAME", (0, 0), (-1, -1), "Times-Bold"),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("LINEABOVE", (0, 0), (-1, 0), 1, colors.black),
            ("LINEABOVE", (0, 0), (0, -1), 1, colors.black),
            ("LINEBELOW", (0, 0), (-1, 0), 1, colors.black),
            ("LINEBELOW", (0, 0), (0, -1), 1, colors.black),
            ("LINEAFTER", (1, 1), (-1, -1), 1, colors.black),
            ("LINEAFTER", (0, 0), (0, -1), 1, colors.black),
            ("LINEAFTER", (0, 0), (-1, 0), 1, colors.black),
            ("BACKGROUND", (1, 1), (-1, -1), colors.whitesmoke),
        ]
    )

    for course in courses:
        if not (course["semester"] == semester or course["semester"] == semester[:2]):
            continue
        start_line = hour_to_line[date_to_hour_id(round_time(course["start_time"]))]
        end_line = hour_to_line[date_to_hour_id(ceil_time(course["end_time"]))]
        style.add(
            "LINEBELOW",
            (table_data[0].index(course["day"]), start_line - 1),
            (table_data[0].index(course["day"]), start_line - 1),
            1,
            colors.black,
        )
        style.add(
            "LINEABOVE",
            (table_data[0].index(course["day"]), end_line + 1),
            (table_data[0].index(course["day"]), end_line + 1),
            1,
            colors.black,
        )

        middle_line = (start_line + end_line) // 2
        # table_data[middle_line-1][table_data[0].index(course["day"])] = course["name"]
        table_data[middle_line][table_data[0].index(course["day"])] = course["code"]
        table_data[middle_line + 1][table_data[0].index(course["day"])] = (
            str(course["ects"]) + " ECTS"
        )

        for line in range(start_line, end_line + 1):
            style.add(
                "BACKGROUND",
                (table_data[0].index(course["day"]), line),
                (table_data[0].index(course["day"]), line),
                colors_list[course['color'] % len(colors_list)],
            )

    table = Table(table_data, colWidths=100, rowHeights=15)

    table.setStyle(style)

    elements.append(table)
