# Generated by Django 4.2.6 on 2024-06-06 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0016_parcours_elective_text_parcours_mandatory_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='parcours',
            name='academic_base_ects',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='parcours',
            name='base_ects',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
