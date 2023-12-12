from django.conf import settings
from django.contrib.auth import authenticate, login, logout  
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime
from bmstu_lab.models import Appointment, Application, AppApp, CustomUser
from bmstu_lab.serializers import AppAppSerializer, ApplicationSerializer, AppointmentSerializer, UserSerializer
from bmstu_lab.permissions import IsAdmin, IsManager
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from datetime import datetime
import base64
import redis
import uuid


# Connect to our Redis instance
session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

class UserViewSet(viewsets.ModelViewSet):
    """
    Класс, описывающий методы работы с пользователями
    Осуществляет связь с таблицей пользователей в базе данных
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [AllowAny]
        elif self.action in ['list']:
            permission_classes = [IsAdmin | IsManager]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def register(request):
    """
    Регистрация пользователя
    """
    serializer = UserSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = serializer.save()

    message = {
        'message': 'Пользователь успешно зарегистрировался',
        'user_id': user.id
    }

    return Response(message, status=status.HTTP_201_CREATED)


@swagger_auto_schema(method='post', request_body=UserSerializer)
@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
@authentication_classes([])
def login_view(request):
    """
    Авторизация пользователя
    """
    username = request.POST["email"] 
    password = request.POST["password"]
    user = authenticate(request=request, email=username, password=password)
    if user is not None:
        login(request, user)
        user_id = CustomUser.objects.get(email=username).id
        random_key = uuid.uuid4()
        session_storage.set(str(random_key), user_id)
        response = HttpResponse("{'status': 'ok'}")
        response.set_cookie("session_id", random_key)
        return response
    else:
        return HttpResponse("{'status': 'error', 'error': 'login failed'}")


@api_view(['POST'])
def logout_view(request):
    """
    Выход из профиля
    """
    logout(request)
    return Response({'status': 'Success'})


@api_view(['GET'])
def get_search_appointment(request, format=None):
    """
    Возвращает список услуг по запросу
    """
    query = request.GET.get('query', '')
    if query != '':
        query_date = datetime.strptime(query, '%d.%m.%Y').strftime('%Y-%m-%d')
        appointments = Appointment.objects.filter(date=query_date)
    else:
        appointments = Appointment.objects.all()
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_list_appointment(request, format=None):
    """
    Возвращает список услуг
    """
    appointments = Appointment.objects.all()
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)


@swagger_auto_schema(method='post', request_body=AppointmentSerializer)
@api_view(['POST'])
@permission_classes([IsAdmin | IsManager])
def post_list_appointment(request, format=None):    
    """
    Добавляет новую услугу
    """
    serializer = AppointmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='post', request_body=AppointmentSerializer) 
@api_view(['GET', 'POST'])
def detail_appointment(request, id, format=None):
    if request.method == 'GET':
        """
        Возвращает информацию об услуге
        """
        appointment = get_object_or_404(Appointment, id=id)
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)   
    
    elif request.method == 'POST':    
        """
        Добавляет услугу в последнюю заявку
        """
        ssid = request.COOKIES.get("session_id")

        if ssid is not None:
            user_id = session_storage.get(ssid)

            if user_id is not None:
                new_appapp, created = AppApp.objects.get_or_create(
                    id_appl = Application.objects.filter(id_user=user_id).latest('id'),
                    id_appoint = Appointment.objects.get(id=id)
                )
                serializer = AppAppSerializer(new_appapp)

                if created:
                    new_appapp.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                
                else:
                    return Response(serializer.data, status=status.HTTP_200_OK)
                
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
    
    
@swagger_auto_schema(method='put', request_body=AppointmentSerializer)
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAdmin | IsManager])
def update_appointment(request, id, format=None):              
    appointment = get_object_or_404(Appointment, id=id)

    if request.method == 'PUT':
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


@api_view(['GET'])
def get_image_appointment(request, id, format=None):
    """
    Возвращает картинку из услуги
    """
    appointment = Appointment.objects.get(id=id)

    return Response(appointment.image[2:-1])


@swagger_auto_schema(method='put', request_body=AppointmentSerializer)
@api_view(['PUT'])
@permission_classes([IsAdmin | IsManager])
def add_image_appointment(request, id, format=None):
    """
    Добавляет изображение в услугу
    """
    appointment = Appointment.objects.get(id=id)

    if 'image' in request.data:
        image_file = request.data['image']
        image_data = base64.b64encode(image_file.read())
        appointment.image = image_data
        appointment.save()

        return Response({ 'message': 'Изображение успешно добавлено' }, status=status.HTTP_201_CREATED)

    else:
        return Response({ 'error': 'Поле "image" отсутствует в запросе' }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_list_application(request, format=None):
    """
    Возвращает список заявок
    """
    ssid = request.COOKIES.get("session_id")

    if ssid is not None:
        user_id = session_storage.get(ssid)

        if user_id is not None:
            user = CustomUser.objects.get(id=user_id)

            # Все заявки для админов
            if user.is_staff or user.is_superuser:
                applications = Application.objects.exclude(Q(status='Черновик') | Q(status='Удалён'))
                serializer = ApplicationSerializer(applications, many=True)
                return Response(serializer.data)
            
            # Собственные заявки для пользователя
            elif Application.objects.filter(id_user=user_id).exists():
                applications = Application.objects.filter(Q(id_user=user_id) & ~(Q(status='Черновик') | Q(status='Удалён')))
                serializer = ApplicationSerializer(applications, many=True)
                return Response(serializer.data)
            
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
            
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
def detail_application(request, id, format=None):
    """
    Возвращает информацию о заявке
    """
    ssid = request.COOKIES.get("session_id")

    if ssid is not None:
        user_id = session_storage.get(ssid)

        if user_id is not None:

            applications = Application.objects.filter(Q(id_user=user_id) & ~(Q(status='Черновик') | Q(status='Удалён')))
            application = get_object_or_404(applications, id=id)
            appapps = AppApp.objects.filter(id_appl=id)
            appointments = []

            for appapp in appapps:
                appointments.append(Appointment.objects.get(id=appapp.id_appoint.id))

            serializer_appl = ApplicationSerializer(application)
            serializer_appoint = AppointmentSerializer(appointments, many=True)
            response_data = {'Заявка': serializer_appl.data, 'Услуги': serializer_appoint.data}

            return Response(response_data)
        
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)
    

@api_view(['DELETE'])
def delete_application(request, id, format=None):    
    """
    Удаляет информацию о заявке
    """
    ssid = request.COOKIES.get("session_id")

    if ssid is not None:
        user_id = session_storage.get(ssid)

        if user_id is not None:

            applications = Application.objects.filter(Q(id_user=user_id) & Q(status='Черновик'))
            application = get_object_or_404(applications, id=id)
            application.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@swagger_auto_schema(method='put', request_body=ApplicationSerializer)
@api_view(['PUT'])
def put_status_user_application(request, id, format=None):
    """
    Формирование заявки создателем
    """
    ssid = request.COOKIES.get("session_id")

    if ssid is not None:
        user_id = session_storage.get(ssid)

        if user_id is not None:

            applications = Application.objects.filter(Q(id_user=user_id) & Q(status='Черновик'))
            application = get_object_or_404(applications, id=id)
            application.status = 'Сформирована'
            application.save()
            serializer = ApplicationSerializer(application)
            return Response(serializer.data)
            
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@swagger_auto_schema(method='put', request_body=ApplicationSerializer)
@api_view(['PUT'])
@permission_classes([IsAdmin | IsManager])
def put_status_moderator_application(request, id, format=None):
    """
    Одобрение или отклонение заявки модератором
    """
    ssid = request.COOKIES.get("session_id")
    if ssid is not None:
        user_id = session_storage.get(ssid)

        if user_id is not None:
            user = CustomUser.objects.get(id=user_id)
            application = get_object_or_404(Application, id=id)

            if application.status == 'Сформирована':
                serializer = ApplicationSerializer(application, data=request.data)
                new_status = request.data.get('status')

                if new_status in ('Одобрена', 'Отклонена'):
                    application.date_completion = datetime.now().strftime("%Y-%m-%d")
                    application.moderator = user.username
                    application.save()
                    serializer = ApplicationSerializer(application)
                    return Response(serializer.data)
                    
                else:
                    error_message = "Неправильный статус. Допустимые значения: 'Одобрена', 'Отклонена'."
                    return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
                
            else:
                error_message = "Нельзя сменить статус у этой заявки."
                return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['DELETE'])
def delete_appointment_from_application(request, id, format=None):    
    """
    Удаляет услугу из заявки
    """
    ssid = request.COOKIES.get("session_id")

    if ssid is not None:
        user_id = session_storage.get(ssid)

        if user_id is not None:

            appapps = AppApp.objects.filter(id_appl__id_user=user_id)
            appapp = get_object_or_404(appapps, id=id)
            appapp.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)