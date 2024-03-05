from rest_framework import serializers

from .models import Course, Department, Enrollment, Parcours, Student


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "id",
            "user",
            "name",
            "surname",
            "department",
            "parcours",
            "editable",
            "is_admin",
            "has_logged_in",
        ]

    is_admin = serializers.SerializerMethodField()
    has_logged_in = serializers.SerializerMethodField()

    def get_is_admin(self, obj):
        return obj.user.is_superuser

    def get_has_logged_in(self, obj):
        return obj.user.last_login is not None


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            # Info pour la scolarité
            "code",
            "department",
            "ects",
            # Info détails
            "description",
            "teacher",
            # Info sur l'horaire
            "semester",
            "day",
            "start_time",
            "end_time",
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student",
            "course",
            "category",
        ]

    course = CourseSerializer()


class CompleteStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "id",
            "user",
            "name",
            "surname",
            "department",
            "parcours",
            "ects",
            "mandatory_courses",
            "elective_courses",
            "editable",
            "has_logged_in",
        ]

    mandatory_courses = EnrollmentSerializer(many=True)
    elective_courses = EnrollmentSerializer(many=True)
    ects = serializers.SerializerMethodField()
    has_logged_in = serializers.SerializerMethodField()

    def get_ects(self, obj):
        return obj.count_ects()

    def get_has_logged_in(self, obj):
        return obj.user.last_login is not None


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = [
            "id",
            "name",
            "code",
            "responsable",
        ]


class ParcoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcours
        fields = [
            "id",
            "name",
            "department",
            "description",
            "courses_mandatory",
            "courses_on_list",
        ]

    department = DepartmentSerializer()
    courses_mandatory = CourseSerializer(many=True)
    courses_on_list = CourseSerializer(many=True)
