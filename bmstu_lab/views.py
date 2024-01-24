from django.conf import settings
from django.contrib.auth import authenticate, login, logout  
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, QueryDict
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
    print(serializer)
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
    username = request.data.get("email") 
    password = request.data.get("password")
    user = authenticate(request=request, email=username, password=password)
    if user is not None:
        login(request, user)
        user_id = user.id
        random_key = uuid.uuid4()
        session_storage.set(str(random_key), user_id)
        response_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_admin': user.is_superuser
        }
        response = JsonResponse(response_data)
        response.set_cookie("session_id", random_key, httponly=True, samesite='None', secure=True, path='/')
        return response
    else:
        return HttpResponse("{'status': 'error', 'error': 'login failed'}", status=401)


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
    data = QueryDict(mutable=True)
    data = request.data.copy()

    if "image" not in data:
        data['image'] = "b'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'"
    
    else:
        image_file = data['image']
        image_data = base64.b64encode(image_file.read())
        data['image'] = f"{image_data}"

    serializer = AppointmentSerializer(data=data)

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
        Добавляет услугу в заявку-черновик
        """
        ssid = request.COOKIES.get("session_id")

        if ssid is not None:
            user_id = session_storage.get(ssid)

            if user_id is not None:
                application = Application.objects.filter(Q(id_user=user_id) & Q(status='Черновик')).first()

                if application is None:
                    application = Application.objects.create(
                    id_user = CustomUser.objects.get(id=user_id),
                    status = 'Черновик',
                    date_creating = datetime.now().strftime("%Y-%m-%d")
                    )
                    application.save()
                    
                new_appapp, created = AppApp.objects.get_or_create(
                    id_appl = application,
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

    if appointment.image:
        return Response(appointment.image[2:-1])
    
    return Response({ 'error': 'Поле "image" отсутствует в запросе' })


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
def get_list_user_application(request, format=None):
    """
    Возвращает список черновой заявки пользователя
    """
    ssid = request.COOKIES.get("session_id")

    if ssid is not None:
        user_id = session_storage.get(ssid)

        if user_id is not None:
            
            user = CustomUser.objects.get(id=user_id)
            if Application.objects.filter(id_user=user_id).exists():
                applications = Application.objects.filter(Q(id_user=user_id) & Q(status='Черновик'))
                app_apps = AppApp.objects.filter(id_appl__in=applications.values('id'))
                data = [
                    {
                        'id': app_app.id_appoint.id,
                        'date': app_app.id_appoint.date,
                        'time': app_app.id_appoint.time,
                        'doctor': app_app.id_appoint.doctor,
                        'status': app_app.id_appoint.status,
                        'id_appl': app_app.id_appl.id
                    }
                    for app_app in app_apps
                ]
                return Response(data)
            
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    else:
        return Response(status=status.HTTP_403_FORBIDDEN)
    

@api_view(['GET'])
def get_list_applications_user(request, format=None):
    """
    Возвращает список всех заявок пользователя
    """
    ssid = request.COOKIES.get("session_id")

    if ssid is not None:
        user_id = session_storage.get(ssid)

        if user_id is not None:
            user = CustomUser.objects.get(id=user_id)

            applications = Application.objects.filter(Q(id_user=user_id) & ~Q(status='Черновик') & ~Q(status='Удалена'))
            data = [
                {
                    'id': application.id,
                    'date_creating': application.date_creating,
                    'date_formation': application.date_formation,
                    'date_completion': application.date_completion,
                    'status': application.status,
                }
                for application in applications
            ]
            return Response(data)
            
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([IsAdmin | IsManager])
def get_list_applications(request, format=None):
    """
    Возвращает список всех заявок
    """
    ssid = request.COOKIES.get("session_id")

    if ssid is not None:
        user_id = session_storage.get(ssid)

        if user_id is not None:
            user = CustomUser.objects.get(id=user_id)

            applications = Application.objects.exclude(Q(status='Черновик') | Q(status='Удалён'))
            data = [
                {
                    'id': application.id,
                    'date_creating': application.date_creating,
                    'date_formation': application.date_formation,
                    'status': application.status,
                    'username': application.id_user.username
                }
                for application in applications
            ]
            return Response(data)
            
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
            application.date_formation = datetime.now().strftime("%Y-%m-%d")
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
                    application.status = new_status
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
    

@swagger_auto_schema(method='put', request_body=ApplicationSerializer)
@permission_classes([AllowAny])
@api_view(['PUT'])
def put_async_was_application(request, id, format=None):
    """
    Обновление поля was асинхронным сервером
    """
    const_token = 'access_token'
    if const_token != request.data.get('token'):
        return Response({'message': 'Ошибка, токен не соответствует'}, status=status.HTTP_403_FORBIDDEN)
    
    application = Application.objects.get(id=id)
    application.was = request.data.get('was')
    application.save()
    serializer = ApplicationSerializer(application)
    return Response(serializer.data)


@api_view(['DELETE'])
def delete_appointment_from_application(request, id, format=None):    
    """
    Удаляет услугу из заявки
    """
    ssid = request.COOKIES.get("session_id")

    if ssid is not None:
        user_id = session_storage.get(ssid)

        if user_id is not None:

            appapps = AppApp.objects.filter(id_appl__id_user=user_id, id_appl__status='Черновик')
            appapp = get_object_or_404(appapps, id_appoint=id)
            appapp.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)