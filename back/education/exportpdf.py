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


def center_text(txt):
    #assert(len(txt) <= 14)
    L = len(txt)
    return (14 - (L)//2)*" " + txt

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
    generate_table(elements, courses, "S3")
    elements.append(PageBreak())
    generate_table(elements, courses, "S4")
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


def generate_table(elements, courses, semester):
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
    table_data = [
        [" ", "Lundi", "" ,"Mardi", "" , "Mercredi", "" , "Jeudi", "" , "Vendredi", ""],
        ["8h", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["8h30", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["9h", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["9h30", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["10h", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["10h30", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["11h", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["11h30", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["12h", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["12h30", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["13h", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["13h30", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["14h", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["14h30", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["15h", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["15h30", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["16h", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["16h30", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["17h", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["17h30", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["18h", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["18h30", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["19h", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["19h30", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
        ["20h", " ", " ", " ", " ", " "," ", " ", " ", " ", " "],
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
            ("LINEAFTER", (0, 0), (0, -1), 1, colors.black),
            ("LINEAFTER", (0, 0), (-1, 0), 1, colors.black),
            ("BACKGROUND", (1, 1), (-1, -1), colors.whitesmoke),
        ]
    )

    for i in range(1,5):
        style.add("LINEAFTER", (2*i, 0), (2*i, -1), 1, colors.black)

    for course in courses:
        if not (course["semester"][:2] == semester):
            continue
        start_line = hour_to_line[date_to_hour_id(round_time(course["start_time"]))]
        end_line = hour_to_line[date_to_hour_id(ceil_time(course["end_time"]))]

        if course["semester"][2:] == "B":
            column = table_data[0].index(course["day"]) + 1
            style.add(
                "LINEAFTER",
                (column - 1, start_line),
                (column - 1, end_line),
                1,
                colors.black,
            )
            table_data[start_line][column] = course["semester"]
            style.add(
                "LINEABOVE",
                (column, start_line + 1),
                (column, start_line + 1),
                1,
                colors.black,
            )
        else:
            column = table_data[0].index(course["day"])
            if course["semester"][2:] == "A":
                style.add(
                    "LINEAFTER",
                    (column, start_line),
                    (column, end_line),
                    1,
                    colors.black,
                )

        table_data[start_line][column] = course["semester"]
        style.add(
            "LINEABOVE",
            (column, start_line + 1),
            (column, start_line + 1),
            1,
            colors.black,
        )
        style.add(
            "LINEAFTER",
            (table_data[0].index(course["day"]) - 1, start_line),
            (table_data[0].index(course["day"]) - 1, end_line),
            1,
            colors.black,
        )

        style.add(
            "LINEAFTER",
            (table_data[0].index(course["day"]) + 1, start_line),
            (table_data[0].index(course["day"]) + 1, end_line),
            1,
            colors.black,
        )
        style.add(
            "LINEBELOW",
            (column, start_line - 1),
            (column , start_line - 1),
            1,
            colors.black,
        )
        style.add(
            "LINEABOVE",
            (column, end_line + 1),
            (column, end_line + 1),
            1,
            colors.black,
        )

        middle_line = (start_line + end_line) // 2
        if course["semester"][2:] == "":
            table_data[middle_line][column] = center_text(course["code"])
            table_data[middle_line + 1][column] = center_text(str(course["ects"]) + " ECTS")
            table_data[start_line][column] = center_text(course["semester"])
            style.add(
                "ALIGN",
                (column, start_line),
                (column + 1, end_line),
                "LEFT",
            )

            style.add(
                "LINEBELOW",
                (column+1, start_line - 1),
                (column+1 , start_line - 1),
                1,
                colors.black,
            )
            style.add(
                "LINEABOVE",
                (column+1, end_line + 1),
                (column+1, end_line + 1),
                1,
                colors.black,
            )
            style.add(
                "LINEABOVE",
                (column+1, start_line + 1),
                (column+1, start_line + 1),
                1,
                colors.black,
            )
            for line in range(start_line, end_line + 1):
                    style.add(
                        "BACKGROUND",
                        (column, line),
                        (column, line),
                        colors_list[course['color'] % len(colors_list)],
                    )
                    style.add(
                        "BACKGROUND",
                        (column + 1, line),
                        (column + 1, line),
                        colors_list[course['color'] % len(colors_list)],
                    )
        else :
            table_data[middle_line][column] = course["code"]
            table_data[middle_line + 1][column] = (
                str(course["ects"]) + " ECTS"
            )

            for line in range(start_line, end_line + 1):
                style.add(
                    "BACKGROUND",
                    (column, line),
                    (column, line),
                    colors_list[course['color'] % len(colors_list)],
                )

    table = Table(table_data, colWidths=50, rowHeights=15)

    table.setStyle(style)

    elements.append(table)
