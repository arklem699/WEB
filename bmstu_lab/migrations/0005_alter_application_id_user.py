# Generated by Django 4.2.4 on 2023-10-21 18:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bmstu_lab', '0004_alter_appointment_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='id_user',
            field=models.ForeignKey(db_column='id_user', on_delete=django.db.models.deletion.CASCADE, to='bmstu_lab.students', unique=True),
        ),
    ]
