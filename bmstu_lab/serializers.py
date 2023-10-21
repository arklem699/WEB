from bmstu_lab.models import AppApp, Application, Appointment
from rest_framework import serializers


class AppAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppApp
        fields = '__all__'

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'