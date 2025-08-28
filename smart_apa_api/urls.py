# your_app/urls.py

from django.urls import path
from .views import LDAPAuthAPIView
from .views import AutorizeView
from .views import AutorizeRefreshView
from .views import check_autorize
from .views import logout_view
from .views import regions_list
from .views import check_email

from .views import EmployeeSearchAPIView
from .views import EmployeesByDepartmentView
from .views import EmployeesByRegionView
from .views import EmployeeByIDView, EmployeeByEmailAPIView
from .views import RegionEmployeeSearchAPIView
from .views import SubordinationListAPIView, SubordinationDetailAPIView
from .views import DepartmentListAPIView, DepartmentDetailAPIView, DepartmentsBySubordinationView
from .views import RegionListAPIView, RegionDetailAPIView
from .views import SectorListAPIView, SectorDetailAPIView
from .views import PositionListAPIView, PositionDetailAPIView
from .views import EmployeeListAPIView
from .views import EmployeeSearchView
from .views import upload_user_photo
from .views import smartcloud_proxy, admission_proxy, icademium_proxy
from .views import events_by_iin

from .views import AutorizeView1
from .views import verify_email

urlpatterns = [
    path("api/smartcloud/", smartcloud_proxy),
    path("api/admission", admission_proxy, name="admission-proxy"),
    path("api/icademium", icademium_proxy, name="icademium-proxy"),
    # autorize
    #path('ldap/', LDAPAuthAPIView.as_view(), name='ldap-auth'),
   path('employees/', EmployeeSearchView.as_view(), name='employee-search'),
    path('autorize/', AutorizeView.as_view(), name='autorize'),
    #path('autorize/refresh', AutorizeRefreshView.as_view(), name='autorize_refresh'),
    path('autorize/check', check_autorize),
    path('upload/user-photo', upload_user_photo, name='upload_user_photo'),
    path('logout/', logout_view, name='logout'),
    # employee
    path('employee/search/', EmployeeSearchAPIView.as_view(), name='employee-search'),
    path('employees/department/<int:department_id>/', EmployeesByDepartmentView.as_view()),
    path('employee/<int:employee_id>/', EmployeeByIDView.as_view()),
    path('employee-by-email/', EmployeeByEmailAPIView.as_view(), name='employee-by-email'),
    path('subordinations/', SubordinationListAPIView.as_view(), name='subordination-list'),
    path('departments/', DepartmentListAPIView.as_view(), name='department-list'),
    path('departments/subordination/<int:subordination_id>/', DepartmentsBySubordinationView.as_view(), name='department-list'),
    #path('departments/<int:pk>/', DepartmentDetailAPIView.as_view(), name='department-detail'),
    #path('regions/', RegionListAPIView.as_view(), name='region-list'),
    #path('regions/<int:pk>/', RegionDetailAPIView.as_view(), name='region-detail'),
    path('sectors/', SectorListAPIView.as_view(), name='sector-list'),
    #path('sectors/<int:pk>/', SectorDetailAPIView.as_view(), name='sector-detail'),
    #path('positions/', PositionListAPIView.as_view(), name='position-list'),
    #path('positions/<int:pk>/', PositionDetailAPIView.as_view(), name='position-detail'),
    # regions
    #path('regions/', RegionListAPIView.as_view(), name='region-list'),
    path('regions/', regions_list, name='regions-list'),
    path('regions/<int:region_id>/', EmployeesByRegionView.as_view(), name='region-detail'),
    path('regions/search/', RegionEmployeeSearchAPIView.as_view(), name='region-search'),
    #path('check_email/', check_email, name='check_email'),
    path('employees/', EmployeeListAPIView.as_view(), name='employee-list'),
    path('employees/region/<int:region_id>/', EmployeeListAPIView.as_view(), name='employee-list-by-region'),
    path('api/scud/<str:iin>/', events_by_iin, name='events_by_iin'),
    # two factor email
    path('autorize1/', AutorizeView1.as_view(), name='autorize1'),
    path('verify-email/', verify_email, name = 'verify-email'),
    path('employee-by-email/', EmployeeByEmailAPIView.as_view(), name='employee-by-email'),

]
