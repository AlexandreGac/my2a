from django.contrib.auth import models as models2
from django.contrib.auth.models import User
from django.db import models
from solo.models import SingletonModel
from django.utils import timezone

from .exportpdf import generate_pdf_from_courses


class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=4)
    # Responsable est un admin qui peut gérer les cours du départment (un user)
    responsable = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True
    )
    description = models.TextField(null=True, blank=True)
    timetable_intro = models.TextField(null=True, blank=True, default="")
    end_comment = models.TextField(null=True, blank=True, default="Attention: Cette action est irréversible. Aucun changement ultérieur ne pourra être effectué sauf en cas de demande auprès de ton responsable de département.")

    def __str__(self):
        return self.code


class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)

    class Semester(models.TextChoices):
        S3 = "S3"
        S4 = "S4"
        # Ajoute les demi-semestres
        S3A = "S3A"
        S3B = "S3B"
        S4A = "S4A"
        S4B = "S4B"

    semester = models.CharField(max_length=10, choices=Semester.choices)

    class Day(models.TextChoices):
        LUN = "Lundi"
        MAR = "Mardi"
        MER = "Mercredi"
        JEU = "Jeudi"
        VEN = "Vendredi"

    day = models.CharField(max_length=10, choices=Day.choices)

    # horaire de début et de fin - format hh:mm (24h) France
    start_time = models.TimeField()
    end_time = models.TimeField()

    ects = models.FloatField()

    teacher = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.code


class Parcours(models.Model):
    """
    Represents a specific educational program or curriculum.
    """

    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    mandatory_text = models.TextField(null=True, blank=True)
    elective_text = models.TextField(null=True, blank=True)
    base_ects = models.FloatField()
    academic_base_ects = models.FloatField()
    courses_mandatory = models.ManyToManyField(
        Course, blank=True, related_name="mandatory_parcours"
    )  # ajouter les cours du tronc commun dedans
    courses_on_list = models.ManyToManyField(
        Course, blank=True, related_name="on_list_parcours"
    )

    class Meta:
        verbose_name_plural = "parcours"

    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(models2.User(), on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    parcours = models.ForeignKey(
        Parcours, on_delete=models.CASCADE, null=True, blank=True
    )
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True, blank=True
    )
    editable = models.BooleanField()
    comment = models.TextField(null=True, blank=True)

    def mandatory_courses(self):
        """Return the list of mandatory courses for the student."""
        return Enrollment.objects.filter(student=self, category="mandatory")

    def elective_courses(self):
        """Return the list of elective courses for the student."""
        return Enrollment.objects.filter(student=self, category="elective")

    def check_time_table(self):
        """Return the list of compatible courses for the student."""
        student_courses = [
            e.course for e in Enrollment.objects.filter(student=self)
        ] + [course for course in self.parcours.courses_mandatory.all()]
        compatible_courses = []
        incompatible_courses = []
        courses = Course.objects.all()
        if len(student_courses) == 0:
            compatible_courses = courses
            return compatible_courses
        for course in courses:
            for s_courses in student_courses:
                min_start = min(s_courses.start_time, course.start_time)
                max_start = max(s_courses.start_time, course.start_time)
                min_end = min(s_courses.end_time, course.end_time)
                # Tri des périodes/semestres
                tiniest_period = max(s_courses.semester, course.semester)
                widest_period = min(s_courses.semester, course.semester)

                # Vérification de la compatibilité des cours
                if (
                        widest_period in tiniest_period
                        and s_courses.day == course.day
                        and min_start <= max_start <= min_end
                ):
                    incompatible_courses.append(course)
                    if course in compatible_courses:
                        compatible_courses.remove(course)
                    break

                if (
                    course not in incompatible_courses
                    and course not in compatible_courses
                ):
                    compatible_courses.append(course)
        return compatible_courses

    def count_ects(self):
        """Return the number of ects the student has."""
        student_courses = Enrollment.objects.filter(student=self)
        ects = 0
        for course in student_courses:
            ects += course.course.ects
        if self.parcours is not None:
            for course in self.parcours.courses_mandatory.all():
                ects += course.ects
        if self.parcours is not None:
            ects += self.parcours.academic_base_ects + self.parcours.base_ects
        return ects

    def check_ects(self):
        """Return True if the student has enough ects, False otherwise."""
        return self.count_ects() >= 39

    def __str__(self):
        return self.name + " " + self.surname

    def generate_timetable(self):
        """Return the timetable of the student."""
        if self.department is None or self.parcours is None:
            return generate_pdf_from_courses(self.name, [], "")
        intro = self.department.timetable_intro
        courses = [
            {
                "name": enrolment.course.name,
                "code": enrolment.course.code,
                "day": enrolment.course.day,
                "start_time": enrolment.course.start_time,
                "end_time": enrolment.course.end_time,
                "semester": enrolment.course.semester,
                "ects": enrolment.course.ects,
                "color": 0 if enrolment.category == "mandatory" else 1,
            }
            for enrolment in Enrollment.objects.filter(student=self)
        ] + [
            {
                "name": course.name,
                "code": course.code,
                "day": course.day,
                "start_time": course.start_time,
                "end_time": course.end_time,
                "semester": course.semester,
                "ects": course.ects,
                "color": 2,
            }
            for course in self.parcours.courses_mandatory.all()
        ]
        return generate_pdf_from_courses(self.name, courses, intro)


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Category(models.TextChoices):
        mandatory = "mandatory"
        elective = "elective"
        visiting = "visiting"

    category = models.CharField(max_length=10, choices=Category.choices)

    def __str__(self):
        return self.student.name + " " + self.course.code


class Parameter(models.Model):
    name = models.CharField(max_length=100)
    value = models.TextField()
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True, blank=True
    )
    show = models.BooleanField(default=True)
    def __str__(self):
        return self.name





class YearInformation(SingletonModel):
    start_of_the_school_year = models.DateField()
    start_of_S4A = models.DateField()
    start_of_S3B = models.DateField()
    start_of_S4A = models.DateField()
    start_of_S4B = models.DateField()
    end_of_school_year = models.DateField()
    monday_of_autumn_holiday = models.DateField()
    moday_of_xmas_holiday = models.DateField()
    monday_of_winter_holiday = models.DateField()
    monday_of_spring_holiday = models.DateField()
    def __str__(self):
        return str(self.start_of_the_school_year)



class SpecialDay(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    date = models.DateField()
    is_public_holiday = models.BooleanField()
    def __str__(self):
        return self.name

