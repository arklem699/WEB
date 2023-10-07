# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AppApp(models.Model):
    id_appl = models.ForeignKey('Application', models.CASCADE, db_column='id_appl')
    id_appoint = models.ForeignKey('Appointment', models.CASCADE, db_column='id_appoint')

    class Meta:
        managed = True
        db_table = 'app_app'


class Application(models.Model):
    id_user = models.ForeignKey('Students', models.CASCADE, db_column='id_user')
    date_creating = models.DateField(blank=True, null=True)
    date_formation = models.DateField(blank=True, null=True)
    date_completion = models.DateField(blank=True, null=True)
    moderator = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'application'


class Appointment(models.Model):
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    doctor = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'appointment'


class Students(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    student_group = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'students'