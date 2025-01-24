import datetime
from io import BytesIO
import random as rd
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


def is_year_bissextile(year):
    return (year % 4 == 0) and (year % 100 != 0) or (year % 400 == 0)


def add_n_day(day,n):
    newday = day[0] + n
    newmonth = day[1]
    if newday > day_in_month[day[1]]:
        newday -= day_in_month[day[1]]
        newmonth = day[1]%12 + 1
    return newday,newmonth

def add_one_week(day):
    return add_n_day(day,7)

def is_after(day1, day2):
    if day1[1] == day2[1]:
        return day1[0] > day2[0]
    else:
        return (day1[1]-8)%12 > (day2[1] - 8)%12


def find_day_and_week(day):
    actual_monday = semester_begin[0]
    old_monday = actual_monday
    weeks = 0
    while is_after(day, actual_monday):
        weeks += 1
        old_monday = actual_monday
        actual_monday = add_one_week(actual_monday)
    days = 0
    while is_after(day, old_monday):
        days += 1
        old_monday = add_n_day(old_monday,1)
    return weeks,days


def write_specil_week(specil_weeks, table_data, style,color):
    for key in specil_weeks:
        for i in range(20):
            table_data[week[key]][i+1] = ""
        table_data[week[key]][len(table_data[0])//2] = specil_weeks[key]
        style.add("BACKGROUND", (1, week[key]), (-1, week[key]), color,)


year = 2025



day_in_month = {
    1 : 31,
    2 : 29 if is_year_bissextile(year) else 28,
    3 : 31,
    4 : 30,
    5 : 31,
    6 : 30,
    7 : 31,
    8 : 31,
    9 : 30,
    10: 31,
    11: 30,
    12: 31
}

semester_to_int = {
    "S3A" : [1],
    "S3B" : [2],
    "S4A" : [3],
    "S4B" : [4],
    "S3" : [1,2],
    "S4" : [3,4]
}

semester_begin = {
    0 : (26,8),
    1 : (16,9),
    2 : (18,11),
    3 : (3,2),
    4 : (14,4),
    5 : (16,6)
}

vacation = {
    (28,10) : "Vacances de Toussaint",
    (23,12) : "Vacances de Noel",
    (30,12) : "Vacances de Noel",
    (24,2) : "Vacances d'Hiver",
    (21,4) : "Vacances de Pâques"
}

pedagogic_day = {
    0 : (28,3),
    1 : (15,1),
    2 : (10,6)
}

ouverture_week = {
    (26,8) : "Semaine d'entrée",
    (2,9) : "Semaine Gestion",
    (9,9) : "Voyage de département",
    (25,11) : "Semaine Athens"
}

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

background_color = {
    0 : colors.HexColor("#c9ff96"),
    1 : colors.HexColor("#7fd3ab"),
    2 : colors.HexColor("#ffcb67"),
    3 : colors.HexColor("#67b5ff"),
    4 : colors.HexColor("#ddff67"),
    5 : colors.HexColor("#da9870"),
    6 : colors.HexColor("#da70c0"),
    7 : colors.HexColor("#70da84"),
    8 : colors.HexColor("#cffd5d")
}


code_to_hour_line = {}

week = {}
actual_monday = semester_begin[0]
i = 1
while actual_monday != semester_begin[5]:
    week[actual_monday] = i
    actual_monday = add_one_week(actual_monday)
    i+=1


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
    elements.append(PageBreak())
    generate_annual_table(elements, courses)
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


def generate_table(elements, courses, semester):

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

def add_course(course, table_data, sem, day = None,emplacement = None, dire = None):
    if not course["code"] in code_to_hour_line:
        code_to_hour_line[course["code"]] = hour_to_line[date_to_hour_id(round_time(course["start_time"]))]
    if emplacement == None:
        if code_to_hour_line[course["code"]] >= 17:
            add_course(course, table_data, sem, day, 3)
        else:
            if code_to_hour_line[course["code"]] >= 11:
                add_course(course, table_data, sem, day, 2)
            else:
                if code_to_hour_line[course["code"]] >= 5:
                    add_course(course, table_data, sem, day, 1)
                else:
                    add_course(course, table_data, sem, day, 0)
    else:
        if day == None:
            day = semester_begin[sem]
        if emplacement == -1:
            pass
        else:
            if table_data[week[day]][table_data[0].index(course["day"]) + emplacement] == "":
                table_data[week[day]][table_data[0].index(course["day"]) + emplacement] = course["code"]
            else:
                if code_to_hour_line[table_data[week[day]][table_data[0].index(course["day"]) + emplacement]] > code_to_hour_line[course["code"]]:
                    if table_data[0].index(course["day"]) + emplacement + 1 != 4 and table_data[week[day]][table_data[0].index(course["day"]) + emplacement + 1] == "":
                        table_data[week[day]][table_data[0].index(course["day"]) + emplacement + 1] = table_data[week[day]][table_data[0].index(course["day"]) + emplacement]
                        table_data[week[day]][table_data[0].index(course["day"]) + emplacement] = course["code"]
                    else:
                        if table_data[0].index(course["day"]) + emplacement - 1 != -1 and table_data[week[day]][table_data[0].index(course["day"]) + emplacement - 1] == "":
                            table_data[week[day]][table_data[0].index(course["day"]) + emplacement - 1] = course["code"]
                        else:
                            pass


            day = add_one_week(day)
            if day != semester_begin[sem+1]:
                add_course(course, table_data, sem, day,emplacement)


def generate_annual_table(elements, courses):

    actual_monday = semester_begin[0]

    colors_list = [
        colors.lightcoral,
        colors.lightgreen,
        colors.lightcyan,
    ]
<<<<<<< HEAD
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
=======

    table_data = [
        [" ", "Lundi", "" , "" , "" ,"Mardi", "" , "" , "" , "Mercredi", "" , "" , "" , "Jeudi", "" , "" , "" , "Vendredi", "" , "" , ""]
>>>>>>> migration-info
    ]

    while actual_monday != semester_begin[5]:
        table_data += [[str(actual_monday[0]) + "/" + str(actual_monday[1])] + 20*[""]]
        actual_monday = add_one_week(actual_monday)

    style = TableStyle(
        [
            ("FONTNAME", (0, 0), (-1, -1), "Times-Bold"),
            ('FONTSIZE', (1, 1), (-1, -1), 5.5),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("ALIGN", (1, 0), (-1, -1), "LEFT"),
            ("ALIGN", (0, 1), (0, -1), "CENTER"),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("LINEABOVE", (0, 0), (-1, 0), 1, colors.black),
            ("LINEABOVE", (0, 0), (0, -1), 1, colors.black),
            ("LINEBELOW", (0, 0), (-1, -1), 1, colors.black),
            ("LINEBELOW", (0, 0), (0, -1), 1, colors.black),
            ("LINEAFTER", (0, 0), (0, -1), 1, colors.black),
            #("LINEAFTER", (0, 0), (-1, 0), 1, colors.black),
            ("BACKGROUND", (1, 1), (-1, -1), colors.whitesmoke),
        ]
    )

    for i in range(1,5):
<<<<<<< HEAD
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
=======
        style.add("LINEAFTER", (4*i, 0), (4*i, -1), 1, colors.black,)

    for course in courses:
        for sem in semester_to_int[course["semester"]]:
            add_course(course, table_data, sem)

    course_color = {}

    for i in range(1, len(table_data)):
        for j in range(1, len(table_data[0])):
            if table_data[i][j] != "":
                if not table_data[i][j] in course_color:
                    course_color[table_data[i][j]] = colors.Color(red=0.5 + 0.5*rd.random(), green=0.5 + 0.5*rd.random(), blue=rd.random())
                style.add("BACKGROUND", (j, i), (j, i), course_color[table_data[i][j]],)


    for key in pedagogic_day:
        weeks, days = find_day_and_week(pedagogic_day[key])
        style.add("BACKGROUND", (4*(days) + 1, weeks), (4*(days)+4, weeks), colors.Color(red=1, blue =0.25, green = 0.25),)
        for i in range(1,5):
            table_data[weeks][4*days+i] = ""
        table_data[weeks][4*days+1] = "JOURNÉE PÉDAGOGIQUE"

    write_specil_week(vacation, table_data, style, colors.lightgrey)
    write_specil_week(ouverture_week, table_data, style,colors.Color(blue = 1, green = 0.85, red = 0.25))






    table = Table(table_data, colWidths=27, rowHeights=18)
>>>>>>> migration-info

    table.setStyle(style)

    elements.append(table)
