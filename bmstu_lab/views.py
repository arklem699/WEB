from django.shortcuts import render
from datetime import datetime
from bmstu_lab.models import Appointment, Application, AppApp, Students


def GetAppointments(request):
    return render(request, 'appointments.html', {'data' : Appointment.objects.all() })


def GetAppointment(request, id):
    new_application = Application.objects.create(
        date_creating = datetime.today(),
        status = 'Введён'
    )
    new_application.save()

    new_appapp = AppApp.objects.create(
        id_appl = Application.objects.latest('id'),
        id_appoint = Appointment.objects.get(id=id)
    )
    new_appapp.save()

    new_students = Students.objects.create(
        id_appl = Application.objects.latest('id'),
        name = 'user',
        student_group = 'group'
    )
    new_students.save()

    return render(request, 'appointment.html', {'data': Appointment.objects.get(id=id)})


def GetQuery(request):
    query = request.GET.get('query', '')
    query_date = datetime.strptime(query, '%d.%m.%Y').strftime('%Y-%m-%d')
    new_data = Appointment.objects.filter(date=query_date)
    return render(request, 'appointments.html', {'data': new_data})