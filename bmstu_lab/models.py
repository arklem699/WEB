from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager, Group, Permission


class AppApp(models.Model):
    id_appl = models.ForeignKey('Application', models.CASCADE, db_column='id_appl')
    id_appoint = models.ForeignKey('Appointment', models.CASCADE, db_column='id_appoint')

    class Meta:
        managed = True
        db_table = 'app_app'


class Application(models.Model):
    id_user = models.ForeignKey('CustomUser', models.CASCADE, db_column='id_user')
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
    image = models.CharField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'appointment'


class NewUserManager(UserManager):
    def create_user(self,email,password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')
        
        email = self.normalize_email(email) 
        user = self.model(email=email, **extra_fields) 
        user.set_password(password)
        user.save(using=self.db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(("email адрес"), unique=True)
    username = models.CharField(max_length=30, unique=True, null=True, blank=True, verbose_name="Имя пользователя")
    password = models.CharField(max_length=100, verbose_name="Пароль")    
    is_staff = models.BooleanField(default=False, verbose_name="Является ли пользователь менеджером?")
    is_superuser = models.BooleanField(default=False, verbose_name="Является ли пользователь админом?")
    groups = models.ManyToManyField(Group, related_name='custom_user_groups', blank=True, verbose_name=('groups'), help_text=('The groups this user belongs to. A user will get all permissions granted to each of their groups.'), related_query_name='user', )
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions', blank=True, verbose_name=('user permissions'), help_text=('Specific permissions for this user.'), related_query_name='user', )

    USERNAME_FIELD = 'email'

    objects =  NewUserManager()

    class Meta:
        managed = True
        db_table = 'customUser'