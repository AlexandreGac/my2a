from django.contrib import admin

from .models import Course, Department, Enrollment, Parameter, Parcours, Student, YearInformation, SpecialDay


class StudentAdmin(admin.ModelAdmin):
    search_fields = [
        "surname",
        "name",
        "department__name",
        "parcours__name",
        "editable",
    ]
    list_filter = ["department", "parcours", "editable"]
    list_display = ["surname", "name", "department", "parcours", "editable"]


class CourseAdmin(admin.ModelAdmin):
    search_fields = ["name", "code", "department__name"]
    list_filter = ["department", "semester", "day"]
    list_display = ["name", "code", "department"]


class Opening_WeekAdmin(admin.ModelAdmin):
    search_fields = ["name", "code", "department__name"]
    list_filter = ["department", "semester", "week"]
    list_display = ["name", "code", "department"]


class ParcoursAdmin(admin.ModelAdmin):
    search_fields = ["name", "department__name"]
    list_filter = ["department"]
    list_display = ["name", "department"]


class EnrollmentAdmin(admin.ModelAdmin):
    search_fields = ["student__surname", "student__name", "course__name", "category"]
    list_filter = ["student", "course", "category"]
    list_display = ["student", "course", "category"]


class DepartmentAdmin(admin.ModelAdmin):
    search_fields = ["code", "name"]
    list_display = ["code", "name", "responsable"]


admin.site.register(Student, StudentAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(Parcours, ParcoursAdmin)
admin.site.register(Parameter)
admin.site.register(YearInformation)
admin.site.register(SpecialDay)
