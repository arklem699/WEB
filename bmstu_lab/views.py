from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from bmstu_lab.models import Appointment, Application, AppApp, Students
from bmstu_lab.serializers import AppAppSerializer, ApplicationSerializer, AppointmentSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
import psycopg2
import base64


def GetAppointments(request):
    appointments = Appointment.objects.filter(status='Действует')
    for appointment in appointments:
        if appointment.image:
            appointment.image = base64.b64encode(appointment.image).decode()
    return render(request, 'appointments.html', {'data' : appointments })


def GetAppointment(request, id):
    id_users_str = Application.objects.values_list('id_user', flat=True)
    id_users_int = [int(id_user_str) for id_user_str in id_users_str]
    if Students.objects.latest('id').id not in id_users_int:
        new_application = Application.objects.create(
            id_user = Students.objects.latest('id'),
            date_creating = datetime.today(),
            status = 'Введён'
        )
        new_application.save()

    new_appapp = AppApp.objects.create(
        id_appl = Application.objects.latest('id'),
        id_appoint = Appointment.objects.get(id=id)
    )
    new_appapp.save()

    return render(request, 'appointment.html', {'data': Appointment.objects.get(id=id)})


def GetQuery(request):
    query = request.GET.get('query', '')
    query_date = datetime.strptime(query, '%d.%m.%Y').strftime('%Y-%m-%d')
    new_data = Appointment.objects.filter(date=query_date)
    return render(request, 'appointments.html', {'data': new_data})


def DeleteAppointment(request, id):
    conn = psycopg2.connect(dbname="med_exam", user="dbuser", password="123", port="5432")
    cursor = conn.cursor()
    cursor.execute("UPDATE appointment SET status = 'Удалён' WHERE id = %s", (id,))
    conn.commit()   # реальное выполнение команд sql
    cursor.close()
    conn.close()
    return redirect('/')


@api_view(['Get'])
def get_list_appointment(request, format=None):
    """
    Возвращает список услуг
    """
    appointments = Appointment.objects.all()
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)


@api_view(['Get', 'Post', 'Put', 'Delete'])
def detail_appointment(request, id, format=None):
    appointment = get_object_or_404(Appointment, id=id)
    if request.method == 'GET':
        """
        Возвращает информацию об услуге
        """
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)   
    
    elif request.method == 'POST':    
        """
        Добавляет услугу в последнюю заявку
        """
        new_appapp, created = AppApp.objects.get_or_create(
            id_appl = Application.objects.latest('id'),
            id_appoint = Appointment.objects.get(id=id)
        )
        serializer = AppAppSerializer(new_appapp)
        if created:
            new_appapp.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        """
        Обновляет информацию об услуге
        """
        serializer = AppointmentSerializer(appointment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':    
        """
        Удаляет информацию об услуге
        """
        appointment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['Post'])
def post_list_appoinment(request, format=None):    
    """
    Добавляет новую услугу
    """
    serializer = AppointmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['Get'])
def get_list_application(request, format=None):
    """
    Возвращает список заявок
    """
    applications = Application.objects.all()
    serializer = ApplicationSerializer(applications, many=True)
    return Response(serializer.data)


@api_view(['Get', 'Delete'])
def detail_application(request, id, format=None):
    application = get_object_or_404(Application, id=id)
    if request.method == 'GET':
        """
        Возвращает информацию о заявке
        """
        serializer = ApplicationSerializer(application)
        return Response(serializer.data)
    elif request.method == 'DELETE':    
        """
        Удаляет информацию о заявке
        """
        application.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['Put'])
def put_status_user_application(request, id, format=None):
    """
    Обновляет информацию о статусе создателя
    """
    application = get_object_or_404(Application, id=id)
    application.status = 'Удалён'
    serializer = ApplicationSerializer(application, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['Put'])
def put_status_moderator_application(request, id, format=None):
    """
    Обновляет информацию о статусе модератора
    """
    application = get_object_or_404(Application, id=id)
    serializer = ApplicationSerializer(application, data=request.data)
    new_status = request.data.get('status')
    if new_status != 'Удалён':
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({'error': "Нельзя изменить статус на 'Удалён'."}, status=status.HTTP_403_FORBIDDEN)


@api_view(['Delete'])
def delete_appointment_from_application(request, id, format=None):    
    """
    Удаляет услугу из заявки
    """
    appapp = get_object_or_404(AppApp, id=id)
    appapp.delete()
    appapps = AppApp.objects.all()
    serializer = AppAppSerializer(appapps, many=True)
    return Response(serializer.data)