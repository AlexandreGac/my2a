import csv
from io import TextIOWrapper  # Import TextIOWrapper for handling file decoding
from datetime import datetime

from django.contrib import admin
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import path
from django.urls.conf import include

from .models import Course, Department, Parcours, Student, SpecialDay

from my2a.mail import send_account_creation_mail


def importCourseCSV(csv_file):
    print("--- Reading CSV file...")
    csv_file_wrapper = TextIOWrapper(
        csv_file.file, encoding="utf-8-sig"
    )  # Use TextIOWrapper for decoding
    csv_reader = csv.DictReader(csv_file_wrapper, delimiter=";")

    # Create Course objects from passed-in data
    error_rows = []  # List to store rows with errors
    created_rows = []  # List to store rows that were created
    print("--- Creating courses:")
    for row in csv_reader:
        print(row)
        try:
            code = row["code"]

            # Check if course with the same code already exists
            if Course.objects.filter(code=code).exists():
                print("------ " + f"Course with code {code} already exists")
                error_rows.append([row["code"], "Un cours avec ce code existe déjà"])
                continue

            name = row["name"]
            department_code = row[
                "department"
            ]  # Change variable name to department_code
            ects = row["ects"]
            description = row["description"]
            teacher = row["teacher"]
            semester = row["semester"]
            day = row["day"]
            start_time = row["start_time"]
            end_time = row["end_time"]

            # catch : Field 'ects' expected a number but got 'a'.
            try:
                ects = float(ects)
            except ValueError:
                print("------ " + f"Ects {ects} is not a valid number")
                error_rows.append(
                    [
                        row["code"],
                        "Le nombre de crédits '"
                        + ects
                        + "' n'est pas valide. Veuillez utiliser un nombre.",
                    ]
                )
                continue

            # Check if department with the given code exists
            try:
                department = Department.objects.get(code=department_code)
            except Department.DoesNotExist:
                print("------ " + f"Department {department_code} does not exist")
                error_rows.append(
                    [
                        row["code"],
                        "Le département '" + department_code + "' n'existe pas",
                    ]
                )
                continue

            if semester not in ["S3", "S4", "S3A", "S3B", "S4A", "S4B"]:
                print("------ " + f"Semester {semester} does not exist")
                error_rows.append(
                    [
                        row["code"],
                        "Le semestre '"
                        + semester
                        + "' n'existe pas. Veuillez utiliser 'S3', 'S3A', 'S3B', 'S4', 'S4A' ou 'S4B'.",
                    ]
                )
                continue
            # Match semester name to semester value
            semester_mapping = {
                "S3": Course.Semester.S3,
                "S3A": Course.Semester.S3A,
                "S3B": Course.Semester.S3B,
                "S4": Course.Semester.S4,
                "S4A": Course.Semester.S4A,
                "S4B": Course.Semester.S4B,
            }
            semester = semester_mapping.get(semester)

            if day not in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]:
                print("------ " + f"Day {day} does not exist")
                error_rows.append(
                    [
                        row["code"],
                        "Le jour '"
                        + day
                        + "' n'existe pas. Veuillez utiliser 'Lundi', 'Mardi', 'Mercredi', 'Jeudi' ou 'Vendredi'",
                    ]
                )
                continue

            # Match day name to day value
            day_mapping = {
                "Lundi": Course.Day.LUN,
                "Mardi": Course.Day.MAR,
                "Mercredi": Course.Day.MER,
                "Jeudi": Course.Day.JEU,
                "Vendredi": Course.Day.VEN,
            }

            day = day_mapping.get(day)

            # # Catch “AAA” value has an invalid format. It must be in HH:MM[:ss[.uuuuuu]] format.
            # try:
            #     start_time = start_time.split(":")
            #     start_time = int(start_time[0]) * 60 + int(
            #         start_time[1]
            #     )  # Convert start time to minutes
            #     end_time = end_time.split(":")
            #     end_time = int(end_time[0]) * 60 + int(
            #         end_time[1]
            #     )  # Convert end time to minutes

            #     if start_time > end_time:
            #         print(
            #             "------ "
            #             + f"Start time {start_time} is after end time {end_time}"
            #         )
            #         error_rows.append(
            #             [
            #                 row["code"],
            #                 "L'heure de début est après l'heure de fin",
            #             ]
            #         )
            #         continue
            # except Exception as e:
            #     print("------ ", e)
            #     error_rows.append(
            #         [
            #             row["code"],
            #             "L'horaire de début ou de fin n'est pas valide. Veuillez utiliser un format valide (HH:MM)",
            #         ]
            #     )
            #     continue

            course = Course(
                name=name,
                code=code,
                department=department,
                ects=ects,
                description=description,
                teacher=teacher,
                semester=semester,
                day=day,
                start_time=start_time,
                end_time=end_time,
            )
            course.save()

            created_rows.append(row["code"])  # Add row to created list
            print("------ " + f"Course {course} created")

        except Exception as e:
            print(type(e))
            error_rows.append([row["code"], e])  # Add row to error list

    return error_rows, created_rows


def importSpecialDayCSV(csv_file):
    print("--- Reading CSV file for Special Days...")
    csv_file_wrapper = TextIOWrapper(csv_file.file, encoding="utf-8-sig")
    csv_reader = csv.DictReader(csv_file_wrapper, delimiter=";")

    error_rows = []
    created_rows = []

    print("--- Creating special days:")
    for row in csv_reader:
        print(row)
        try:
            name = row["name"]
            date = row["date"]

            # Validate date format
            try:
                date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                print(f"------ Date {date} is not valid")
                error_rows.append(
                    [name, "Mauvais format de date. Veuillez utiliser 'AAAA-MM-JJ'."]
                )
                continue

            # Check if a special day with the same name and date already exists
            if SpecialDay.objects.filter(name=name, date=date).exists():
                print(f"------ Special Day {name} on {date} already exists")
                error_rows.append([name, f"Le jour spécial '{name}' le '{date}' existe déjà."])
                continue

            # Create and save the SpecialDay object
            special_day = SpecialDay(
                name=name,
                date=date,
            )
            special_day.save()

            created_rows.append(name)
            print(f"------ Special Day {special_day} created")

        except Exception as e:
            print(f"------ {e}")
            error_rows.append([name, str(e)])

    return error_rows, created_rows


def importStudentCSV(csv_file):
    print("--- Reading CSV file...")
    csv_file_wrapper = TextIOWrapper(
        csv_file.file, encoding="utf-8-sig"
    )  # Use TextIOWrapper for decoding
    csv_reader = csv.DictReader(csv_file_wrapper, delimiter=";")

    # Create Student objects from passed-in data
    error_rows = []  # List to store rows with errors
    created_rows = []  # List to store rows that were created
    print("--- Creating students:")
    for row in csv_reader:
        print(row)
        try:
            email = row["email"]
            name = row["name"]
            surname = row["surname"]
            department_code = row[
                "department"
            ]  # Change variable name to department_code

            # Create user
            split = email.split("@")
            if split[1] == "eleves.enpc.fr":
                username = email.split("@")[0]
            else:
                username = email
            password = User.objects.make_random_password()
            user, created = User.objects.get_or_create(
                last_name=surname,
                first_name=name,
                username=username,
                email=email,
            )

            if created:
                user.set_password(password)
                user.save()
                print("------ " + f"User {user} created")
                # Send email
                if email.split("@")[1] != "eleves.enpc.fr":
                    print("------ " + f"Sending email to {email}")
                    send_account_creation_mail.delay(email, name, surname, password)

            try:
                department = Department.objects.get(code=department_code)
            except Department.DoesNotExist:
                print("------ " + f"Department {department_code} does not exist")
                error_rows.append(
                    [
                        row["surname"].upper() + " " + row["name"],
                        "Le département '" + department_code + "' n'existe pas",
                    ]
                )
                continue

            if not created and Student.objects.filter(user=user).exists():
                print("------ " + f"Student {user} already exists")
                error_rows.append(
                    [
                        row["surname"].upper() + " " + row["name"],
                        "Un étudiant avec cet email existe déjà",
                    ]
                )
                continue

            Student.objects.create(
                user=user,
                name=name,
                surname=surname,
                department=department,
                editable=True,
            )

            created_rows.append(row["surname"].upper() + " " + row["name"])
            print("------ " + f"Student {user} created")

        except Exception as e:
            print(type(e))
            print(e)
            error_rows.append([row["surname"].upper() + " " + row["name"], e])

    return error_rows, created_rows


def course_list_to_string(course_list):
    text = ""
    for course in course_list:
        text += course.course.name + " "
    if len(text) > 2:
        text = text[:-2]
    return text
