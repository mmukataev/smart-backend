from django.db import models
from django.core.validators import FileExtensionValidator
# Create your models here.

#class User(models.Model):
class SmartApaUser(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
        ('superadmin', 'Super Admin'),
    ]

    login = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    display_name = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)

    last_ad_check = models.DateTimeField(null=True, blank=True)
    blocked_until = models.DateTimeField(null=True, blank=True)
    bad_pwd_count = models.IntegerField(default=0)

    last_login = models.DateTimeField(null=True, blank=True)
    last_logout = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    # This will exist only in memory, not in DB
    _object_guid = None  

    @property
    def object_guid(self):
        return self._object_guid

    @object_guid.setter
    def object_guid(self, value):
        self._object_guid = value

    class Meta:
        db_table = 'smart_apa_user_role'
        verbose_name = "Smart Apa User"
        verbose_name_plural = "1. Smart Apa Users"
        
    def __str__(self):
        return f"{self.display_name or self.login} ({self.role})"

# byuropass.apa.kz
class ByuropassUserRole(models.Model):
    ROLE_CHOICES = [
        ('usercreatedoc', 'User Create Doc'),
        ('signdoc', 'Sign Doc'),
        ('signdoc_security', 'Sign Doc Security'),
        ('us_pos', 'Us Pos'),
        ('admin', 'Admin'),
        ('superadmin', 'Super Admin'),
    ]

    login = models.CharField(max_length=150, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='usercreatedoc')

    class Meta:
        db_table = 'byuropass_user_role'
        verbose_name = "Byuropass User Access Role"
        verbose_name_plural = "2. Byuropass User Access Roles"

    def __str__(self):
        return f"{self.login} ({self.role})"


# reg.apa.kz
class RegApaUserRole(models.Model):
    ROLE_CHOICES = [
        (2, 'Admin'),
        (4, 'Fiz'),
        (6, 'TIKAdmin'),
    ]
    
    REGION_CHOICES = [
        (1,'AST'),
        (2,'ALM'),
        (3,'ShYM'),
        (4,'AKM'),
        (5,'AKT'),
        (6,'ALO'),
        (7,'ATR'),
        (8,'SHKO'),
        (9,'ZHM'),
        (10,'BKO'),
        (11,'KRG'),
        (12,'KST'),
        (13,'KZL'),
        (14,'MNG'),
        (15,'PVL'),
        (16,'SKO'),
        (17,'TRK'),
        (18,'ABI'),
        (19,'JTS'),
        (40,'ULT'),
    ]
    
    login = models.CharField(max_length=150, unique=True)
    #role = models.CharField(max_length=50, choices=ROLE_CHOICES, default=4)
    role = models.IntegerField(choices=ROLE_CHOICES, default=4)
    #region = models.CharField(max_length=20, choices=REGION_CHOICES, default=0)
    region = models.IntegerField(choices=REGION_CHOICES, default=0)

    class Meta:
        db_table = 'regapa_user_role'
        verbose_name = "RegApa User Access Role"
        verbose_name_plural = "3. RegApa User Access Roles"

    def __str__(self):
        return f"{self.login} ({self.role})"


# admission.apa.kz
class AdmissionUserRole(models.Model):
    ROLE_CHOICES = [
        ('tech_secretary', 'Tech Secretary'),
        ('candidate', 'Candidate'),
        ('videointerview_expert', 'Videointerview Expert'),
        ('essay_expert', 'Essay Expert'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    ]

    login = models.CharField(max_length=150, unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='tech_secretary')

    class Meta:
        db_table = 'admission_user_role'
        verbose_name = "Admission User Access Role"
        verbose_name_plural = "4. Admission User Access Roles"

    def __str__(self):
        return f"{self.login} ({self.role})"
        
# regtesting.apa.kz
class RegtestingUserRole(models.Model):
    ROLE_CHOICES = [
        ('pm_candidate', 'Pm Candidate'),
        ('hr_candidate', 'Hr Candidate'),
        ('mzd_candidate', 'Mzd Candidate'),
        ('pm_admin', 'Pm Admin'),
        ('hr_admin', 'Hr Admin'),
        ('mzd_admin', 'Mzd Admin'),
    ]

    login = models.CharField(max_length=150, unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='pm_candidate')

    class Meta:
        db_table = 'regtesting_user_role'
        verbose_name = "Regtesting User Access Role"
        verbose_name_plural = "5. Regtesting User Access Roles"

    def __str__(self):
        return f"{self.login} ({self.role})"    


# icademium.apa.kz
class IcademiumUserRole(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('graduate', 'Graduate'),
        ('viewer', 'Viewer'),
        ('tech_secretary', 'Tech Secretary'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    ]

    login = models.CharField(max_length=150, unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='student')

    class Meta:
        db_table = 'icademium_user_role'
        verbose_name = "Icademium User Access Role"
        verbose_name_plural = "6. Icademium User Access Roles"

    def __str__(self):
        return f"{self.login} ({self.role})"         

#class Employee(models.Model):
#    job_position = models.CharField(max_length=255)  # Должность сотрудника
#    fio = models.CharField(max_length=255)  # ФИО сотрудника
#    id_department = models.IntegerField()  # ID департамента
#
#    def __str__(self):
#        return f"{self.fio} - {self.job_position}" 
#
#class Department(models.Model):
#    name = models.CharField(max_length=255, verbose_name="Название отдела")
#
#    def __str__(self):
#        return self.name
#
#    class Meta:
#        verbose_name = "Отдел"
#        verbose_name_plural = "Отделы"
#        ordering = ['name']

# Employee Subordination
class Subordination(models.Model):
    full_name = models.CharField(max_length=100, blank=True, null=True)
    kz = models.CharField(max_length=100)
    ru = models.CharField(max_length=100, blank=True, null=True)
    user_image = models.ImageField(
        upload_to='subordination/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
    )

    class Meta:
        verbose_name = "Subordination"
        verbose_name_plural = "7.1. Employees Subordination Table"

    def __str__(self):
        #return self.name 
        return self.kz 
        


# Employee Department        
class Department(models.Model):
    subordination = models.ForeignKey(Subordination, on_delete=models.SET_NULL, null=True)
    kz = models.CharField(max_length=100)
    ru = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "7.3. Employees Department Table"

    def __str__(self):
        return self.kz

# Employee Sector        
class Sector(models.Model):
    kz = models.CharField(max_length=100)
    ru = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = "Sector"
        verbose_name_plural = "7.4. Employees Sector Table"

    def __str__(self):
        return self.kz        

# Employee Position
class Position(models.Model):
    kz = models.CharField(max_length=100)
    ru = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Position"
        verbose_name_plural = "7.5. Employees Position Table"
        
    def __str__(self):
        return self.kz

# Employee class
# class Employee(models.Model):
#     user_name = models.CharField(max_length=100)
#     user_surename = models.CharField(max_length=100)
#     user_patronymic = models.CharField(max_length=100, blank=True, null=True)
#     user_phone = models.CharField(max_length=100, blank=True, null=True)
#     user_image = models.CharField(max_length=200, blank=True, null=True)
#     user_email = models.CharField(max_length=100, blank=True, null=True)
#     subordination = models.ForeignKey(Subordination, on_delete=models.SET_NULL, null=True)
#     #region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
#     department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
#     sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True)
#     position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True)

#     class Meta:
#         verbose_name = "Employee"
#         verbose_name_plural = "7. Employees Table"

#     def __str__(self):
#         return f"{self.user_name} {self.user_surename}"     




class Employee(models.Model):
    user_name = models.CharField(max_length=100)
    user_surename = models.CharField(max_length=100)
    user_patronymic = models.CharField(max_length=100, blank=True, null=True)
    user_phone = models.CharField(max_length=100, blank=True, null=True)
    user_image = models.ImageField(
        upload_to='employee/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
    )

    user_email = models.CharField(max_length=100, blank=True, null=True)

    subordination = models.ForeignKey('Subordination', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)
    sector = models.ForeignKey('Sector', on_delete=models.SET_NULL, null=True, blank=True)
    position = models.ForeignKey('Position', on_delete=models.SET_NULL, null=True, blank=True)
    birth_date = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    work_start_date = models.DateField(blank=True, null=True, verbose_name="Дата начала работы")
    is_chief = models.BooleanField(default=False, verbose_name="Является начальником")
    is_sector_head = models.BooleanField(default=False, verbose_name="Заведующий сектором") 

    # Связь с UserRole по user_email = login
    # user_role = models.ForeignKey(
    #     UserRole,
    #     to_field='login',
    #     db_column='user_email',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name='employees'
    # )

    class Meta:
        db_table = 'smart_apa_api_employee'
        verbose_name = "Employee"
        verbose_name_plural = "7. Employees Table"

    def __str__(self):
        return f"{self.user_name} {self.user_surename}"
        

# Region Region
class Region(models.Model):
    kz = models.CharField(max_length=200)
    ru = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = "Regions"
        verbose_name_plural = "8.1. Regions Table"

    def __str__(self):
        return self.kz        
        
# Region Department        
class RegionDepartment(models.Model):
    kz = models.CharField(max_length=100)
    ru = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Region Department"
        verbose_name_plural = "8.2. Region Departments Table"

    def __str__(self):
        return self.kz

# Region Position
class RegionPosition(models.Model):
    kz = models.CharField(max_length=100)
    ru = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Region Positions"
        verbose_name_plural = "8.3. Region Positions Table"
        
    def __str__(self):
        return self.kz

# Region Employee
class RegionEmployee(models.Model):
    user_name = models.CharField(max_length=100)
    user_surename = models.CharField(max_length=100)
    user_patronymic = models.CharField(max_length=100, blank=True, null=True)
    user_phone = models.CharField(max_length=100, blank=True, null=True)
    user_image = models.CharField(max_length=200, blank=True, null=True)
    user_email = models.CharField(max_length=100, blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(RegionDepartment, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.ForeignKey(RegionPosition, on_delete=models.SET_NULL, null=True)


    class Meta:
        verbose_name = "Region Employee"
        verbose_name_plural = "8. Region Employees Table"

    def __str__(self):
        return f"{self.user_name} {self.user_surename}"         