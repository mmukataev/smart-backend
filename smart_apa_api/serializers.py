from rest_framework import serializers
from .models import Employee, Subordination, Department, Sector, Position
from .models import RegionEmployee, Region, RegionDepartment, RegionPosition
from datetime import timedelta
from django.utils.timezone import now
from .models import Employee

class SubordinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subordination
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
        
class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = '__all__'        

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'

# class EmployeeSerializer(serializers.ModelSerializer):
  
#     subordination = SubordinationSerializer()                                         
#     #region = RegionSerializer()
#     department = DepartmentSerializer()
#     sector = SectorSerializer()
#     position = PositionSerializer()

#     class Meta:
#         model = Employee
#         fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    user_image = serializers.ImageField(use_url=True)
    last_logout = serializers.SerializerMethodField()
    chief = serializers.SerializerMethodField()

    subordination = SubordinationSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    sector = SectorSerializer(read_only=True)
    position = PositionSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = '__all__'

    def get_last_logout(self, obj):
        from smart_apa_api.models import SmartApaUser
        if obj.user_email:
            try:
                user_role = SmartApaUser.objects.filter(login=obj.user_email).first()
                if user_role and user_role.last_logout:
                    return user_role.last_logout.strftime('%Y-%m-%d %H:%M')
            except Exception:
                pass
        return None

    def get_chief(self, obj):
        from .models import Employee  # убедимся, что импорт есть

        # 1. Поиск начальника в рамках отдела
        if obj.department:
            chief = Employee.objects.filter(
                department=obj.department,
                is_chief=True
            ).exclude(id=obj.id).first()
            if chief and chief.id != obj.id:
                return {
                    "id": chief.id,
                    "user_name": chief.user_name,
                    "user_surename": chief.user_surename,
                    "user_patronymic": chief.user_patronymic,
                    "user_image": chief.user_image.url if chief.user_image else None
                }

        # 2. Если нет шефа в отделе — ищем по subordination
        if obj.subordination:
            try:
                fallback_chief = Employee.objects.get(id=obj.subordination.id)
                if fallback_chief.id != obj.id:
                    return {
                        "id": fallback_chief.id,
                        "user_name": fallback_chief.user_name,
                        "user_surename": fallback_chief.user_surename,
                        "user_patronymic": fallback_chief.user_patronymic,
                        "user_image": fallback_chief.user_image.url if fallback_chief.user_image else None
                    }
            except Employee.DoesNotExist:
                pass

        return None




class EmployeeSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'display_name', 'title', 'department', 'last_ad_check', 'last_logout']
        
class EmployeeSerializerLight(serializers.ModelSerializer):
    #subordination = SubordinationSerializer()                                         
    #region = RegionSerializer()
    #department = DepartmentSerializer()
    sector = SectorSerializer()
    position = PositionSerializer()

    class Meta:
        model = Employee
        fields = '__all__'        




# Region
class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'
        
class RegionDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegionDepartment
        fields = '__all__'

class RegionPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegionPosition
        fields = '__all__'
        
class RegionEmployeeSerializer(serializers.ModelSerializer):
    region = RegionSerializer()
    department = RegionDepartmentSerializer()
    position = RegionPositionSerializer()

    class Meta:
        model = RegionEmployee
        fields = '__all__'   


class RegionEmployeeSerializerLigth(serializers.ModelSerializer):
    #region = RegionSerializer()
    department = RegionDepartmentSerializer()
    position = RegionPositionSerializer()

    class Meta:
        model = RegionEmployee
        fields = '__all__'       