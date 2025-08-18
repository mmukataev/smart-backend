#from datetime import timezone
from django.utils import timezone

from django.shortcuts import render

# Create your views here.

# your_app/views.py
import requests 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework import generics

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from django.http import JsonResponse 
from rest_framework.decorators import api_view, parser_classes, permission_classes
import jwt
from django.conf import settings
from django.db.models import Q

from exchangelib import Credentials, Account, Configuration, DELEGATE, NTLM

from .ldap_utils import authenticate_and_get_user_info

from .autorize_utils import authenticate1
# from .autorize_utils import authenticate2
#from .autorize_utils import authenticate3

from  .mail_utils import check_email

from .rocketchat_utils import get_rocketchat_token
from .rocketchat_utils import get_last_conversations
from django.contrib.auth import authenticate

from smart_apa_api.models import SmartApaUser
from smart_apa_api.models import RegApaUserRole
from smart_apa_api.models import ByuropassUserRole
from smart_apa_api.models import AdmissionUserRole
from smart_apa_api.models import RegtestingUserRole
from smart_apa_api.models import IcademiumUserRole

from .models import Employee
from .models import Subordination
from .models import Department
from .models import Sector
from .models import Position

from .models import RegionEmployee
from .models import Region
from .models import RegionDepartment
from .models import RegionPosition

from .serializers import EmployeeSerializer
from .serializers import EmployeeSerializerLight
from .serializers import SubordinationSerializer
from .serializers import DepartmentSerializer
from .serializers import SectorSerializer
from .serializers import PositionSerializer

from .serializers import RegionEmployeeSerializer
from .serializers import RegionEmployeeSerializerLigth
from .serializers import RegionSerializer
from .serializers import RegionDepartmentSerializer
from .serializers import RegionPositionSerializer
from rest_framework.generics import ListAPIView

from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
import pytz
from .models import Employee
from .serializers import EmployeeSearchSerializer
from django.db.models import Q
import logging

from django.http import HttpResponse

logger = logging.getLogger(__name__)

from django.http import HttpResponse

def smartcloud_proxy(request):
    token = request.GET.get("token")
    if not token:
        return HttpResponse("Token is required", status=400)

    url = "https://smartcloud.apa.kz/"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Запрос к SmartCloud
        response = requests.get(url, headers=headers, timeout=10, verify=False)

        # Создаем HttpResponse для браузера
        proxy_response = HttpResponse(response.content, status=response.status_code)

        # Передаем cookies SmartCloud в браузер (если есть)
        for k, v in response.cookies.items():
            proxy_response.set_cookie(k, v)

        # Можно передать Content-Type
        if "Content-Type" in response.headers:
            proxy_response["Content-Type"] = response.headers["Content-Type"]

        return proxy_response

    except requests.Timeout:
        return HttpResponse("SmartCloud request timed out", status=504)
    except requests.RequestException as e:
        return HttpResponse(f"SmartCloud request failed: {e}", status=502)


class EmployeeSearchView(APIView):
    def get(self, request):
        search = request.GET.get("search", "")
        employees = Employee.objects.all()
        if search:
            employees = employees.filter(
                Q(user_name__icontains=search) |
                Q(user_surename__icontains=search) |
                Q(user_patronymic__icontains=search)
            )
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LDAPAuthAPIView(APIView):
    def post(self, request):
        login = request.data.get('login')
        password = request.data.get('password')

        if not login or not password:
            return Response({'status': 'failure', 'error': 'Missing login or password'}, status=status.HTTP_400_BAD_REQUEST)

        result = authenticate_and_get_user_info(login, password)

        if result['status'] == 'success':
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_401_UNAUTHORIZED)



class AutorizeView(APIView):
    def post(self, request):
        login = request.data.get("login")
        password = request.data.get("password")

        if not login or not password:
            return Response({'status': 'failure', 'error': 'Missing login or password'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate1(login, password)
        # user = authenticate2(login, password)
        #user = authenticate3(login, password)
        if user is not None:
            byuropass_user, _ = ByuropassUserRole.objects.get_or_create(login=login)
            regapa_user, _ = RegApaUserRole.objects.get_or_create(login=login)
            admission_user, _ = AdmissionUserRole.objects.get_or_create(login=login)
            regtesting_user, _ = RegtestingUserRole.objects.get_or_create(login=login)
            icademium_user, _ = IcademiumUserRole.objects.get_or_create(login=login)
            
            try:
                chat_token, chat_uid = get_rocketchat_token(login, password)
            except Exception as e:
                # Handle any connection or unexpected errors gracefully
                print(f"[ERROR] Failed to get Rocket.Chat token: {e}")
                chat_token = None
                chat_uid = None

            # chat_token, chat_uid = get_rocketchat_token(login, password)
            if chat_token is not None:
                lst = get_last_conversations(chat_token, chat_uid, login)
            else:
                lst = []

            #refresh = RefreshToken.for_user(user)
            #refresh["username"] = user.login
            # Add roles
            #refresh["byuropass_role"] = byuropass_user.role
            #refresh["admission_role"] = admission_user.role
            #refresh["regtesting_role"] = regtesting_user.role
            #refresh["icademium_role"] = icademium_user.role
            if regapa_user.region == 40:
                regapa_user.region = 20

            employee = Employee.objects.filter(user_email=user.login).first()
            
            token = AccessToken.for_user(user)
            token["username"] = user.login
            # Full name & objectGUID from AD
            token["guid"] = user.object_guid
            token["display_name"] = user.display_name
            # Full name from Employee Table
            token["employee_name"] = employee.user_name if employee else None
            token["employee_surename"] = employee.user_surename if employee else None
            token["employee_patronymic"] = employee.user_patronymic if employee else None
            # is_chief from Employee Table
            token["is_chief"] = employee.is_chief if employee else None
            # Add roles
            token["byuropass_role"] = byuropass_user.role
            token["regapa_role"] = regapa_user.role
            token["regapa_region"] = regapa_user.region
            token["admission_role"] = admission_user.role
            token["regtesting_role"] = regtesting_user.role
            token["icademium_role"] = icademium_user.role

            #emails = check_email(login, password)
            #return Response({
            #    'access': str(token),
            #    #'access': str(token.access_token),
            #    #'refresh': str(refresh),
            #})
            
            #response = Response({'status': 'login successful', 'access': str(token)}, status=status.HTTP_200_OK)
            #response = Response({'status': 'login successful', 'access': str(token),
            #                     'chattoken':str(chat_token), 'chatuserid':str(chat_uid), 'chatlist':lst,
            #                     'emails': emails }, status=status.HTTP_200_OK)
            response = Response({'status': 'login successful', 'access': str(token),
                                 'chattoken':str(chat_token), 'chatuserid':str(chat_uid), 'chatlist':lst}, status=status.HTTP_200_OK)

            # Set the token in HttpOnly cookie
            response.set_cookie(
                key='access_token',
                value=str(token),
                domain='.apa.kz',
                path='/',
                httponly=False,
                secure=True,  # False, set to True in production
                samesite='None',  # 'Lax' or 'Strict', or 'None'
                max_age=3600,  # 900 - 15min, 3600 - 1 hour
            )

            return response
        
        # Hardcoded login check
        #if login == "j.depp@apa.kz" and password == "Academy2024$!":
        #    # Create a dummy user-like object for token creation
        #    class DummyUser:
        #        def __init__(self, username):
        #            self.username = username
        #            self.id = 9999  # Any static id
        #            self.is_active = True
        #
        #    dummy_user = DummyUser(username=login)
        #
        #    # Generate JWT token using dummy user
        #    refresh = RefreshToken.for_user(dummy_user)
        #    refresh["username"] = dummy_user.username  # Add custom claim
        #
        #    return Response({
        #        'access': str(refresh.access_token),
        #        'refresh': str(refresh),
        #    })
        
        return Response({'status': 'failure', 'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)		


class AutorizeRefreshView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({'status': 'failure', 'error': 'No refresh token provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token

            # Optional: Add custom claims to access token
            access_token["username"] = refresh["username"]  # Assuming you stored it when issuing

            return Response({
                "access": str(access_token)
            })

        except TokenError as e:
            return Response({'status': 'failure', 'error': 'Invalid or expired refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)		


@api_view(['GET'])
def check_autorize(request):
    token = request.COOKIES.get('access_token')
    if not token:
        return JsonResponse({'authorized': False}, status=401)

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = SmartApaUser.objects.get(login=payload['username'])

        employee = Employee.objects.filter(user_email=user.login).first()
        image_url = employee.user_image.url if employee and employee.user_image else None

        return JsonResponse({
            'authorized': True,
            'login': user.login,
            'display_name': user.display_name,
            'title': user.title,
            'department': user.department,
            'image': image_url,
            'user_id' : employee.id if employee else None,
            'user_name': employee.user_name if employee else None,
            'user_surename': employee.user_surename if employee else None,
            'user_patronymic': employee.user_patronymic if employee else None,
        })

    except jwt.ExpiredSignatureError:
        return JsonResponse({'authorized': False, 'error': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({'authorized': False, 'error': 'Invalid token'}, status=401)


@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload_user_photo(request):
    token = request.COOKIES.get('access_token')
    if not token:
        return JsonResponse({'error': 'Токен не найден'}, status=401)

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        login = payload.get('username')

        if not login:
            return JsonResponse({'error': 'Неверный токен'}, status=401)

        employee = Employee.objects.filter(user_email=login).first()
        if not employee:
            return JsonResponse({'error': 'Сотрудник не найден'}, status=404)

        image_file = request.FILES.get('user_image')
        if not image_file:
            return JsonResponse({'error': 'Файл не найден'}, status=400)

        employee.user_image = image_file
        employee.save()

        return JsonResponse({'message': 'Фотография успешно обновлена', 'image': employee.user_image.url})

    except jwt.ExpiredSignatureError:
        return JsonResponse({'error': 'Токен истёк'}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({'error': 'Недействительный токен'}, status=401)

@api_view(['POST'])
def logout_view(request):
    token = request.COOKIES.get('access_token')
    last_logout = None

    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = SmartApaUser.objects.get(login=payload['username'])
            user.last_logout = timezone.now()
            last_logout = user.last_logout
            user.save()
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, SmartApaUser.DoesNotExist):
            pass

    response = JsonResponse({'message': 'Logged out', 'last_logout': last_logout})
    response.delete_cookie(
        key='access_token',
        domain='.apa.kz',
        path='/'
    )
    return response
# Employee

# Subordination
class SubordinationListAPIView(generics.ListAPIView):
    queryset = Subordination.objects.all()
    serializer_class = SubordinationSerializer
    
class SubordinationDetailAPIView(generics.RetrieveAPIView):
    queryset = Subordination.objects.all()
    serializer_class = SubordinationSerializer
    
# Department
class DepartmentListAPIView(generics.ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    
class DepartmentDetailAPIView(generics.RetrieveAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

# Sector
class SectorListAPIView(generics.ListAPIView):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    
class SectorDetailAPIView(generics.RetrieveAPIView):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    
# Position
class PositionListAPIView(generics.ListAPIView):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    
class PositionDetailAPIView(generics.RetrieveAPIView):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer    

#class EmployeeSearchAPIView(generics.ListAPIView):
#    serializer_class = EmployeeSerializer
#
#    def get_queryset(self):
#        queryset = Employee.objects.all()
#        name = self.request.query_params.get('name', None)
#        surname = self.request.query_params.get('surname', None)
#        if name or surname:
#            queryset = queryset.filter(
#                Q(user_name__icontains=name) & Q(user_surename__icontains=surname)
#            )
#        return queryset

class EmployeeSearchAPIView(generics.ListAPIView):
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        search_query = self.request.GET.get('s', '')
        if search_query:
            return Employee.objects.filter(
                Q(user_name__icontains=search_query) |
                Q(user_surename__icontains=search_query) |
                Q(user_patronymic__icontains=search_query)
            )
        else:
            return Employee.objects.none()    

class EmployeeListAPIView(ListAPIView):
    queryset = Employee.objects.all().select_related('department', 'sector', 'position', 'subordination')
    serializer_class = EmployeeSerializer


class EmployeesByDepartmentView(APIView):
    def get(self, request, department_id):
        employees = Employee.objects.filter(department_id=department_id)
        serializer = EmployeeSerializer(employees, many=True)
        #serializer = EmployeeSerializerLight(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# views.py

# class EmployeesByDepartmentView(APIView):
#     def get(self, request, department_id):
#         employees = Employee.objects.filter(department_id=department_id).select_related('user_role')
#         serializer = EmployeeSerializer(employees, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

        
        
        
class DepartmentsBySubordinationView(APIView):
    def get(self, request, subordination_id):
        departments = Department.objects.filter(subordination_id=subordination_id)
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)            
        
class EmployeeByIDView(APIView):
    def get(self, request, employee_id):
        employees = Employee.objects.filter(id=employee_id)
        serializer = EmployeeSerializer(employees, many=True)
        #serializer = EmployeeSerializerLight(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)        
        
        
        
# Region
class RegionListAPIView(generics.ListAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    
class RegionDetailAPIView(generics.RetrieveAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer        
    
    
    
@api_view(['GET'])
def regions_list(request):
    directors = RegionEmployee.objects.filter(position_id=8)
    serializer = RegionEmployeeSerializer(directors, many=True)
    return Response(serializer.data)    
    
    
class EmployeesByRegionView(APIView):
    def get(self, request, region_id):
        employees = RegionEmployee.objects.filter(region_id=region_id).exclude(position_id=8)
        #serializer = RegionEmployeeSerializer(employees, many=True)
        serializer = RegionEmployeeSerializerLigth(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)    
        
        
class RegionEmployeeSearchAPIView(generics.ListAPIView):
    serializer_class = RegionEmployeeSerializer

    def get_queryset(self):
        search_query = self.request.GET.get('s', '')
        if search_query:
            return RegionEmployee.objects.filter(
                Q(user_name__icontains=search_query) |
                Q(user_surename__icontains=search_query) |
                Q(user_patronymic__icontains=search_query)
            )
        else:
            return RegionEmployee.objects.none()

class EmployeeByEmailAPIView(APIView):
    def get(self, request):
        email = request.query_params.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            employee = Employee.objects.select_related("position").get(user_email=email)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

        data = {
            "id": employee.id,
            "surename": employee.user_surename,
            "name": employee.user_name,
            "patronymic": employee.user_patronymic,
            "fio": f"{employee.user_surename} {employee.user_name} {employee.user_patronymic or ''}".strip(),
            "position": {
                "kz": employee.position.kz if employee.position else None,
                "ru": employee.position.ru if employee.position else None
            },

            "photo": (
                request.build_absolute_uri(employee.user_image.url)
                if employee.user_image and hasattr(employee.user_image, 'url')
                else None
            )
        }
        return Response(data, status=status.HTTP_200_OK)




# def check_email(request):
#     # Optional: you can secure this endpoint with login_required or token authentication
#
#     try:
#         # Replace with real values or use environment variables
#         username = 'apa.kz\\a.kerimbayev'
#         password = '9xWF9TZ+'
#         email_address = 'a.kerimbayev@apa.kz'
#         exchange_server = 'mail.apa.kz'  # e.g., 'mail.company.com'
#
#         credentials = Credentials(username=username, password=password)
#         config = Configuration(server=exchange_server, credentials=credentials, auth_type=NTLM)
#         account = Account(primary_smtp_address=email_address, config=config, autodiscover=False, access_type=DELEGATE)
#
#         unread_emails = account.inbox.filter(is_read=False).order_by('-datetime_received')[:10]
#
#         email_data = []
#         for msg in unread_emails:
#             email_data.append({
#                 'subject': msg.subject,
#                 'from': msg.sender.email_address if msg.sender else 'Unknown',
#                 'received': msg.datetime_received.strftime('%Y-%m-%d %H:%M:%S'),
#                 #'body': str(msg.body)[:500],  # limit size
#                 'body': str(msg.body),
#             })
#
#         return JsonResponse({'emails': email_data})
#
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)