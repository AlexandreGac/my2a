# Generated by Django 4.2.6 on 2023-11-27 15:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("education", "0003_rename_ects_course__ects"),
    ]

    operations = [
        migrations.CreateModel(
            name="Department",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("code", models.CharField(max_length=4)),
                (
                    "responsable",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.RemoveField(
            model_name="course",
            name="parcours",
        ),
        migrations.AddField(
            model_name="student",
            name="user",
            field=models.OneToOneField(
                default=0,
                on_delete=django.db.models.deletion.PROTECT,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="course",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="student",
            name="parcours",
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
        migrations.CreateModel(
            name="Parcours",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "courses_mandatory",
                    models.ManyToManyField(
                        blank=True,
                        related_name="mandatory_parcours",
                        to="education.course",
                    ),
                ),
                (
                    "courses_on_list",
                    models.ManyToManyField(
                        blank=True,
                        related_name="on_list_parcours",
                        to="education.course",
                    ),
                ),
                (
                    "department",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="education.department",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "parcours",
            },
        ),
        migrations.AlterField(
            model_name="course",
            name="department",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to="education.department"
            ),
        ),
        migrations.AlterField(
            model_name="student",
            name="department",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="education.department",
            ),
        ),
    ]
