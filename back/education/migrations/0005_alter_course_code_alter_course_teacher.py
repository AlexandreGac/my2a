# Generated by Django 4.2.6 on 2023-11-27 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0004_department_remove_course_parcours_student_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='code',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='course',
            name='teacher',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
