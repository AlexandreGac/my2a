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

from .models import Course, Department, Parcours, Student, SpecialDay, YearInformation

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
            print("Ok")
            # Check if course with the same code already exists
            if Course.objects.filter(code=code).exists():
                print("------ " + f"Course with code {code} already exists")
                error_rows.append([row["code"], "Un cours avec ce code existe déjà"])
                continue

            name = row["name"]
            department_code = row[
                "department"
            ]
            ects = row["ects"]
            description = row["description"]
            teacher = row["teacher"]
            day = row["day"]

            # Si day est un nombre, on utilise des valeurs par défaut pour semester et les horaires
            if day.isdigit():
                print("------ " + f"Day {day} is a number, using default values")
                semester = "S3"  # Valeur par défaut "S3"
                start_time = "8:00"  # Valeur par défaut "8:00"
                end_time = "17:00"  # Valeur par défaut "17:00"
            else:
                print
                semester = row["semester"]
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

            if semester not in ["S3", "S4", "S3A", "S3B", "S4A", "S4B","S5", "S5A", "S5B", "S6", "S6A", "S6B"]:
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
                "S5": Course.Semester.S5,
                "S5A": Course.Semester.S5A,
                "S5B": Course.Semester.S5B,
                "S6": Course.Semester.S6,
                "S6A": Course.Semester.S6A,
                "S6B": Course.Semester.S6B,
            }
            semester = semester_mapping.get(semester)

            if (day not in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]) and not day.isdigit():
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

            """
            # Match day name to day value
            day_mapping = {
                "Lundi": Course.Day.LUN,
                "Mardi": Course.Day.MAR,
                "Mercredi": Course.Day.MER,
                "Jeudi": Course.Day.JEU,
                "Vendredi": Course.Day.VEN,
            }

            day = day_mapping.get(day)
            """

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


def importSpecialDayCSV(csv_file, replace=False):
    print("--- Reading CSV file for Special Days...")
    
    # Si le flag replace est True, supprimer tous les anciens jours spéciaux
    if replace:
        print("--- Replace flag activé : suppression des anciens jours spéciaux")
        SpecialDay.objects.all().delete()
    
    csv_file_wrapper = TextIOWrapper(csv_file.file, encoding="utf-8-sig")
    csv_reader = csv.DictReader(csv_file_wrapper, delimiter=";")

    error_rows = []
    created_rows = []

    print("--- Création des jours spéciaux:")
    for row in csv_reader:
        print(row)
        try:
            name = row["name"]
            date_str = row["date"]

            # Validation du format de la date
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                print(f"------ La date {date_str} n'est pas valide")
                error_rows.append(
                    [name, "Mauvais format de date. Veuillez utiliser 'AAAA-MM-JJ'."]
                )
                continue

            # Si replace n'est pas activé, on vérifie si un jour spécial identique existe déjà
            if not replace and SpecialDay.objects.filter(name=name, date=date).exists():
                print(f"------ Le jour spécial {name} du {date} existe déjà")
                error_rows.append([name, f"Le jour spécial '{name}' le '{date}' existe déjà."])
                continue

            # Création et sauvegarde de l'objet SpecialDay
            special_day = SpecialDay(name=name, date=date)
            special_day.save()

            created_rows.append(name)
            print(f"------ Le jour spécial {special_day} a été créé")

        except Exception as e:
            print(f"------ Erreur : {e}")
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
            year = row["year"]

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
                """if email.split("@")[1] != "eleves.enpc.fr":
                    print("------ " + f"Sending email to {email}")
                    send_account_creation_mail.delay(email, name, surname, password)"""

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
                year=year,
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


def send_account_created_mails():
    """
       Identifies students who have accounts and are 'editable', implying they are new
       or pending setup, and triggers sending them an account creation email.
       For non-'@eleves.enpc.fr' emails, it generates a new password and includes it.
       Returns a summary of actions: count of emails sent, skipped, and any errors.
    """

    students_to_potentially_email = Student.objects.filter(user__isnull=False, editable=True)

    sent_count = 0
    skipped_enpc_domain = 0  # Count students skipped due to @eleves.enpc.fr domain
    errors = []

    if not students_to_potentially_email.exists():
        return {
            "sent_count": 0,
            "skipped_enpc_domain": 0,
            "errors": [],
            "message": "No students found matching criteria (user exists and student is editable)."
        }

    for student in students_to_potentially_email:
        user = None  # Initialize user to None for robust error reporting
        try:
            user = student.user
            if not user.email:  # Should ideally not happen if email is part of user creation
                errors.append({
                    "student_id": student.id,
                    "student_name": f"{student.name} {student.surname}",
                    "error": "User account exists but has no email address."
                })
                continue

            # Check email domain condition from importStudentCSV's commented email section
            email_parts = user.email.split("@")
            if len(email_parts) == 2 and email_parts[1] == "eleves.enpc.fr":
                # Consistent with importStudentCSV, skip sending this specific email
                # to @eleves.enpc.fr addresses.
                # Their passwords, if set by importStudentCSV, remain untouched by this function.
                skipped_enpc_domain += 1
                continue

                # For other email domains, generate a new random password.
            # This overwrites any previous password for the user.
            # Necessary because the original plaintext password (if any) is not stored.
            new_password = User.objects.make_random_password(length=12)  # Using a reasonable length
            user.set_password(new_password)
            user.save()  # Save the user with the new password hash

            # Send the email with the new password using the imported Celery task.
            # Assumes send_account_creation_mail is a Celery task and handles .delay()
            send_account_creation_mail.delay(
                user.email,  # email (positional argument 1)
                student.name,  # name (positional argument 2)
                student.surname,  # surname (positional argument 3)
                new_password  # password (positional argument 4)
            )

            sent_count += 1

            # OPTIONAL/RECOMMENDED IMPROVEMENT:
            # To prevent re-sending emails to the same students if this function is called again,
            # you would ideally set a flag on the Student model here. E.g.:
            # student.account_creation_email_sent = True
            # student.save(update_fields=['account_creation_email_sent'])
            # This requires adding `account_creation_email_sent = models.BooleanField(default=False)`
            # to the Student model in `models.py`.

        except Exception as e:
            # Log full error for server-side debugging if a logger is configured
            # import logging
            # logger = logging.getLogger(__name__)
            # logger.error(f"Error processing student {student.id} ({student.name} {student.surname}): {e}", exc_info=True)
            errors.append({
                "student_id": student.id,
                "student_name": f"{student.name} {student.surname}",
                "user_email": user.email if user and hasattr(user, 'email') else "N/A",
                "error": str(e)
            })

    return {
        "sent_count": sent_count,
        "skipped_enpc_domain": skipped_enpc_domain,
        "errors": errors
    }