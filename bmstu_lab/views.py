from django.shortcuts import render, get_object_or_404
from datetime import datetime
from bmstu_lab.models import Appointment, Application, AppApp, Students
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from bmstu_lab.serializers import AppAppSerializer, ApplicationSerializer, AppointmentSerializer


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


@api_view(['Get'])
def get_list_appointment(request, format=None):
    """
    Возвращает список услуг
    """
    print('get')
    appointments = Appointment.objects.all()
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)


@api_view(['Get'])
def get_detail_appointment(request, id, format=None):
    appointment = get_object_or_404(Appointment, id=id)
    if request.method == 'GET':
        """
        Возвращает информацию об услуге
        """
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)
    

@api_view(['Post'])
def post_list_appoinment(request, format=None):    
    """
    Добавляет новую услугу
    """
    print('post')
    serializer = AppointmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['Put'])
def put_detail_appointment(request, id, format=None):
    """
    Обновляет информацию об услуге
    """
    appointment = get_object_or_404(Appointment, id=id)
    serializer = AppointmentSerializer(appointment, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['Delete'])
def delete_detail_appointment(request, id, format=None):    
    """
    Удаляет информацию об услуге
    """
    appointment = get_object_or_404(Appointment, id=id)
    appointment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['Get'])
def get_list_application(request, format=None):
    """
    Возвращает список заявок
    """
    print('get')
    applications = Application.objects.all()
    serializer = ApplicationSerializer(applications, many=True)
    return Response(serializer.data)


@api_view(['Get'])
def get_detail_application(request, id, format=None):
    application = get_object_or_404(Application, id=id)
    if request.method == 'GET':
        """
        Возвращает информацию о заявке
        """
        serializer = ApplicationSerializer(application)
        return Response(serializer.data)


@api_view(['Delete'])
def delete_detail_application(request, id, format=None):    
    """
    Удаляет информацию о заявке
    """
    application = get_object_or_404(Application, id=id)
    application.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['Put'])
def put_status_user_application(request, id, format=None):
    """
    Обновляет информацию о стаутсе создателя
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
    Обновляет информацию о стаутсе модератора
    """
    application = get_object_or_404(Application, id=id)
    serializer = ApplicationSerializer(application, data=request.data)
    new_status = request.data.get('status')
    if new_status != 'Удалён':
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({'error': "Нельзя изменить статус на 'Удалён'."}, status=status.HTTP_400_BAD_REQUEST)