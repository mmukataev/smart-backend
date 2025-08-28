from django.contrib import admin

# Register your models here.

from .models import SmartApaUser
from .models import ByuropassUserRole
from .models import RegApaUserRole
from .models import AdmissionUserRole
from .models import RegtestingUserRole
from .models import IcademiumUserRole

from .models import Employee
from .models import Subordination
from .models import Department 
from .models import Sector
from .models import Position

from .models import Region
from .models import RegionEmployee
from .models import RegionDepartment
from .models import RegionPosition


from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.formats.base_formats import XLSX

@admin.register(SmartApaUser)
class SmartApaUserAdmin(admin.ModelAdmin):
    search_fields = ['login', 'role', 'display_name', 'title', 'department']
    list_display = ('login', 'display_name', 'role', 'is_email_verified', 'last_login', 'last_logout')
    list_editable = ('is_email_verified',)  # редактируем прямо в списке
    readonly_fields = ('login', 'display_name', 'title', 'department', 'last_login', 'last_logout')
    fields = (
        'login', 'role', 'display_name', 'title', 'department',
        'last_login', 'last_logout', 'last_ad_check', 'blocked_until',
        'bad_pwd_count', 'is_active', 'is_email_verified'  # <-- добавлено
    )

    def has_add_permission(self, request):
        return False  # запрет на добавление новых



@admin.register(ByuropassUserRole)
class ByuropassUserRoleAdmin(admin.ModelAdmin):
    search_fields = ['login', 'role']
    readonly_fields = ('login',)
    fields = ('login', 'role')
    def has_add_permission(self, request):
        return False  # Disables the add button
        
@admin.register(RegApaUserRole)
class RegApaUserRoleAdmin(admin.ModelAdmin):
    search_fields = ['login', 'role', 'region']
    readonly_fields = ('login',)
    fields = ('login', 'role', 'region')
    def has_add_permission(self, request):
        return False  # Disables the add button

@admin.register(AdmissionUserRole)
class AdmissionUserRoleAdmin(admin.ModelAdmin):
    search_fields = ['login', 'role']
    readonly_fields = ('login',)
    fields = ('login', 'role')
    def has_add_permission(self, request):
        return False  # Disables the add button   


@admin.register(RegtestingUserRole)
class RegtestingUserRoleAdmin(admin.ModelAdmin):
    search_fields = ['login', 'role']
    readonly_fields = ('login',)
    fields = ('login', 'role')
    def has_add_permission(self, request):
        return False  # Disables the add button     


@admin.register(IcademiumUserRole)
class IcademiumUserRoleAdmin(admin.ModelAdmin):
    search_fields = ['login', 'role']
    readonly_fields = ('login',)
    fields = ('login', 'role')
    def has_add_permission(self, request):
        return False  # Disables the add button        



        
# Employee   
class EmployeeResource(resources.ModelResource):
    class Meta:
        model = Employee
        fields = ('id', 'user_name', 'user_surename', 'user_patronymic', 'subordination', 'region', 'department', 'sector', 'position', 'user_phone', 'user_email', 'user_image','birth_date', 'work_start_date','is_chief','is_sector_head','region_id')
        
@admin.register(Employee)
class EmployeeAdmin(ImportExportModelAdmin):
    resource_class = EmployeeResource
    #list_display = ('user_name', 'user_surename', 'user_patronymic', 'subordination', 'region', 'department', 'sector', 'position', 'user_phone')
    list_display = ('user_name', 'user_surename', 'user_patronymic', 'subordination', 'department', 'sector', 'position', 'user_phone', 'user_email', 'user_image','birth_date','work_start_date','is_chief','is_sector_head','region_id')
    #search_fields = ('user_name', 'user_surename', 'user_patronymic', 'subordination', 'region', 'department', 'sector', 'position', 'user_phone')
    #search_fields = ('user_name', 'user_surename', 'user_patronymic', 'user_phone')
    search_fields = ('user_name', 'user_surename', 'user_patronymic', 'user_phone', 'user_email')
    
    def get_export_formats(self):
        formats = super().get_export_formats()
        formats.append(XLSX)
        return formats

    def get_import_formats(self):
        formats = super().get_import_formats()
        formats.append(XLSX)
        return formats    

# Subordination
class SubordinationResource(resources.ModelResource):
    class Meta:
        model = Subordination
        fields = ('id', 'full_name', 'kz', 'ru')
        
@admin.register(Subordination)
class SubordinationAdmin(ImportExportModelAdmin):
    resource_class = SubordinationResource
    list_display = ('full_name', 'kz', 'ru')
    search_fields = ('full_name', 'kz', 'ru')
    
    def get_export_formats(self):
        formats = super().get_export_formats()
        formats.append(XLSX)
        return formats

    def get_import_formats(self):
        formats = super().get_import_formats()
        formats.append(XLSX)
        return formats    


    
# Department    
class DepartmentResource(resources.ModelResource):
    class Meta:
        model = Department
        fields = ('id', 'subordination', 'kz', 'ru')
        
@admin.register(Department)
class DepartmentAdmin(ImportExportModelAdmin):
    resource_class = DepartmentResource
    list_display = ('subordination', 'kz', 'ru')
    search_fields = ('subordination', 'kz', 'ru')    
    
    def get_export_formats(self):
        formats = super().get_export_formats()
        formats.append(XLSX)
        return formats

    def get_import_formats(self):
        formats = super().get_import_formats()
        formats.append(XLSX)
        return formats    

# Sector    
class SectorResource(resources.ModelResource):
    class Meta:
        model = Sector
        fields = ('id', 'kz', 'ru')
        
@admin.register(Sector)
class SectorAdmin(ImportExportModelAdmin):
    resource_class = SectorResource
    list_display = ('kz', 'ru')
    search_fields = ('kz', 'ru')    
    
    def get_export_formats(self):
        formats = super().get_export_formats()
        formats.append(XLSX)
        return formats

    def get_import_formats(self):
        formats = super().get_import_formats()
        formats.append(XLSX)
        return formats    

# Position
class PositionResource(resources.ModelResource):
    class Meta:
        model = Position
        fields = ('id', 'kz', 'ru')
        
@admin.register(Position)
class PositionAdmin(ImportExportModelAdmin):
    resource_class = PositionResource
    list_display = ('kz', 'ru')
    search_fields = ('kz', 'ru') 

    def get_export_formats(self):
        formats = super().get_export_formats()
        formats.append(XLSX)
        return formats

    def get_import_formats(self):
        formats = super().get_import_formats()
        formats.append(XLSX)
        return formats    
        
        
        
        
# Region Employee   
class RegionEmployeeResource(resources.ModelResource):
    class Meta:
        model = RegionEmployee
        fields = ('id', 'user_name', 'user_surename', 'user_patronymic', 'region', 'department', 'position', 'user_phone', 'user_email', 'user_image')
        
@admin.register(RegionEmployee)
class RegionEmployeeAdmin(ImportExportModelAdmin):
    resource_class = RegionEmployeeResource
    list_display = ('user_name', 'user_surename', 'user_patronymic', 'region', 'department', 'position', 'user_phone', 'user_email', 'user_image')
    search_fields = ('user_name', 'user_surename', 'user_patronymic', 'user_phone', 'user_email')
    
    def get_export_formats(self):
        formats = super().get_export_formats()
        formats.append(XLSX)
        return formats

    def get_import_formats(self):
        formats = super().get_import_formats()
        formats.append(XLSX)
        return formats        
        
        
# Region Region   
class RegionResource(resources.ModelResource):
    class Meta:
        model = Region
        fields = ('id', 'kz', 'ru')
        
@admin.register(Region)
class RegionAdmin(ImportExportModelAdmin):
    resource_class = RegionResource
    list_display = ('kz', 'ru')
    search_fields = ('kz', 'ru')
    
    def get_export_formats(self):
        formats = super().get_export_formats()
        formats.append(XLSX)
        return formats

    def get_import_formats(self):
        formats = super().get_import_formats()
        formats.append(XLSX)
        return formats        
        
        
# Region Department    
class RegionDepartmentResource(resources.ModelResource):
    class Meta:
        model = RegionDepartment
        fields = ('id', 'kz', 'ru')
        
@admin.register(RegionDepartment)
class RegionDepartmentAdmin(ImportExportModelAdmin):
    resource_class = RegionDepartmentResource
    list_display = ('kz', 'ru')
    search_fields = ('kz', 'ru')    
    
    def get_export_formats(self):
        formats = super().get_export_formats()
        formats.append(XLSX)
        return formats

    def get_import_formats(self):
        formats = super().get_import_formats()
        formats.append(XLSX)
        return formats          
        
        
# Region Position
class RegionPositionResource(resources.ModelResource):
    class Meta:
        model = RegionPosition
        fields = ('id', 'kz', 'ru')
        
@admin.register(RegionPosition)
class PositionAdmin(ImportExportModelAdmin):
    resource_class = RegionPositionResource
    list_display = ('kz', 'ru')
    search_fields = ('kz', 'ru') 

    def get_export_formats(self):
        formats = super().get_export_formats()
        formats.append(XLSX)
        return formats

    def get_import_formats(self):
        formats = super().get_import_formats()
        formats.append(XLSX)
        return formats        