import csv
import io
from textwrap import wrap

from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from django.db.models import Q
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, ViewSet
import json

from .admin import CourseAdmin
from my2a.mail import send_confirmation_mail, send_account_status_change_mail
from .models import Course, Department, Enrollment, Parcours, Student, Parameter, SpecialDay, YearInformation
from .serializers import (
    CompleteStudentSerializer,
    CourseSerializer,
    SpecialDaySerializer,
    DepartmentSerializer,
    EnrollmentSerializer,
    ParcoursSerializer,
    StudentSerializer,
    ParameterSerializer,
)
from .utils import course_list_to_string, importCourseCSV, importStudentCSV, importSpecialDayCSV


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def auth_view(request):
    if request.method == "GET":
        if request.user.is_authenticated and request.user.is_superuser:
            return redirect("/inspector/")
        elif request.user.is_authenticated:
            return redirect("/")
        return render(request, "registration/login.html")
    username = request.POST.get("mail", "")
    password = request.POST.get("password", "")
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            auth.login(request, user)
            if user.is_superuser:
                return redirect("/inspector/")
            return redirect("/")

    else:
        return render(
            request,
            "registration/login.html",
            {"error": "Mauvaise adresse email ou mot de passe"},
        )


class TranslationView(APIView):
    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        department = [department.code for department in Department.objects.all()]
        parcours = [parcours.name for parcours in Parcours.objects.all()]
        response = {"departments": {}, "parcours": {}}
        for department in Department.objects.all(): 
            response["departments"][department.id] = department.name
        for parcours in Parcours.objects.all():
            response["parcours"][parcours.id] = parcours.name
        return Response(response)


class StudentViewset(ReadOnlyModelViewSet):
    """
    A viewset for retrieving Student objects.

    This viewset allows for retrieving all Student objects, one in particular.
    """

    # Example:
    # /api/student/ (all contacts)
    # /api/student/4/ (contact with id 4)

    serializer_class = StudentSerializer

    @permission_classes([IsAdminUser])
    def get_queryset(self):
        """
        Returns a queryset of all Student objects.
        """

        queryset = Student.objects.all()
        if "department" in self.request.GET:
            queryset = queryset.filter(department__pk=self.request.GET["department"])
        return queryset

    @permission_classes([IsAdminUser])
    def retrieve(self, request, pk=None):
        """
        Returns a queryset of all Student objects.
        """
        student = get_object_or_404(Student, id=pk)
        serializer = CompleteStudentSerializer(student)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def search(self, request):
        students = Student.objects.filter(surname__contains=request.GET["search"])
        if "department" in request.GET:
            students = students.filter(department__pk=request.GET["department"])
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def current(self, request):
        """
        Returns the current user.
        """
        student = get_object_or_404(Student, user=request.user)
        serializer = StudentSerializer(student)
        response = Response(serializer.data)
        response.set_cookie("student_id", student.id)
        return response

    # Return all data of the current user (dep, parcours, courses)
    @action(detail=False, methods=["get"], url_path="current/id")
    def get_current_id(self, request):
        student = get_object_or_404(Student, user=request.user)
        serializer = CompleteStudentSerializer(student)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        url_path="current/department",
        permission_classes=[IsAdminUser],
    )
    def set_department(self, request):
        """
        Set current user department.
        """
        student = get_object_or_404(Student, user=request.user)
        if not student.editable:
            return Response({"error": "student_not_editable"})
        department = get_object_or_404(Department, id=request.data["department"])
        student.department = department
        student.parcours = None
        student.save()
        serializer = StudentSerializer(student)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="current/parcours")
    def set_parcours(self, request):
        """
        Set current user parcours.
        """
        student = get_object_or_404(Student, user=request.user)
        if not student.editable:
            return Response({"error": "student_not_editable"})
        parcours = get_object_or_404(Parcours, id=request.data["parcours"])
        student.parcours = parcours
        student.save()
        enrollment = Enrollment.objects.filter(student=student)
        enrollment.delete()
        serializer = StudentSerializer(student)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="current/enroll")
    def update_course_choice(self, request):
        """
        Update the course choice of the current user.
        """
        student = get_object_or_404(Student, user=request.user)
        if not student.editable:
            return Response({"error": "student_not_editable"})
        if request.data["is_enrolled"]:
            course = get_object_or_404(Course, name=request.data["course"])
            if Enrollment.objects.filter(student=student, course=course).exists():
                return Response({"status": "already enrolled"})
            print(request.data["category"])
            enrollment = Enrollment(
                student=student, course=course, category=request.data["category"]
            )
            enrollment.save()
            serializer = EnrollmentSerializer(enrollment)
            return Response(serializer.data)
        else:
            enrollment = get_object_or_404(
                Enrollment, student=student, course__name=request.data["course"]
            )
            enrollment.delete()
        return Response({"status": "ok"})

    @action(detail=False, methods=["get"], url_path="current/courses/available")
    def get_available_courses(self, request):
        """
        Return the available courses for the current user.
        """
        student = get_object_or_404(Student, user=request.user)
        if student.parcours is None:
            return Response([])
        courses = student.check_time_table()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    @action(
        detail=False, methods=["get"], url_path="current/courses/available_electives"
    )
    def get_not_enrolled_courses(self, request):
        """
        Return the courses not enrolled by the current user.
        """
        student = get_object_or_404(Student, user=request.user)
        if student.parcours is None:
            return Response([])
        courses = (
            Course.objects.all().order_by("code").filter(~Q(department__code="SHS"))
        )
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="current/timetable")
    def get_timetable(self, request):
        student = get_object_or_404(Student, user=request.user)
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "filename=timetable.pdf"
        response.write(student.generate_timetable())
        return response

    @action(detail=False, methods=["post"], url_path="updatestatus")
    def change_status(self, request):
        # check if user is admin or is self
        student = get_object_or_404(Student, user=request.user)
        if "id" in request.data and student.user.is_superuser:
            target_student = get_object_or_404(Student, id=request.data["id"])
            target_student.editable = not target_student.editable
            target_student.save()
            if target_student.editable:
                send_account_status_change_mail(
                    target_student.user.email, target_student.name, target_student.surname
                )
            return Response({"status": "ok"})
        elif "id" not in request.data:
            if (
                student.editable
                and student.department is not None
                and student.parcours is not None
            ):
                if "comment" in request.data:
                    student.comment = request.data["comment"]
                student.editable = False
                send_confirmation_mail.delay(student.id)
                student.save()
                return Response({"status": "ok"})
        return Response({"status": "error"})


class CourseViewset(ReadOnlyModelViewSet):
    """
    A viewset for retrieving Course objects.

    This viewset allows for retrieving all Course objects, one in particular.
    We can also filter by department, semester and day.
    """

    # Example:
    # /api/course/ (all contacts)
    # /api/course/4/ (contact with id 4)
    # /api/course/?departement=IMI (all IMI courses)
    # /api/course/?semester=S3
    # /api/course/?day=Lundi
    # (all course mandatory for Vision Aprentissage parcours)
    # /api/course/?parcours=1&mandatory=1

    serializer_class = CourseSerializer

    def get_queryset(self):
        """
        Returns a queryset of all Course objects.
        """

        queryset = Course.objects.all()
        # get parameters from request
        dpt = self.request.GET.get("department")
        sem = self.request.GET.get("semester")
        day = self.request.GET.get("day")
        parcours = self.request.GET.get("parcours")
        mandatory = self.request.GET.get("mandatory")
        onList = self.request.GET.get("on_list")
        # filter by dpt
        if dpt is not None:
            queryset = queryset.filter(department__pk=dpt)
        # filter by sem
        if sem is not None:
            queryset = queryset.filter(semester=sem)
        # filter by day
        if day is not None:
            queryset = queryset.filter(day=day)

        # filter by parcours
        if parcours is not None:
            parcours_obj = Parcours.objects.get(id=parcours)
            if mandatory is not None:
                queryset = parcours_obj.courses_mandatory.all()
            elif onList is not None:
                queryset = parcours_obj.courses_on_list.all()
            else:
                # return everything
                queryset = queryset.union(
                    parcours_obj.courses_mandatory.all(),
                    parcours_obj.courses_on_list.all(),
                )

        return queryset.order_by("name")

    @action(detail=False, methods=["delete"])
    def delete(self, request):
        course = get_object_or_404(Course, id=request.data["id"])
        dep_pk = course.department.pk
        course.delete()
        return Response(
            CourseSerializer(
                Course.objects.filter(department__pk=dep_pk), many=True
            ).data
        )


class DepartmentViewset(ReadOnlyModelViewSet):
    """
    A viewset for retrieving Department objects.

    This viewset allows for retrieving all Department objects, one in particular.
    """

    # Example:
    # /api/department/ (all contacts)
    # /api/department/4/ (contact with id 4)
    # /api/department/?code=IMI (The IMI department)

    serializer_class = DepartmentSerializer

    def get_queryset(self):
        """
        Returns a queryset of all Department objects.
        """

        queryset = Department.objects.all()

        code = self.request.GET.get("code")
        if code is not None:
            queryset = queryset.filter(code=code)

        respo = self.request.GET.get("responsable")
        if respo is not None:
            queryset = queryset.filter(responsable=respo)

        return queryset


# create a view to return the parcours of a departement
# api/IMI/parcours

# api/IMI/courses

# api/IMI/VisionApprentissage/courses

# api/IMI/VisionApprentissage/courses/mandatory

# api/IMI/VisionApprentissage/courses/on_list


class EnrollmentViewset(ReadOnlyModelViewSet):
    """
    A viewset for retrieving Enrollment objects.

    This viewset allows for retrieving all Enrollment objects, one in particular.
    """

    # Example:
    # /api/enrollment/ (all contacts)
    # /api/enrollment/4/ (contact with id 4)

    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        """
        Returns a queryset of all Enrollment objects.
        """

        queryset = Enrollment.objects.all()
        return queryset


class PostEnrollment(APIView):
    """
    API endpoint to select courses
    """

    def post(self, request):
        for course in request.data["courses"]:
            get_object_or_404(Course, name=course)
            student = Student.objects.get(user__id=request.user.id)
            enrollment = Enrollment(student=student, course=course)
            enrollment.save()


class ImportCourseCSV(APIView):
    def post(self, request):
        try:
            csv_file = request.FILES.get("csv_file")
            if csv_file:
                failed, created = importCourseCSV(csv_file)
                if failed:
                    return Response(
                        {
                            "success": True,
                            "error": "Some rows failed to import",
                            "failed": failed,
                            "created": created,
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {
                            "success": True,
                            "error": "CSV file processed successfully",
                            "failed": failed,
                            "created": created,
                        },
                        status=status.HTTP_200_OK,
                    )
            else:
                return Response(
                    {"success": False, "error": "No CSV file provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ImportSpecialDayCSV(APIView):
    def post(self, request):
        try:
            csv_file = request.FILES.get("csv_file")
            # Récupération du paramètre "replace" depuis le formulaire, par défaut "false"
            replace_flag = request.POST.get("replace", "false").lower() == "true"

            if csv_file:
                # Transmet le flag à la fonction d'import pour réaliser le remplacement
                failed, created = importSpecialDayCSV(csv_file, replace=replace_flag)
                if failed:
                    return Response(
                        {
                            "success": True,
                            "error": "Certaines lignes n'ont pas pu être importées",
                            "failed": failed,
                            "created": created,
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {
                            "success": True,
                            "error": "Fichier CSV traité avec succès",
                            "failed": failed,
                            "created": created,
                        },
                        status=status.HTTP_200_OK,
                    )
            else:
                return Response(
                    {"success": False, "error": "Aucun fichier CSV fourni"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class ImportStudentCSV(APIView):
    def post(self, request):
        try:
            csv_file = request.FILES.get("csv_file")
            if csv_file:
                failed, created = importStudentCSV(csv_file)
                if failed:
                    return Response(
                        {
                            "success": True,
                            "error": "Some rows failed to import",
                            "failed": failed,
                            "created": created,
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {
                            "success": True,
                            "error": "CSV file processed successfully",
                            "failed": failed,
                            "created": created,
                        },
                        status=status.HTTP_200_OK,
                    )
            else:
                return Response(
                    {"success": False, "error": "No CSV file provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ViewContractPDF(APIView):
    def get(self, request, id=None):
        user = request.user
        if not user.is_superuser:
            return Response({"status": "error", "message": "not authorized"})
        student = get_object_or_404(Student, id=id)
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        textobject = p.beginText(2 * cm, 29.7 * cm - 2 * cm)
        textobject.textLine(
            "Contrat de formation de " + student.name + " " + student.surname
        )
        textobject.textLine(" ")
        textobject.textLine("Département: " + student.department.code)
        textobject.textLine("Parcours: " + student.parcours.name)
        textobject.textLine("Nombres d'ECTS: " + str(student.count_ects()))
        textobject.textLine(" ")
        if student.parcours is not None:
            textobject.textLine("Liste des cours:")
            textobject.textLine(" ")
            textobject.textLine("Obligatoire parcours:")
            for course in student.parcours.courses_mandatory.all():
                wraped_text = "\n".join(
                    wrap(
                        course.name
                        + " - "
                        + course.semester
                        + " - "
                        + str(course.ects)
                        + " ECTS",
                        80,
                    )
                )
                textobject.textLines(wraped_text)

            textobject.textLine(" ")
            textobject.textLine("Obligatoire sur liste:")
            for enrollment in student.mandatory_courses():
                wraped_text = "\n".join(
                    wrap(
                        enrollment.course.name
                        + " - "
                        + enrollment.course.semester
                        + " - "
                        + str(enrollment.course.ects)
                        + " ECTS",
                        80,
                    )
                )
                textobject.textLine(wraped_text)
            textobject.textLine(" ")
            textobject.textLine("Cours électifs: ")
            for enrollment in student.elective_courses():
                wraped_text = "\n".join(
                    wrap(
                        enrollment.course.name
                        + " - "
                        + enrollment.course.semester
                        + " - "
                        + str(enrollment.course.ects)
                        + " ECTS",
                        80,
                    )
                )
                textobject.textLines(wraped_text)
        else:
            textobject.textLine("Pas de parcours sélectionné par l'étudiant")
        textobject.textLine(" ")
        p.drawText(textobject)
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(
            buffer, filename="contrat" + student.name + "_" + student.surname + ".pdf"
        )


class ExportStudentsView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="etudiants.csv"'},
        )
        response.write("\ufeff".encode("utf8"))
        writer = csv.writer(response, delimiter=";")
        writer.writerow(
            [
                "Prénom",
                "Nom",
                "Département",
                "Parcours",
                "Cours obligatoires sur liste",
                "Cours électifs",
                "Total ECTS",
                "Commentaire",
            ]
        )
        students = Student.objects.all().filter(editable=False)
        if "dep" in request.GET:
            students = students.filter(department__pk=request.GET["dep"])
            print(students)
        for student in students:
            writer.writerow(
                [
                    student.name,
                    student.surname,
                    student.department,
                    student.parcours,
                    course_list_to_string(student.mandatory_courses()),
                    course_list_to_string(student.elective_courses()),
                    student.count_ects(),
                    student.comment,
                ]
            )
        return response


class ParcoursViewset(ViewSet):

    permission_classes = [IsAuthenticated]

    def list(self, request):
        if "department" not in request.GET:
            return Response({"error": "department not provided"}, status=400)
        department = get_object_or_404(Department, pk=request.GET["department"])
        parcours = Parcours.objects.filter(department=department).order_by("name")
        serializer = ParcoursSerializer(parcours, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsAdminUser])
    def mandatory(self, request):
        if "parcours" not in request.GET:
            return Response({"error": "parcours not provided"}, status=400)
        parcours = get_object_or_404(Parcours, pk=request.GET["parcours"])
        mandatory_courses = parcours.courses_mandatory.all().order_by("name")
        serializer = CourseSerializer(mandatory_courses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[IsAdminUser])
    def add_course(self, request):
        if "type" not in request.data:
            return Response({"error": "type not provided"}, status=400)
        type = request.data["type"]
        if "parcours" not in request.data:
            return Response({"error": "parcours not provided"}, status=400)
        parcours = get_object_or_404(Parcours, pk=request.data["parcours"])
        if "course" not in request.data:
            return Response({"error": "course not provided"}, status=400)
        course = get_object_or_404(Course, pk=request.data["course"])
        courses = []
        if type == "mandatory":
            parcours.courses_mandatory.add(course)
            parcours.save()
            courses = parcours.courses_mandatory.all().order_by("name")
        elif type == "on_list":
            parcours.courses_on_list.add(course)
            parcours.save()
            courses = parcours.courses_on_list.all().order_by("name")
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[IsAdminUser])
    def remove_course(self, request):
        if "type" not in request.data:
            return Response({"error": "type not provided"}, status=400)
        type = request.data["type"]
        if "parcours" not in request.data:
            return Response({"error": "parcours not provided"}, status=400)
        parcours = get_object_or_404(Parcours, pk=request.data["parcours"])
        if "course" not in request.data:
            return Response({"error": "course not provided"}, status=400)
        course = get_object_or_404(Course, pk=request.data["course"])
        courses = []
        if type == "mandatory":
            parcours.courses_mandatory.remove(course)
            parcours.save()
            courses = parcours.courses_mandatory.all().order_by("name")
        elif type == "on_list":
            parcours.courses_on_list.remove(course)
            parcours.save()
            courses = parcours.courses_on_list.all().order_by("name")
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsAdminUser])
    def avalaible_mandatory(self, request):
        if "department" not in request.GET:
            return Response({"error": "department not provided"}, status=400)
        department = get_object_or_404(Department, pk=request.GET["department"])
        if "parcours" not in request.GET:
            return Response({"error": "parcours not provided"}, status=400)
        parcours = get_object_or_404(Parcours, pk=request.GET["parcours"])
        courses = (
            Course.objects.filter(department=department)
            .exclude(id__in=parcours.courses_mandatory.all())
            .order_by("name")
        )
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)


class ParameterView(APIView):
    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        parameters = Parameter.objects.filter(show=True)
        serializer = ParameterSerializer(parameters, many=True)
        return Response(serializer.data)
    

class ModifyYearInformations(View):
    def get(self, request, *args, **kwargs):
        try:
            year_info = YearInformation.objects.first()
            if year_info:
                data = {
                    "start_of_the_school_year": year_info.start_of_the_school_year,
                    "start_of_S3B": year_info.start_of_S3B,
                    "start_of_S4A": year_info.start_of_S4A,
                    "start_of_S4B": year_info.start_of_S4B,
                    "end_of_school_year": year_info.end_of_school_year,
                    "monday_of_autumn_holiday": year_info.monday_of_autumn_holiday,
                    "monday_of_xmas_holiday": year_info.monday_of_xmas_holiday,
                    "monday_of_winter_holiday": year_info.monday_of_winter_holiday,
                    "monday_of_spring_holiday": year_info.monday_of_spring_holiday,
                    "easter_monday": year_info.easter_monday,
                    "ascension_day": year_info.ascension_day,
                    "whit_monday": year_info.whit_monday,
                }
                return JsonResponse(data)
            else:
                return JsonResponse({"error": "No year information found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            year_info, created = YearInformation.objects.get_or_create(pk=1)
            year_info.start_of_the_school_year = data.get("start_of_the_school_year")
            year_info.start_of_S3B = data.get("start_of_S3B")
            year_info.start_of_S4A = data.get("start_of_S4A")
            year_info.start_of_S4B = data.get("start_of_S4B")
            year_info.end_of_school_year = data.get("end_of_school_year")
            year_info.monday_of_autumn_holiday = data.get("monday_of_autumn_holiday")
            year_info.monday_of_xmas_holiday = data.get("monday_of_xmas_holiday")
            year_info.monday_of_winter_holiday = data.get("monday_of_winter_holiday")
            year_info.monday_of_spring_holiday = data.get("monday_of_spring_holiday")
            year_info.easter_monday = data.get("easter_monday")
            year_info.ascension_day = data.get("ascension_day")
            year_info.whit_monday = data.get("whit_monday")
            year_info.save()
            return JsonResponse({"success": "Year information updated successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

