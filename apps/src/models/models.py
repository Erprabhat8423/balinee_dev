from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'
        
class TblClContactNumbers(models.Model):
    student_id = models.IntegerField()
    country_code = models.CharField(max_length=10)
    contact_type = models.IntegerField()
    contact_type_name = models.CharField(max_length=25, blank=True, null=True)
    contact_number = models.CharField(max_length=15)
    is_primary = models.IntegerField()
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_contact_numbers'

class SpApprovalStatus(models.Model):
    row_id = models.IntegerField()
    model_name = models.CharField(max_length=100)
    initiated_by_id = models.IntegerField()
    initiated_by_name = models.CharField(max_length=255)
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=255)
    role_id = models.IntegerField()
    sub_module_id = models.IntegerField()
    permission_id = models.IntegerField()
    permission_slug = models.CharField(max_length=25)
    level_id = models.IntegerField()
    level = models.CharField(max_length=25)
    status = models.IntegerField()
    final_status_user_id = models.IntegerField(null=True)
    final_status_user_name = models.CharField(max_length=255, null=True)
    final_update_date_time = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_approval_status'

class SpPasswordResets(models.Model):

    email = models.CharField(max_length=100,blank=True, null=True)

    auth_token = models.CharField(max_length=100,blank=True, null=True)

    mobile = models.CharField(max_length=10,blank=True, null=True)

    otp = models.IntegerField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)



    class Meta:

        managed = False

        db_table = 'sp_password_resets'

class SpActivityLogs(models.Model):
    module = models.CharField(max_length=100, blank=True, null=True)
    sub_module = models.CharField(max_length=100, blank=True, null=True)
    heading = models.TextField()
    activity = models.TextField()
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=150)
    icon = models.CharField(max_length=100, blank=True, null=True)
    platform = models.CharField(max_length=50)
    platform_icon = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_activity_logs'



class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, on_delete=models.CASCADE)
    permission = models.ForeignKey('AuthPermission', on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', on_delete=models.CASCADE)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    group = models.ForeignKey(AuthGroup, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    permission = models.ForeignKey(AuthPermission, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)

class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class SpAttendanceGroups(models.Model):
    attendance_group = models.CharField(max_length=100)
    start_time = models.CharField(max_length=100)
    end_time = models.CharField(max_length=100)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_attendance_groups'


class SpCities(models.Model):
    state = models.ForeignKey('SpStates', on_delete=models.CASCADE)
    state_name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_cities'



class SpContactTypes(models.Model):
    contact_type = models.CharField(max_length=100)
    status = models.IntegerField()
    create_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_contact_types'


class SpCountries(models.Model):
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_countries'


class SpDepartments(models.Model):
    organization = models.ForeignKey('SpOrganizations', on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=150)
    department_name = models.CharField(max_length=100)
    landline_country_code = models.CharField(max_length=10)
    landline_state_code = models.CharField(max_length=10)
    landline_number = models.CharField(max_length=15)
    extension_number = models.CharField(max_length=10)
    mobile_country_code = models.CharField(max_length=10)
    mobile_number = models.CharField(max_length=15)
    email = models.CharField(max_length=50)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_departments'


class SpDriverAddresses(models.Model):
    user_id = models.IntegerField()
    type = models.CharField(max_length=100)
    address_line_1 = models.CharField(max_length=250)
    address_line_2 = models.CharField(max_length=250, blank=True, null=True)
    country_id = models.IntegerField()
    country_name = models.CharField(max_length=100)
    state_id = models.IntegerField()
    state_name = models.CharField(max_length=100)
    city_id = models.IntegerField()
    city_name = models.CharField(max_length=100)
    pincode = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_driver_addresses'


class SpDriverBasicDetails(models.Model):
    driver_id = models.IntegerField()
    father_name = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=25, blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    aadhaar_nubmer = models.CharField(max_length=15, blank=True, null=True)
    aadhaar_document = models.CharField(max_length=255, blank=True, null=True)
    dl_number = models.CharField(max_length=50, blank=True, null=True)
    dl_document = models.CharField(max_length=255, blank=True, null=True)
    date_of_joining = models.DateField(blank=True, null=True)
    personal_email = models.CharField(max_length=50, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_driver_basic_details'


class SpDriverContactNumbers(models.Model):
    user_id = models.IntegerField()
    country_code = models.CharField(max_length=10)
    contact_type = models.IntegerField()
    contact_type_name = models.CharField(max_length=25, blank=True, null=True)
    contact_number = models.CharField(max_length=15)
    is_primary = models.IntegerField()
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_driver_contact_numbers'


class SpDrivers(models.Model):
    salutation = models.CharField(max_length=10)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    primary_contact_number = models.CharField(max_length=25)
    profile_image = models.CharField(max_length=100, blank=True, null=True)
    device_id = models.CharField(max_length=50, blank=True, null=True)
    firebase_token = models.CharField(max_length=255, blank=True, null=True)
    web_auth_token = models.CharField(max_length=255, blank=True, null=True)
    auth_otp = models.CharField(max_length=10, blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    last_ip = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.CharField(max_length=100, blank=True, null=True)
    longitude = models.CharField(max_length=100, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_drivers'

class SpFavorites(models.Model):
    user = models.ForeignKey('SpUsers', on_delete=models.CASCADE)
    favorite = models.CharField(max_length=100, blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_favorites'


class SpFuelType(models.Model):
    fuel_type = models.CharField(max_length=100)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_fuel_type'


class SpHolidayTypes(models.Model):
    holiday_type = models.CharField(max_length=100)
    status = models.IntegerField()        
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_holiday_types'


class SpHolidays(models.Model):
    holiday_type_id = models.IntegerField()
    holiday_type = models.CharField(max_length=100)
    holiday = models.CharField(max_length=100)
    organization_id = models.IntegerField()
    organization_name = models.CharField(max_length=150)
    applicable_to = models.JSONField(blank=True, null=True)
    start_date = models.DateField()
    
    start_time = models.CharField(max_length=10, blank=True, null=True)
    end_date = models.DateField()
    end_time = models.CharField(max_length=10, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    approval_description = models.TextField(blank=True, null=True)
    document = models.TextField(blank=True, null=True)
    status = models.IntegerField()
    holiday_status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_holidays'



class SpInsuranceCoverage(models.Model):
    insurance_coverage = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'sp_insurance_coverage'


class SpLeavePolicies(models.Model):
    leave_policy = models.CharField(max_length=150)
    status = models.IntegerField()
    policy_status = models.CharField(max_length=20)
    organization_id = models.IntegerField()
    organization_name = models.CharField(max_length=150)
    policy_description = models.CharField(max_length=150)
    approval_description = models.TextField(blank=True, null=True)
    document = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_leave_policies'


class SpLeavePolicyDetails(models.Model):
    leave_policy_id = models.IntegerField()
    leave_type_id = models.IntegerField()
    year_leave_count = models.FloatField()
    month_leave_count = models.FloatField()
    consecutive_leave = models.FloatField()
    is_salary_affecting = models.IntegerField()
    is_carry_forward = models.IntegerField()
    is_halfday_included = models.IntegerField()
    
    apply_leave_before = models.IntegerField(blank=True, null=True)
    is_fraction_leave = models.IntegerField(default=0)
    is_avial_advance_leave = models.IntegerField(default=0)
    is_document_required = models.IntegerField(default=0)
    
    can_swipe = models.IntegerField()
    swipeable_leave_types = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_leave_policy_details'

class SpLeaveTypeDocuments(models.Model):
    leave_type_id = models.IntegerField()
    document = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'sp_leave_type_documents'


class SpLeaveTypes(models.Model):
    leave_type = models.CharField(max_length=50)
    alias = models.CharField(max_length=20)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_leave_types'

class SpLicenseCategory(models.Model):
    license_category = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'sp_license_category'

class SpModulePermissions(models.Model):
    module_id = models.IntegerField(blank=True, null=True)
    sub_module_id = models.IntegerField(blank=True, null=True)
    permission_id = models.IntegerField(blank=True, null=True)
    permission_slug = models.CharField(max_length=100)
    workflow = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_module_permissions'


class SpModules(models.Model):
    module_name = models.CharField(max_length=100)
    link = models.CharField(max_length=100, blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_modules'

class SpOdoMeter(models.Model):
    driver_id = models.IntegerField()
    vehicle_id = models.IntegerField()
    odo_meter_pic = models.CharField(max_length=150, blank=True, null=True)
    odo_meter_reading = models.IntegerField()
    fuel_quantity_ltrs = models.FloatField()
    fuel_status = models.CharField(max_length=20)
    card_no = models.CharField(max_length=50)
    latitude = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)
    date_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_odo_meter'

class SpUserModulePermissions(models.Model):
    user_id = models.IntegerField()
    module_id = models.IntegerField(blank=True, null=True)
    sub_module_id = models.IntegerField(blank=True, null=True)
    permission_id = models.IntegerField(blank=True, null=True)
    permission_slug = models.CharField(max_length=100)
    workflow = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_module_permissions'


class SpOrganizations(models.Model):
    organization_code = models.CharField(max_length=22)
    organization_name = models.CharField(max_length=150)
    alias = models.CharField(max_length=100, blank=True, null=True)
    landline_country_code = models.CharField(max_length=10)
    landline_state_code = models.CharField(max_length=10)
    landline_number = models.CharField(max_length=15)
    mobile_country_code = models.CharField(max_length=10)
    mobile_number = models.CharField(max_length=15)
    email = models.CharField(max_length=50)
    address = models.TextField(blank=True, null=True)
    pincode = models.CharField(max_length=8, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_organizations'

class SpPayBands(models.Model):
    pay_band = models.CharField(max_length=100)
    pay_band_code = models.CharField(max_length=100)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_pay_bands'


class SpPermissionWorkflowRoles(models.Model):
    sub_module_id = models.IntegerField()
    permission_id = models.IntegerField()
    level_id = models.IntegerField()
    workflow_level_dept_id = models.IntegerField(blank=True, null=True)
    workflow_level_dept_name = models.CharField(max_length=100, blank=True, null=True)
    workflow_level_role_id = models.IntegerField()
    workflow_level_role_name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'sp_permission_workflow_roles'


class SpPermissionWorkflows(models.Model):
    module_id = models.IntegerField(blank=True, null=True)
    sub_module_id = models.IntegerField()
    permission_id = models.IntegerField()
    permission_slug = models.CharField(max_length=100)
    level_id = models.IntegerField()
    level = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_permission_workflows'

class SpPermissions(models.Model):
    permission = models.CharField(max_length=100)
    slug = models.CharField(max_length=150)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_permissions'



class SpRoleEntityMapping(models.Model):
    entity_type = models.CharField(max_length=100)
    role_id = models.IntegerField()
    entity_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'sp_role_entity_mapping'
        
class SpRolePermissions(models.Model):
    role = models.ForeignKey('SpRoles', on_delete=models.CASCADE)
    module = models.ForeignKey(SpModules, on_delete=models.CASCADE, blank=True, null=True)
    sub_module = models.ForeignKey('SpSubModules', on_delete=models.CASCADE, blank=True, null=True)
    permission = models.ForeignKey(SpPermissions, on_delete=models.CASCADE, blank=True, null=True)
    permission_slug = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_role_permissions'


class SpRoleWorkflowPermissions(models.Model):
    role_id = models.IntegerField()
    module_id = models.IntegerField(blank=True, null=True)
    sub_module_id = models.IntegerField()
    permission_id = models.IntegerField()
    permission_slug = models.CharField(max_length=100)
    level_id = models.IntegerField()
    level = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    workflow_level_dept_id = models.IntegerField(null=True)
    workflow_level_role_id = models.IntegerField()
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_role_workflow_permissions'


class SpRoles(models.Model):
    organization = models.ForeignKey(SpOrganizations, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=100)
    department = models.ForeignKey(SpDepartments, on_delete=models.CASCADE)
    department_name = models.CharField(max_length=100)
    role_name = models.CharField(max_length=100)
    reporting_department_id = models.IntegerField(null=True)
    reporting_department_name = models.CharField(max_length=100,null=True)
    reporting_role_id = models.IntegerField(null=True)
    reporting_role_name = models.CharField(max_length=100,null=True)
    responsibilities = models.TextField(blank=True, null=True)
    is_outsider = models.IntegerField(default=0)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_roles'

class SpRoleActivities(models.Model):
    role_id = models.IntegerField()
    activity = models.TextField()
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_role_activities'



class SpSalaryAdditionTypes(models.Model):
    addition = models.CharField(max_length=100)
    addition_basis = models.CharField(max_length=100)
    addition_amount = models.IntegerField()
    addition_percent_on = models.CharField(max_length=100, blank=True, null=True)
    addition_limit = models.IntegerField()
    addition_upper_limit = models.FloatField()
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_salary_addition_types'


class SpSalaryDeductionTypes(models.Model):
    deduction = models.CharField(max_length=100)
    deduction_basis = models.CharField(max_length=100)
    deduction_amount = models.IntegerField()
    deduction_percent_on = models.CharField(max_length=100, blank=True, null=True)
    deduction_limit = models.IntegerField()
    deduction_upper_limit = models.FloatField()
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_salary_deduction_types'



class SpStates(models.Model):
    country = models.ForeignKey(SpCountries, on_delete=models.CASCADE)
    country_name = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_states'


class SpSubModules(models.Model):
    module = models.ForeignKey(SpModules, on_delete=models.CASCADE)
    module_name = models.CharField(max_length=100)
    sub_module_name = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_sub_modules'

class SpSubmodulePermissionWorkflows(models.Model):
    sub_module_id = models.IntegerField()
    permission_id = models.IntegerField()
    permission_slug = models.CharField(max_length=100)
    level_id = models.IntegerField()
    level = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_submodule_permission_workflows'



class UserManager(BaseUserManager):
    def create_user(self, user, password=None):
        """
        Creates and saves a User with the given username and password.
        """
        if not user:
            raise ValueError('Error: The User you want to create must have an username, try again')

        my_user = self.model(
            user=self.model.normalize_username(user)
        )
    
        my_user.set_password(password)
        my_user.save(using=self._db)
        return my_user

    def create_staffuser(self, user, password):
        """
        Creates and saves a staff user with the given username and password.
        """
        my_user = self.create_user(
            user,
            password=password,
        )
        my_user.staff = True
        my_user.save(using=self._db)
        return my_user

    def create_superuser(self, user, password):
        """
        Creates and saves a superuser with the given username and password.
        """
        my_user = self.create_user(
            user,
            password=password,
        )
        my_user.staff = True
        my_user.admin = True
        my_user.save(using=self._db)
        return my_user

class SpUserRolePermissions(models.Model):
    user = models.ForeignKey('SpUsers', models.DO_NOTHING)
    role_id = models.IntegerField()
    module_id = models.IntegerField(blank=True, null=True)
    sub_module_id = models.IntegerField(blank=True, null=True)
    permission_id = models.IntegerField(blank=True, null=True)
    permission_slug = models.CharField(max_length=100)
    workflow = models.TextField(blank=True, null=True)
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_role_permissions'


class SpUserRoleWorkflowPermissions(models.Model):
    user = models.ForeignKey('SpUsers', models.DO_NOTHING)
    role_id = models.IntegerField()
    module_id = models.IntegerField(blank=True, null=True)
    sub_module_id = models.IntegerField()
    permission_id = models.IntegerField()
    permission_slug = models.CharField(max_length=100)
    level_id = models.IntegerField()
    level = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    workflow_level_dept_id = models.IntegerField()
    workflow_level_role_id = models.IntegerField()
    status = models.IntegerField()
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_role_workflow_permissions'

               
class SpUsers(AbstractBaseUser):
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'official_email'

    alias = models.CharField(max_length=255)
    salutation = models.CharField(max_length=10)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50,blank=True, null=True)
    last_name = models.CharField(max_length=50)
    store_name = models.CharField(max_length=255, blank=True, null=True)
    store_image = models.CharField(max_length=100, blank=True, null=True)
    official_email = models.CharField(unique=True,max_length=100)
    primary_contact_number = models.CharField(max_length=25)
    password = models.CharField(max_length=255)
    plain_password = models.CharField(max_length=50)
    emp_sap_id = models.CharField(max_length=50)
    organization_id = models.IntegerField()
    organization_name = models.CharField(max_length=222, blank=True, null=True)
    department_id = models.IntegerField()
    department_name = models.CharField(max_length=222, blank=True, null=True)
    role_id = models.IntegerField()
    role_name = models.CharField(max_length=222)
    reporting_to_id = models.IntegerField()
    reporting_to_name = models.CharField(max_length=255)
    profile_image = models.CharField(max_length=100, blank=True, null=True)
    device_id = models.CharField(max_length=50, blank=True, null=True)
    firebase_token = models.CharField(max_length=255, blank=True, null=True)
    web_auth_token = models.CharField(max_length=255, blank=True, null=True)
    auth_otp = models.CharField(max_length=10, blank=True, null=True)
    last_login = models.DateTimeField(null=True)
    last_ip = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(default=1)
    user_type = models.IntegerField(default=0)
    is_distributor = models.IntegerField(default=0)
    is_super_stockist = models.IntegerField(default=0)
    is_retailer = models.IntegerField(default=0)
    is_tagged = models.IntegerField(default=0)
    latitude = models.CharField(max_length=100, blank=True, null=True)
    longitude = models.CharField(max_length=100, blank=True, null=True)
    self_owned = models.IntegerField(default=0)
    api_token = models.CharField(max_length=255, blank=True, null=True)
    
    finger_iso_1 = models.TextField(blank=True, null=True)
    finger_iso_2 = models.TextField(blank=True, null=True)
    aten_timing = models.CharField(max_length=100, blank=True, null=True)
    periphery = models.CharField(max_length=100, blank=True, null=True)
    fencing_timing = models.CharField(max_length=100, blank=True, null=True)
    attendence_mode = models.CharField(max_length=100, blank=True, null=True)
    id_card_attempts_left = models.IntegerField(default=3)
    is_id_card_generated = models.IntegerField(default=0)
    id_card_link = models.CharField(max_length=255, blank=True, null=True)
    id_card_created_at = models.DateTimeField(blank=True, null=True)
    login_status = models.IntegerField(default=0)
    created_by = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    class Meta:
        managed = False
        db_table = 'sp_users'

class SpVehicleClass(models.Model):
    vehicle_class = models.CharField(max_length=50)
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'sp_vehicle_class'


class SpVehicleFinancer(models.Model):
    financer = models.CharField(max_length=50)
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'sp_vehicle_financer'


class SpVehicleFitnessDetails(models.Model):
    vehicle_id = models.IntegerField()
    application_no = models.CharField(max_length=100, blank=True, null=True)
    inspection_date = models.DateField(blank=True, null=True)
    fitness_valid_till = models.DateField(blank=True, null=True)
    copy_of_fitness_certificate = models.CharField(max_length=100, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_vehicle_fitness_details'


class SpVehicleInsuranceDetails(models.Model):
    vehicle_id = models.IntegerField()
    name_of_insurer = models.CharField(max_length=50, blank=True, null=True)
    date_of_insurance = models.DateField(blank=True, null=True)
    valid_till = models.DateField(blank=True, null=True)
    premium_amount = models.FloatField(blank=True, null=True)
    total_sum_insured = models.FloatField(blank=True, null=True)
    insurance_copy = models.CharField(max_length=100, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_vehicle_insurance_details'


class SpVehicleInsurer(models.Model):
    name_of_insurer = models.CharField(max_length=50)
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'sp_vehicle_insurer'


class SpVehicleMaker(models.Model):
    maker_name = models.CharField(max_length=50)
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'sp_vehicle_maker'


class SpVehicleMakerClassification(models.Model):
    classification = models.CharField(max_length=50)
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'sp_vehicle_maker_classification'


class SpVehiclePollutionDetails(models.Model):
    vehicle_id = models.IntegerField()
    certificate_sr_no = models.CharField(max_length=50, blank=True, null=True)
    date_of_registration = models.DateField(blank=True, null=True)
    pollution_valid_till = models.DateField(blank=True, null=True)
    copy_of_certificate = models.CharField(max_length=100, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_vehicle_pollution_details'


class SpVehicleRegistrationDetails(models.Model):
    vehicle_id = models.IntegerField()
    owner_name = models.CharField(max_length=50, blank=True, null=True)
    registration_number = models.CharField(max_length=50)
    registered_address = models.CharField(max_length=100, blank=True, null=True)
    rto = models.CharField(max_length=50, blank=True, null=True)
    registration_fees_amount = models.FloatField(blank=True, null=True)
    registration_date = models.DateField(blank=True, null=True)
    registration_valid_till = models.DateField(blank=True, null=True)
    registration_copy = models.CharField(max_length=100, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_vehicle_registration_details'


class SpVehicleRoadpermitDetails(models.Model):
    vehicle_id = models.IntegerField()
    permit_no = models.CharField(max_length=50,blank=True, null=True)
    permit_registration_date = models.DateField(blank=True, null=True)
    permit_valid_till = models.DateField(blank=True, null=True)
    permitted_route = models.CharField(max_length=50,blank=True, null=True)
    purpose = models.CharField(max_length=100,blank=True, null=True)
    insurance_copy = models.CharField(max_length=100, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_vehicle_roadpermit_details'


class SpVehicleWarrantyDetails(models.Model):
    vehicle_id = models.IntegerField()
    overall_warranty_period = models.IntegerField(blank=True, null=True)
    component_warranty = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_vehicle_warranty_details'


class SpVehicles(models.Model):
    user_id = models.IntegerField(null=True)
    registration_number = models.CharField(max_length=255, blank=True, null=True)
    registered_address = models.TextField(blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    ownership_type = models.CharField(max_length=50)
    dealer_name = models.CharField(max_length=50, blank=True, null=True)
    dealer_address = models.CharField(max_length=100, blank=True, null=True)
    dealer_contact_no = models.CharField(max_length=10, blank=True, null=True)
    owner_name = models.CharField(max_length=50, blank=True, null=True)
    owner_address = models.CharField(max_length=100, blank=True, null=True)
    owner_contact_no = models.CharField(max_length=10, blank=True, null=True)
    vehicle_type = models.CharField(max_length=20, blank=True, null=True)
    class_of_vehicle = models.CharField(max_length=50, blank=True, null=True)
    maker_name = models.CharField(max_length=50, blank=True, null=True)
    year_of_manufacture = models.TextField(blank=True, null=True)  # This field type is a guess.
    chassis_no = models.CharField(max_length=50, blank=True, null=True)
    engine_no = models.CharField(max_length=50, blank=True, null=True)
    horsepower = models.CharField(max_length=50, blank=True, null=True)
    cubic_capacity = models.FloatField(blank=True, null=True)
    maker_classification = models.CharField(max_length=50, blank=True, null=True)
    seating_capacity_standard = models.IntegerField(null=True)
    seating_capacity_max = models.IntegerField(null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    ac_fitted = models.CharField(max_length=10, blank=True, null=True)
    finance = models.CharField(max_length=10, blank=True, null=True)
    financer_name = models.CharField(max_length=50, blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    fuel_type = models.CharField(max_length=22,blank=True, null=True)
    purchase_amount = models.FloatField(blank=True, null=True)
    driver_id = models.CharField(max_length=55,  null=True)
    dl_expiry =  models.DateField(null=True)
    driver_name = models.CharField(max_length=255, blank=True, null=True)
    route_id = models.IntegerField(blank=True, null=True)
    route_name = models.CharField(max_length=255, blank=True, null=True)
    incharge_id = models.IntegerField(blank=True, null=True)
    assign_from_date = models.DateField(blank=True, null=True)
    assign_to_date = models.DateField(blank=True, null=True)
    petro_card_id = models.IntegerField(blank=True, null=True)
    sale_letter = models.CharField(max_length=100, blank=True, null=True)
    mileage = models.FloatField(blank=True, null=True)
    vehicle_pic = models.TextField(blank=True, null=True)
    api_token = models.TextField(blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_vehicles'


class SpVehicleTracking(models.Model):
    vehicle_id = models.IntegerField()
    driver_id = models.IntegerField(blank=True, null=True)
    driver_name = models.CharField(max_length=100, blank=True, null=True)
    route_id = models.IntegerField(blank=True, null=True)
    route_name = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.CharField(max_length=25, blank=True, null=True)
    longitude = models.CharField(max_length=25, blank=True, null=True)
    velocity = models.FloatField(blank=True, null=True)
    distance_travelled = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_vehicle_tracking'

class SpWorkflowLevels(models.Model):
    level = models.CharField(max_length=15)
    priority = models.CharField(max_length=10, blank=True, null=True)
    color = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_workflow_levels'



class SpCountryCodes(models.Model):
    country_code = models.CharField(max_length=10)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_country_codes'

class AuthtokenToken(models.Model):
    key  = models.CharField(max_length=40)
    created = models.DateTimeField()
    user_id  = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'authtoken_token'


class TblAdmin(models.Model):
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'tbl_admin'

class TblAttendance(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    student_id = models.IntegerField(blank=True, null=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(blank=True, null=True)
    latitude = models.CharField(max_length=100)
    longitude = models.CharField(max_length=100)
    semester_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_attendance'

class TblBlock(models.Model):
    tehsil_id = models.IntegerField()
    block_name = models.CharField(max_length=100)
    code = models.IntegerField(blank=True, null=True)
    latlong = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_block'


class TblBranch(models.Model):
    college_id = models.IntegerField()
    course_type_id = models.CharField(max_length=255)
    branch = models.CharField(max_length=255)
    branch_code = models.IntegerField(blank=True, null=True)
    alias = models.CharField(max_length=255, blank=True, null=True)
    abbr = models.CharField(max_length=255)
    form_amount = models.IntegerField()
    total_student = models.IntegerField(blank=True, null=True)
    max_student = models.IntegerField(blank=True, null=True)
    total_sem = models.IntegerField(blank=True, null=True)
    total_year = models.IntegerField(blank=True, null=True)
    eligibility = models.CharField(max_length=255, blank=True, null=True)
    course_persuing_id = models.IntegerField(blank=True, null=True)
    is_admission_closed = models.IntegerField(default=0)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_branch'


class TblColleges(models.Model):
    college_name = models.TextField()
    alias = models.CharField(max_length=255)
    college_address = models.TextField()
    college_logo = models.CharField(max_length=255)
    college_contacts = models.CharField(max_length=255, blank=True, null=True)
    whatsapp_link = models.CharField(max_length=255)
    college_website = models.CharField(max_length=255, blank=True, null=True)
    label_strip = models.CharField(max_length=255)
    prospectus = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_colleges'


class TblCountry(models.Model):
    country_name = models.CharField(max_length=15)
    country_code = models.CharField(max_length=15)

    class Meta:
        managed = False
        db_table = 'tbl_country'


class TblCourseTypes(models.Model):
    college_id = models.IntegerField()
    course_type = models.CharField(max_length=255)
    eligibility = models.CharField(max_length=255, blank=True, null=True)
    course_persuing_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(default=1)

    class Meta:
        managed = False
        db_table = 'tbl_course_types'


class TblDistrict(models.Model):
    district_name = models.CharField(max_length=100)
    state_id = models.IntegerField()
    district_id = models.IntegerField(blank=True, null=True)
    latlong = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_district'


class TblEducationDetails(models.Model):
    registration_id = models.IntegerField()
    course_name = models.CharField(max_length=111)
    institute = models.CharField(max_length=255)
    university = models.CharField(max_length=111)
    other_board = models.CharField(max_length=255, blank=True, null=True)
    stream = models.CharField(max_length=111, blank=True, null=True)
    year = models.CharField(max_length=255, blank=True, null=True)
    percent = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_education_details'


class TblFailedPayments(models.Model):
    registration_id = models.IntegerField(blank=True, null=True)
    bank_ref_number = models.CharField(max_length=255, blank=True, null=True)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    payment_mode = models.CharField(max_length=255, blank=True, null=True)
    amount = models.FloatField(blank=True, null=True)
    payment_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbl_failed_payments'


class TblPayments(models.Model):
    registration_id = models.IntegerField()
    bank_ref_number = models.CharField(max_length=255)
    transaction_id = models.CharField(max_length=255)
    payment_mode = models.CharField(max_length=255, blank=True, null=True)
    amount = models.FloatField()
    status = models.IntegerField()
    payment_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbl_payments'


class TblRegistration(models.Model):
    college_id = models.IntegerField()
    first_name = models.CharField(max_length=111)
    middle_name = models.CharField(max_length=111)
    last_name = models.CharField(max_length=111)
    father_name = models.CharField(max_length=111)
    dob = models.DateField()
    primary_contact_no = models.CharField(max_length=55)
    secondary_contact_no = models.CharField(max_length=55)
    email = models.CharField(max_length=255, blank=True, null=True)
    aadhaar_no = models.CharField(max_length=55)
    aadhaar_front_image = models.CharField(max_length=255)
    aadhaar_back_image = models.CharField(max_length=255)
    state_id = models.IntegerField()
    district_id = models.IntegerField()
    tehsil_id = models.IntegerField()
    block = models.CharField(max_length=255)
    village = models.CharField(max_length=255)
    pincode = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField()
    course_persuing_id = models.IntegerField()
    branch_1 = models.CharField(max_length=55)
    status = models.IntegerField()
    created_on = models.DateTimeField()
    otp = models.IntegerField(blank=True, null=True)
    is_otp_expired = models.IntegerField()
    is_paid = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tbl_registration'


class TblSemester(models.Model):
    semester_id = models.CharField(max_length=11)
    sem_name = models.CharField(max_length=222)
    type = models.CharField(max_length=222)

    class Meta:
        managed = False
        db_table = 'tbl_semester'


class TblStates(models.Model):
    country_id = models.IntegerField()
    country_name = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    inter_state = models.IntegerField(blank=True, null=True)
    state_code = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_states'


class TblStudents(models.Model):
    admission_session = models.IntegerField()
    form_no = models.CharField(max_length=50)
    reg_no = models.CharField(unique=True, max_length=222, blank=True, null=True)
    salutation = models.CharField(max_length=10)
    first_name = models.CharField(max_length=111)
    middle_name = models.CharField(max_length=111, blank=True, null=True)
    last_name = models.CharField(max_length=111, blank=True, null=True)
    college_id = models.IntegerField(blank=True, null=True)
    college_name = models.CharField(max_length=222)
    email = models.CharField(max_length=100, blank=True, null=True)
    father_name = models.CharField(max_length=111)
    mother_name = models.CharField(max_length=255, blank=True, null=True)
    teacher_gaurdian_name = models.CharField(max_length=255, blank=True, null=True)
    primary_contact_no = models.CharField(max_length=55, blank=True, null=True)
    password = models.CharField(max_length=255)
    aadhaar_no = models.CharField(max_length=55, blank=True, null=True)
    aadhaar_front_image = models.CharField(max_length=255, blank=True, null=True)
    secondary_phone_no = models.CharField(max_length=15, blank=True, null=True)
    secondary_phone_relative = models.CharField(max_length=200, blank=True, null=True)
    sbat_id = models.CharField(db_column='SBAT_id', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sbat_percentage = models.CharField(db_column='SBAT_percentage', max_length=50, blank=True, null=True)  # Field name made lowercase.
    country_id = models.IntegerField(blank=True, null=True)
    state_id = models.IntegerField(blank=True, null=True)
    district_id = models.IntegerField(blank=True, null=True)
    tehsil_id = models.IntegerField(blank=True, null=True)
    village_id = models.IntegerField(blank=True, null=True)
    address_hno = models.CharField(max_length=255, blank=True, null=True)
    address_locality = models.CharField(max_length=255, blank=True, null=True)
    per_country_id = models.IntegerField(blank=True, null=True)
    per_state_id = models.IntegerField(blank=True, null=True)
    per_district_id = models.IntegerField(blank=True, null=True)
    per_tehsil_id = models.IntegerField(blank=True, null=True)
    per_village_id = models.IntegerField(blank=True, null=True)
    per_address_hno = models.CharField(max_length=255, blank=True, null=True)
    per_address_locality = models.CharField(max_length=255, blank=True, null=True)
    course_type_id = models.IntegerField(blank=True, null=True)
    cros_pincode = models.IntegerField()
    per_pincode = models.IntegerField()
    course_type_name = models.CharField(max_length=100, blank=True, null=True)
    branch_id = models.CharField(max_length=55)
    branch_name = models.CharField(max_length=100, blank=True, null=True)
    year_id = models.IntegerField(blank=True, null=True)
    semester_id = models.CharField(max_length=22)
    section_id = models.IntegerField(blank=True, null=True)
    finger_iso_1 = models.TextField(blank=True, null=True)
    finger_iso_2 = models.TextField(blank=True, null=True)
    profile_image = models.TextField(blank=True, null=True)
    student_image = models.CharField(max_length=255, blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    is_registered = models.IntegerField()
    registered_date = models.DateTimeField(blank=True, null=True)
    is_mobile_verified = models.IntegerField()
    otp = models.IntegerField(blank=True, null=True)
    is_otp_expired = models.IntegerField()
    id_card_pin = models.IntegerField(blank=True, null=True)
    is_id_card_pin_verified = models.IntegerField()
    is_id_card_generated = models.IntegerField()
    id_card_link = models.CharField(max_length=255, blank=True, null=True)
    id_card_created_at = models.DateTimeField(blank=True, null=True)
    id_card_attempts_left = models.IntegerField(default=3)
    is_paid = models.IntegerField()
    visit_status = models.IntegerField()
    last_visit_datetime = models.DateTimeField(blank=True, null=True)
    latitude = models.CharField(max_length=100, blank=True, null=True)
    longitude = models.CharField(max_length=100, blank=True, null=True)
    status = models.IntegerField()
    created_on = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_students'

class TblClBasicDetails(models.Model):
    student_id = models.IntegerField(unique=True)
    blood_group = models.CharField(max_length=50)
    dob = models.DateField()
    gender = models.CharField(max_length=25)
    caste_category_id = models.IntegerField()
    caste_category = models.CharField(max_length=50)
    privilage_category_id = models.IntegerField()
    privilage_category = models.CharField(max_length=50)
    income_category_id = models.IntegerField()
    income_category = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_basic_details'

class TblClContactTypes(models.Model):
    contact_type = models.CharField(max_length=100)
    status = models.IntegerField()
    create_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_contact_types'

class TblClSection(models.Model):
    section_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_section'


class TblClPrviliageCategory(models.Model):
    prviliage_category = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_prviliage_category'

class TblClCasteCategory(models.Model):
    caste_category = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_caste_category'

class TblClCollegeSession(models.Model):
    session = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_college_session'

class TblClIncomeCategory(models.Model):
    income_category = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_income_category'

class TblTehsil(models.Model):
    district_id = models.IntegerField()
    tehsil_name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, blank=True, null=True)
    latlong = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_tehsil'

class TblUserWebTokens(models.Model):
    user_id = models.IntegerField()
    token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'tbl_user_web_tokens'
        

class TblVerifiedMobile(models.Model):
    mobile_no = models.CharField(max_length=15)
    otp = models.CharField(max_length=22, blank=True, null=True)
    isverified = models.IntegerField(db_column='isVerified')  # Field name made lowercase.
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tbl_verified_mobile'


class TblVillage(models.Model):
    block_id = models.IntegerField()
    village_name = models.CharField(max_length=100)
    village_code = models.IntegerField(blank=True, null=True)
    latlong = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_village'


class TblVisits(models.Model):
    ip = models.CharField(max_length=255)
    page = models.CharField(max_length=255, blank=True, null=True)
    visited_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tbl_visits'

class SpAttributes(models.Model):
    attribute = models.CharField(max_length=50)
    is_active = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'sp_attributes'

class SpRoutes(models.Model):
    state_id = models.IntegerField()
    state_name = models.CharField(max_length=100)
    route = models.CharField(max_length=255)
    status = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SpRoleAttrHiddenFields(models.Model):
    role_id = models.IntegerField()
    attribute_id = models.IntegerField()
    field_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_role_attr_hidden_fields'


class SpRoleAttrOptionalFields(models.Model):
    role_id = models.IntegerField()
    attribute_id = models.IntegerField()
    field_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_role_attr_optional_fields'



class SpBusinessTypes(models.Model):
    business_type = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_business_types'

class SpTags(models.Model):
    tag = models.CharField(max_length=20)
    color = models.CharField(max_length=10, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_tags'


class SpContactTags(models.Model):
    contact_id = models.IntegerField(blank=True, null=True)
    tag_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_contact_tags'


class SpContacts(models.Model):
    type = models.IntegerField()
    company_name = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    profile_picture = models.CharField(max_length=100, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    city = models.IntegerField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gstin = models.CharField(max_length=20, blank=True, null=True)
    spoc = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    designation = models.CharField(max_length=50, blank=True, null=True)
    website = models.CharField(max_length=100, blank=True, null=True)
    linkedin_profile = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_contacts'


class SpRoleAttributes(models.Model):
    role_id = models.IntegerField()
    attribute_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_role_attributes'

class SpRequiredDocuments(models.Model):
    document = models.CharField(max_length=100)
    is_active = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_required_documents'

class SpVehicleTypes(models.Model):
    vehicle_type = models.CharField(max_length=50)
    is_active = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_vehicle_types'

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)        

class SpIncomeCategories(models.Model):
    income_category = models.CharField(max_length=25)
    is_active = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_income_categories'

class SpPrevilegeCategories(models.Model):
    previlege_category = models.CharField(max_length=50)
    is_active = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_previlege_categories'

class SpSessions(models.Model):
    session = models.CharField(max_length=255)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_current = models.IntegerField()
    is_active = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_sessions'

class SpLocations(models.Model):
    name = models.TextField()
    country_id = models.IntegerField(blank=True, null=True)
    state_id = models.IntegerField(blank=True, null=True)
    state = models.CharField(max_length=20, blank=True, null=True)
    city_id = models.IntegerField(blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    landline = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_locations'


class SpYears(models.Model):
    year = models.CharField(max_length=50)
    alias = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_years'

class SpPayGrades(models.Model):
    paygrade_code = models.CharField(max_length=50)
    paygrade = models.FloatField()
    is_active = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_pay_grades'

class SpWorkingHours(models.Model):
    work_from = models.TimeField()
    work_to = models.TimeField()
    is_active = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_working_hours'


class SpAdditionalResponsibilities(models.Model):
    responsibility = models.CharField(max_length=50)
    is_active = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_additional_responsibilities'

class SpBanks(models.Model):
    bank_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_banks'

class SpBankDetails(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    bank_id = models.IntegerField(blank=True, null=True)
    bank_name = models.CharField(max_length=30, blank=True, null=True)
    bank_account_no = models.CharField(max_length=50, blank=True, null=True)
    ifsc_code = models.CharField(max_length=11, blank=True, null=True)
    bank_address = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_bank_details'

class SpUserTags(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    tag_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sp_user_tags'

class SpUserAcademicDetails(models.Model):
    user_id = models.IntegerField()
    admission_procedure_id = models.IntegerField(blank=True, null=True)
    registration_no = models.CharField(max_length=55, blank=True, null=True)
    location_id = models.IntegerField(blank=True, null=True)
    branch_id = models.IntegerField(blank=True, null=True)
    teacher_guardian_id = models.IntegerField(blank=True, null=True)
    teacher_guardian_name = models.CharField(max_length=55, blank=True, null=True)
    date_of_admission = models.DateField(blank=True, null=True)
    year_id = models.CharField(max_length=22, blank=True, null=True)
    semester_id = models.CharField(max_length=55, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_academic_details'


class SpUserBankDetails(models.Model):
    user_id = models.IntegerField()
    bank_id = models.IntegerField(blank=True, null=True)
    bank_name = models.CharField(max_length=50, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    bank_account_no = models.CharField(max_length=20, blank=True, null=True)
    account_holder_name = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_bank_details'


class SpUserBusinessDetails(models.Model):
    user_id = models.IntegerField()
    business_type_id = models.IntegerField(blank=True, null=True)
    business_type = models.CharField(max_length=50, blank=True, null=True)
    contact_persons = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_business_details'


class SpUserDocuments(models.Model):
    user_id = models.IntegerField()
    document_id = models.IntegerField(blank=True, null=True)
    document_name = models.CharField(max_length=100, blank=True, null=True)
    ducument_number = models.CharField(max_length=50, blank=True, null=True)
    document_path = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_documents'


class SpUserFinancialDetails(models.Model):
    user_id = models.IntegerField()
    is_health_insurance = models.IntegerField(default=1)
    health_insurance = models.CharField(max_length=255, blank=True, null=True)
    wage_tax = models.CharField(max_length=50, blank=True, null=True)
    salary_saving_scheme = models.CharField(max_length=50, blank=True, null=True)
    gstin = models.CharField(max_length=20, blank=True, null=True)
    salary_additions = models.CharField(max_length=10, blank=True, null=True)
    salary_deductions = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_financial_details'

class SpUserOfficialDetails(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    location_id = models.IntegerField(blank=True, null=True)
    location = models.CharField(max_length=50, blank=True, null=True)
    department_id = models.IntegerField(blank=True, null=True)
    department = models.CharField(max_length=50, blank=True, null=True)
    designation_id = models.IntegerField(blank=True, null=True)
    designation = models.CharField(max_length=50, blank=True, null=True)
    pay_grade_id = models.IntegerField(blank=True, null=True)
    pay_grade = models.CharField(max_length=20, blank=True, null=True)
    employment_term = models.CharField(max_length=20, blank=True, null=True)
    additional_responsibilities = models.CharField(max_length=50, blank=True, null=True)
    working_hour = models.IntegerField(blank=True, null=True)
    date_of_joining = models.DateField(blank=True, null=True)
    previous_employer = models.CharField(max_length=100, blank=True, null=True)
    years_of_experience = models.IntegerField(blank=True, null=True)
    gstin = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_official_details'


class SpUserPersonalDetails(models.Model):
    user_id = models.IntegerField()
    father_first_name = models.CharField(max_length=50, blank=True, null=True)
    father_last_name = models.CharField(max_length=50, blank=True, null=True)
    mother_first_name = models.CharField(max_length=50, blank=True, null=True)
    mother_last_name = models.CharField(max_length=50, blank=True, null=True)
    spouse_name = models.CharField(max_length=100, blank=True, null=True)
    spouse_employer = models.CharField(max_length=100, blank=True, null=True)
    spouse_work_phone = models.CharField(max_length=15, blank=True, null=True)
    no_of_children = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    place_of_birth = models.CharField(max_length=100, blank=True, null=True)
    martial_status = models.CharField(max_length=15, blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    disability = models.CharField(max_length=100, blank=True, null=True)
    identification_mark = models.CharField(max_length=200, blank=True, null=True)
    caste_category = models.CharField(max_length=20, blank=True, null=True)
    income_category_id = models.IntegerField(blank=True, null=True)
    income_category = models.CharField(max_length=100, blank=True, null=True)
    previlege_category_id = models.IntegerField(blank=True, null=True)
    previlege_category = models.CharField(max_length=100, blank=True, null=True)
    c_country = models.CharField(max_length=10, blank=True, null=True)
    c_state = models.IntegerField(blank=True, null=True)
    c_city = models.IntegerField(blank=True, null=True)
    c_address_line_1 = models.CharField(max_length=100, blank=True, null=True)
    c_address_line_2 = models.CharField(max_length=100, blank=True, null=True)
    c_pincode = models.CharField(max_length=8, blank=True, null=True)
    p_country = models.CharField(max_length=10, blank=True, null=True)
    p_state = models.IntegerField(blank=True, null=True)
    p_city = models.IntegerField(blank=True, null=True)
    p_address_line_1 = models.CharField(max_length=100, blank=True, null=True)
    p_address_line_2 = models.CharField(max_length=100, blank=True, null=True)
    p_pincode = models.CharField(max_length=8, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_personal_details'

class SpUserContacts(models.Model):
    user_id = models.IntegerField()
    contact_type_id = models.IntegerField()
    contact_type = models.CharField(max_length=20)
    contact_number = models.CharField(max_length=10)
    is_primary = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_contacts'

class SpAdmissionProcedureBranches(models.Model):
    admission_procedure_id = models.IntegerField()
    branch_id = models.IntegerField()
    branch = models.CharField(max_length=255)
    semesters = models.CharField(max_length=10, blank=True, null=True)
    years = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_admission_procedure_branches'


class SpAdmissionProcedures(models.Model):
    session_id = models.IntegerField()
    location_id = models.IntegerField()
    procedure_type = models.IntegerField()
    admission_procedure = models.CharField(max_length=100)
    form_fee = models.IntegerField()
    form_starting_number = models.IntegerField()
    form_ending_number = models.IntegerField()
    is_active = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_admission_procedures'

class SpUserBiometricDetails(models.Model):
    user_id = models.IntegerField()
    finger_1 = models.TextField(blank=True, null=True)
    finger_2 = models.TextField(blank=True, null=True)
    finger_3 = models.TextField(blank=True, null=True)
    finger_4 = models.TextField(blank=True, null=True)
    finger_5 = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_biometric_details'

class TblQuestionnaire(models.Model):
    semester = models.IntegerField()
    academic_year = models.IntegerField()
    college_id = models.IntegerField()
    question = models.TextField(blank=False, null=False)
    input_flag = models.BooleanField()
    input_type = models.IntegerField()
    max_value = models.IntegerField(blank=True, null=True)
    max_length = models.IntegerField(blank=True, null=True)
    label = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_questionnaire'

class TblHomeVisit(models.Model):
    faculty_id = models.IntegerField()
    student_id = models.IntegerField()
    registration_no = models.CharField(max_length=112)
    college_id = models.IntegerField()
    guardian_relation = models.CharField(max_length=255)
    mob_no = models.CharField(max_length=15, blank=True, null=True)
    address_hno = models.CharField(max_length=255)
    address_locality = models.CharField(max_length=255)
    state_id = models.IntegerField(blank=True, null=True)
    state_name = models.CharField(max_length=200)
    district_id = models.CharField(max_length=255)
    district_name = models.CharField(max_length=200)
    tehsil_id = models.IntegerField(blank=True, null=True)
    tehsil_name = models.CharField(max_length=200)
    village_id = models.IntegerField(blank=True, null=True)
    village_name = models.CharField(max_length=200, blank=True, null=True)
    pincode = models.CharField(max_length=8, blank=True, null=True)
    semester = models.CharField(max_length=10, blank=True, null=True)
    opinion = models.CharField(max_length=500, blank=True, null=True)
    rating = models.DecimalField(max_digits=4, decimal_places=2)
    field_report = models.CharField(max_length=200, blank=True, null=True)
    selfie_with_parents = models.CharField(max_length=200, blank=True, null=True)
    latitude = models.CharField(max_length=100, blank=True, null=True)
    longitude = models.CharField(max_length=100, blank=True, null=True)
    answers = models.TextField()
    support_staff = models.JSONField(blank=True, null=True)
    visit_audio = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_home_visit'

class TblNewDistrict(models.Model):
    state_id = models.IntegerField()
    district_name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "tbl_new_district"

class TblNewTehsil(models.Model):
    district_id = models.IntegerField()
    tehsil_name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "tbl_new_tehsil"

class TblNewVillage(models.Model):
    tehsil_id = models.IntegerField()
    village_name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "tbl_new_villages"

class TblVisitOtp(models.Model):
    mobile_no = models.IntegerField()
    otp = models.CharField(max_length=50)
    student_id = models.CharField(max_length=50)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'tbl_visit_otp'
        
        
class TblSchoolVisit(models.Model):
    school_name = models.CharField(max_length=255)
    school_image = models.CharField(max_length=255)
    school_contact = models.CharField(max_length=15)
    address_hno = models.CharField(max_length=200)
    address_locality = models.CharField(max_length=200, blank=True, null=True)
    state_id = models.IntegerField(blank=True, null=True)
    state_name = models.CharField(max_length=200)
    district_id = models.IntegerField(blank=True, null=True)
    district_name = models.CharField(max_length=200)
    tehsil_id = models.IntegerField(blank=True, null=True)
    tehsil_name = models.CharField(max_length=200)
    village_id = models.IntegerField(blank=True, null=True)
    village_name = models.CharField(max_length=200)
    pincode = models.IntegerField(blank=True, null=True)
    high_school_students = models.IntegerField(blank=True, null=True)
    latitude = models.CharField(max_length=100)
    longitude = models.CharField(max_length=100)
    selfie = models.CharField(max_length=200)
    support_staff = models.TextField(blank=True, null=True)
    visited_datetime = models.DateTimeField(blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    visited_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_school_visit'

class TblSchoolContact(models.Model):
    school_id = models.IntegerField()
    contact_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    contact_type = models.CharField(max_length=100)
    is_referred = models.IntegerField(default=0)
    referred_by = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_school_contact'


class TblIndividualVisit(models.Model):
    student_name = models.CharField(max_length=200)
    student_image = models.CharField(max_length=200)
    guardian_name = models.CharField(max_length=200)
    student_contact = models.CharField(max_length=15)
    referred_by_teacher = models.CharField(max_length=200)
    referred_by_student = models.CharField(max_length=200)
    branch_id = models.IntegerField()
    branch_name = models.CharField(max_length=200)
    year = models.CharField(max_length=100)
    highschool_in_year = models.IntegerField()
    address_hno = models.CharField(max_length=200)
    address_locality = models.CharField(max_length=200, blank=True, null=True)
    village_id = models.IntegerField()
    address_village = models.CharField(max_length=200)
    tehsil_id = models.IntegerField()
    address_tehsil = models.CharField(max_length=200)
    district_id = models.IntegerField()
    address_district = models.CharField(max_length=200)
    state_id = models.IntegerField()
    address_state = models.CharField(max_length=200)
    pincode = models.IntegerField(blank=True, null=True)
    school_name = models.CharField(max_length=200)
    school_address = models.CharField(max_length=200)
    coaching_name = models.CharField(max_length=200, blank=True, null=True)
    coaching_teacher = models.CharField(max_length=200, blank=True, null=True)
    coaching_address = models.CharField(max_length=200, blank=True, null=True)
    selfie = models.CharField(max_length=500, blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    visited_by = models.IntegerField()
    visited_datetime = models.DateTimeField()
    remark = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_individual_visit'

class TblSchoolVisitHistory(models.Model):
    school_id = models.IntegerField()
    school_name = models.CharField(max_length=255, blank=True, null=True)
    school_contact = models.CharField(max_length=15, blank=True, null=True)
    school_image = models.CharField(max_length=255, blank=True, null=True)
    address_hno = models.CharField(max_length=200, blank=True, null=True)
    address_locality = models.CharField(max_length=200, blank=True, null=True)
    village_id = models.IntegerField(blank=True, null=True)
    village_name = models.CharField(max_length=200, blank=True, null=True)
    tehsil_id = models.IntegerField(blank=True, null=True)
    tehsil_name = models.CharField(max_length=200, blank=True, null=True)
    district_id = models.IntegerField(blank=True, null=True)
    district_name = models.CharField(max_length=200, blank=True, null=True)
    state_id = models.IntegerField(blank=True, null=True)
    state_name = models.CharField(max_length=200, blank=True, null=True)
    pincode = models.IntegerField(blank=True, null=True)
    high_school_students = models.IntegerField(blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    visited_by = models.IntegerField(blank=True, null=True)
    edited_by = models.IntegerField()
    edited_datetime = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_school_visit_history'


class TblSchoolContactHistory(models.Model):
    school_id = models.IntegerField()
    school_contact_id = models.IntegerField()
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    contact_type = models.CharField(max_length=100, blank=True, null=True)
    is_referred = models.IntegerField(default=0)
    referred_by = models.CharField(max_length=255, blank=True, null=True)
    edited_by = models.IntegerField()
    edited_datetime = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_school_contact_history'

class TblIndividualVisitHistory(models.Model):
    individual_student_id = models.IntegerField()
    student_name = models.CharField(max_length=200, blank=True, null=True)
    student_contact = models.CharField(max_length=200, blank=True, null=True)
    student_image = models.CharField(max_length=200, blank=True, null=True)
    guardian_name = models.CharField(max_length=200, blank=True, null=True)
    referred_by_teacher = models.CharField(max_length=200, blank=True, null=True)
    referred_by_student = models.CharField(max_length=200, blank=True, null=True)
    branch_id = models.IntegerField(blank=True, null=True)
    branch_name = models.CharField(max_length=200, blank=True, null=True)
    year =models.CharField(max_length=100, blank=True, null=True)
    highschool_in_year = models.IntegerField(blank=True, null=True)
    address_hno = models.CharField(max_length=200, blank=True, null=True)
    address_locality = models.CharField(max_length=200, blank=True, null=True)
    village_id = models.IntegerField(blank=True, null=True)
    address_village = models.CharField(max_length=200, blank=True, null=True)
    tehsil_id = models.IntegerField(blank=True, null=True)
    address_tehsil = models.CharField(max_length=200, blank=True, null=True)
    district_id = models.IntegerField(blank=True, null=True)
    address_district = models.CharField(max_length=200, blank=True, null=True)
    state_id = models.IntegerField(blank=True, null=True)
    address_state = models.CharField(max_length=200, blank=True, null=True)
    pincode = models.IntegerField(blank=True, null=True)
    school_name = models.CharField(max_length=200, blank=True, null=True)
    school_address = models.CharField(max_length=200, blank=True, null=True)
    coaching_name = models.CharField(max_length=200, blank=True, null=True)
    coaching_teacher = models.CharField(max_length=200, blank=True, null=True)
    coaching_address = models.CharField(max_length=200, blank=True, null=True)
    remark = models.CharField(max_length=500, blank=True, null=True)
    visited_by = models.IntegerField()
    edited_by = models.IntegerField()
    edited_datetime = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_individual_visit_history'

# class TblEntranceRegistration(models.Model):
#     student_name = models.CharField(max_length=255)
#     contact = models.CharField(max_length=15, unique=True)
#     email_address = models.CharField(max_length=255, blank=True, null=True)
#     photo = models.CharField(max_length=500, blank=True, null=True)
#     address_hno = models.CharField(max_length=255, blank=True, null=True)
#     address_locality = models.CharField(max_length=255, blank=True, null=True)
#     village_id = models.IntegerField(blank=True, null=True)
#     address_village = models.CharField(max_length=255, blank=True, null=True)
#     tehsil_id = models.IntegerField(blank=True, null=True)
#     address_tehsil = models.CharField(max_length=255, blank=True, null=True)
#     district_id = models.IntegerField(blank=True, null=True)
#     address_district = models.CharField(max_length=255, blank=True, null=True)
#     state_id = models.IntegerField(blank=True, null=True)
#     address_state = models.CharField(max_length=255, blank=True, null=True)
#     course_id = models.IntegerField(blank=True, null=True)
#     course_name = models.CharField(max_length=255, blank=True, null=True)
#     entrance_status = models.IntegerField(default=0) # 0 --> Not appeared in entrance || 1 --> Appeared in entrance
#     is_student = models.IntegerField(blank=True, null=True, default=0) # 0 --> Referred by Student || 1 --> Referred by Other
#     referenced_by_name = models.CharField(max_length=255, blank=True, null=True)
#     referenced_by_branch_id = models.IntegerField(blank=True, null=True)
#     referenced_by_branch_name = models.CharField(max_length=255, blank=True, null=True)
#     referenced_by_year = models.CharField(max_length=255, blank=True, null=True)
#     registered_by = models.IntegerField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         managed = False
#         db_table = 'tbl_entrance_registration'


class TblEntranceRegistration(models.Model):
    registration_id = models.CharField(max_length=255, blank=True, null=True)
    student_name = models.CharField(max_length=255)
    contact = models.CharField(unique=True, max_length=15)
    email_address = models.CharField(max_length=255, blank=True, null=True)
    class_passed = models.IntegerField(blank=True, null=True)
    photo = models.CharField(max_length=500, blank=True, null=True)
    address_hno = models.CharField(max_length=255, blank=True, null=True)
    address_locality = models.CharField(max_length=255, blank=True, null=True)
    village_id = models.IntegerField(blank=True, null=True)
    address_village = models.CharField(max_length=255, blank=True, null=True)
    tehsil_id = models.IntegerField(blank=True, null=True)
    address_tehsil = models.CharField(max_length=255, blank=True, null=True)
    district_id = models.IntegerField(blank=True, null=True)
    address_district = models.CharField(max_length=255, blank=True, null=True)
    state_id = models.IntegerField(blank=True, null=True)
    address_state = models.CharField(max_length=255, blank=True, null=True)
    course_id = models.IntegerField(blank=True, null=True)
    course_name = models.CharField(max_length=255, blank=True, null=True)
    entrance_status = models.IntegerField(default=0)
    is_student = models.IntegerField(blank=True, null=True, default=0)
    referenced_by_name = models.CharField(max_length=255, blank=True, null=True)
    referenced_by_branch_id = models.IntegerField(blank=True, null=True)
    referenced_by_branch_name = models.CharField(max_length=255, blank=True, null=True)
    referenced_by_year = models.CharField(max_length=255, blank=True, null=True)
    registered_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_entrance_registration'


class TblEntranceOtp(models.Model):
    student_contact = models.CharField(max_length=15)
    otp = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_entrance_otp'


class TblSubjects(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'tbl_subjects'


class TblQuizQuestionnaire(models.Model):
    subject_id = models.IntegerField()
    question = models.TextField()
    option_1 = models.TextField()
    option_2 = models.TextField()
    option_3 = models.TextField()
    option_4 = models.TextField()
    answer_key = models.CharField(max_length=1)
    language = models.IntegerField()
    for_class = models.IntegerField()
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'tbl_quiz_questionnaire'


class TblEntranceQuiz(models.Model):
    candidate_id = models.IntegerField()
    quiz_start_datetime = models.DateTimeField(blank=True, null=True)
    quiz_end_datetime = models.DateTimeField(blank=True, null=True)
    question_answers = models.JSONField(blank=True, null=True)
    result = models.FloatField(blank=True, null=True)
    time_left = models.TimeField(blank=True, null=True)
    last_position = models.IntegerField(default=1)
    is_notified = models.IntegerField(default=0, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_entrance_quiz'

class TblClDocumentTypes(models.Model):
    document_name = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_document_types'

class TblClDocuments(models.Model):
    student_id = models.IntegerField()
    document_name = models.CharField(max_length=100, blank=True, null=True)
    ducument_number = models.CharField(max_length=50, blank=True, null=True)
    document_path = models.CharField(max_length=255, blank=True, null=True)
    is_uploaded = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_documents' 

class SpTowns(models.Model):
    state_id = models.IntegerField()
    state_name = models.CharField(max_length=100)
    town = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_towns'

class SpAddresses(models.Model):
    user = models.OneToOneField('SpUsers', on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    address_line_1 = models.CharField(max_length=250)
    address_line_2 = models.CharField(max_length=250, blank=True, null=True)
    country = models.ForeignKey('SpCountries', on_delete=models.CASCADE)
    country_name = models.CharField(max_length=100)
    state = models.ForeignKey('SpStates', on_delete=models.CASCADE)
    state_name = models.CharField(max_length=100)
    city = models.ForeignKey('SpCities', on_delete=models.CASCADE)
    city_name = models.CharField(max_length=100)
    pincode = models.CharField(max_length=8 )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_addresses'

class SpContactNumbers(models.Model):
    user = models.ForeignKey('SpUsers', on_delete=models.CASCADE)
    country_code = models.CharField(max_length=10)
    contact_type = models.CharField(max_length=50)
    contact_type_name = models.CharField(max_length=25, blank=True, null=True)
    contact_number = models.CharField(max_length=15)
    is_primary = models.IntegerField(default=0)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_contact_numbers'

class SpBasicDetails(models.Model):
    user = models.ForeignKey('SpUsers', on_delete=models.CASCADE)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=25)
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    aadhaar_nubmer = models.CharField(max_length=15, blank=True, null=True)
    pan_number = models.CharField(max_length=20, blank=True, null=True)
    cin = models.CharField(max_length=20, blank=True, null=True)
    gstin = models.CharField(max_length=20, blank=True, null=True)
    fssai = models.CharField(max_length=20, blank=True, null=True)
    working_shift = models.ForeignKey('TblClWorkingShifts', on_delete=models.CASCADE, blank=True, null=True)
    # working_shift = models.ForeignKey('TblClWorkingShifts', on_delete=models.CASCADE, blank=True, null=True)
    date_of_relieving = models.DateField(blank=True, null=True)
    working_shift_name = models.CharField(max_length=50, blank=True, null=True)
    order_timing = models.CharField(max_length=50, blank=True, null=True)
    date_of_joining = models.DateField(blank=True, null=True)
    personal_email = models.CharField(max_length=50, blank=True, null=True)
    outlet_owned = models.CharField(max_length=50, blank=True, null=True)
    outstanding_amount = models.FloatField(blank=True, null=True)
    security_amount = models.FloatField(blank=True, null=True)
    opening_crates = models.IntegerField(blank=True, null=True)
    production_unit_id = models.CharField(max_length=11,null=True)
    distributor_type_id = models.CharField(max_length=11,null=True)
    tcs_applicable = models.IntegerField(blank=True,default=0, null=True)
    tcs_value = models.FloatField(blank=True, null=True)
    per_crate_incentive = models.IntegerField(blank=True, null=True)
    leave_count = models.FloatField(blank=True, null=True)
    week_of_day = models.CharField(max_length=255, blank=True, null=True)
    bank_name = models.CharField(max_length=200, blank=True, null=True)
    account_number = models.CharField(max_length=61, blank=True, null=True)
    ifsc_code = models.CharField(max_length=14, blank=True, null=True)
    account_holder_name = models.CharField(max_length=200, blank=True, null=True)
    branch_address = models.CharField(max_length=250, blank=True, null=True)
    geofencing = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(default=1)
    attendance_type = models.IntegerField(blank=True, null=True)
    contract_type = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_basic_details'


# class SpBasicDetails(models.Model):
#     user_id = models.IntegerField()
#     father_name = models.CharField(max_length=100, blank=True, null=True)
#     mother_name = models.CharField(max_length=100, blank=True, null=True)
#     date_of_birth = models.DateField(blank=True, null=True)
#     gender = models.CharField(max_length=25, blank=True, null=True)
#     blood_group = models.CharField(max_length=10, db_collation='utf8_general_ci', blank=True, null=True)
#     aadhaar_nubmer = models.CharField(max_length=15, blank=True, null=True)
#     pan_number = models.CharField(max_length=20, blank=True, null=True)
#     cin = models.CharField(max_length=20, blank=True, null=True)
#     gstin = models.CharField(max_length=20, blank=True, null=True)
#     fssai = models.CharField(max_length=20, blank=True, null=True)
#     working_shift_id = models.IntegerField(blank=True, null=True)
#     working_shift_name = models.CharField(max_length=50, blank=True, null=True)
#     order_timing = models.CharField(max_length=50, blank=True, null=True)
#     date_of_joining = models.DateField(blank=True, null=True)
#     personal_email = models.CharField(max_length=50, blank=True, null=True)
#     outlet_owned = models.CharField(max_length=50, blank=True, null=True)
#     outstanding_amount = models.FloatField(blank=True, null=True)
#     security_amount = models.FloatField(blank=True, null=True)
#     opening_crates = models.IntegerField(blank=True, null=True)
#     production_unit_id = models.CharField(max_length=11, blank=True, null=True)
#     distributor_type_id = models.CharField(max_length=11, blank=True, null=True)
#     tcs_applicable = models.IntegerField(blank=True, null=True)
#     tcs_value = models.FloatField(blank=True, null=True)
#     per_crate_incentive = models.IntegerField(blank=True, null=True)
#     leave_count = models.IntegerField(blank=True, null=True)
#     week_of_day = models.CharField(max_length=22, blank=True, null=True)
#     bank_name = models.CharField(max_length=200, blank=True, null=True)
#     account_number = models.CharField(max_length=16, blank=True, null=True)
#     ifsc_code = models.CharField(max_length=14, blank=True, null=True)
#     account_holder_name = models.CharField(max_length=200, blank=True, null=True)
#     branch_address = models.CharField(max_length=250, blank=True, null=True)
#     opening_time = models.CharField(max_length=22, blank=True, null=True)
#     closing_time = models.CharField(max_length=22, blank=True, null=True)
#     contract_type = models.IntegerField(blank=True, null=True)
#     board_type = models.CharField(max_length=22, blank=True, null=True)
#     brand_name = models.CharField(max_length=50, blank=True, null=True)
#     location_type = models.CharField(max_length=50, blank=True, null=True)
#     status = models.IntegerField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         managed = False
#         db_table = 'sp_basic_details'


class SpWorkingShifts(models.Model):
    working_shift = models.CharField(max_length=255)
    order_timing = models.TimeField(null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_working_shifts'

class TblClWorkingShifts(models.Model):
    working_shift = models.CharField(max_length=255)
    start_timing = models.TimeField(blank=True, null=True)
    end_timing = models.TimeField(blank=True, null=True)

    first_half_start_timing = models.TimeField(blank=True, null=True)
    first_half_end_timing = models.TimeField(blank=True, null=True)

    second_half_start_timing = models.TimeField(blank=True, null=True)
    second_half_end_timing = models.TimeField(blank=True, null=True)

    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_working_shifts'


        
class TblClRoom(models.Model):
    room = models.CharField(max_length=50)
    college_id = models.IntegerField()
    college_name = models.CharField(max_length=60)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    path = models.CharField(max_length=2000)
    class Meta:
        managed = False
        db_table = 'tbl_cl_room'
        
class TblClAlmirah(models.Model):
    college_id = models.IntegerField()
    college_name = models.CharField(max_length=100)
    room_id = models.IntegerField()
    room_name = models.CharField(max_length=20)
    almirah = models.CharField(max_length=20)
    status = models.IntegerField()
    path = models.CharField(max_length=2000)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_almirah'

class TblClFileFolder(models.Model):
    student_id = models.IntegerField()
    college_id = models.IntegerField()
    room_id = models.IntegerField()
    almira_id = models.IntegerField()
    rack_id = models.IntegerField()
    file_name = models.CharField(max_length=222)
    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_file_folder'

class TblClFolderFiles(models.Model):
    student_id = models.IntegerField()
    college_id = models.IntegerField()
    room_id = models.IntegerField()
    almira_id = models.IntegerField()
    rack_id = models.IntegerField()
    file_id = models.IntegerField()
    file_name = models.CharField(max_length=222)
    docket_no = models.CharField(max_length=222)
    document_id = models.IntegerField()
    document_name = models.CharField(max_length=222)
    document_no = models.CharField(max_length=100)
    document_group = models.CharField(max_length=222)
    is_expiry = models.IntegerField()
    expiry_date = models.DateField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)
    document_path = models.CharField(max_length=222)
    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_folder_files'

class TblClDocumentGroup(models.Model):
    group_name = models.CharField(max_length=222)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_document_group'
        
class TblClRack(models.Model):
    college_id = models.IntegerField()
    college_name = models.CharField(max_length=100)
    room_id = models.IntegerField()
    room_name = models.CharField(max_length=100)
    almira_id = models.IntegerField()
    almira_name = models.CharField(max_length=50)
    rack = models.CharField(max_length=50)
    status = models.IntegerField()
    path = models.CharField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_rack'
        
class TblClEmployeeAttendance(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    emp_id = models.IntegerField(blank=True, null=True)
    attendence_type = models.CharField(max_length=50, blank=True, null=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(blank=True, null=True)
    latitude = models.CharField(max_length=100)
    longitude = models.CharField(max_length=100)
    attendance_img = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_employee_attendance'

class TblClEmployeeDocuments(models.Model):
    employee_id = models.IntegerField()
    document_name = models.CharField(max_length=100, blank=True, null=True)
    ducument_number = models.CharField(max_length=50, blank=True, null=True)
    document_path = models.CharField(max_length=255, blank=True, null=True)
    is_uploaded = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_employee_documents'

class TblClEmployeeFileFolder(models.Model):
    employee_id = models.IntegerField()
    college_id = models.IntegerField()
    room_id = models.IntegerField()
    almira_id = models.IntegerField()
    rack_id = models.IntegerField()
    file_name = models.CharField(max_length=222)
    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_employee_file_folder'

class TblClEmployeeFolderFiles(models.Model):
    employee_id = models.IntegerField()
    college_id = models.IntegerField()
    room_id = models.IntegerField()
    almira_id = models.IntegerField()
    rack_id = models.IntegerField()
    file_id = models.IntegerField()
    file_name = models.CharField(max_length=222)
    docket_no = models.CharField(max_length=222)
    document_id = models.IntegerField()
    document_name = models.CharField(max_length=222)
    document_no = models.CharField(max_length=100)
    document_group = models.CharField(max_length=222)
    is_expiry = models.IntegerField()
    expiry_date = models.DateField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)
    document_path = models.CharField(max_length=222)
    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_employee_folder_files'


# New Model Added

class TblClUserTracking(models.Model):
    user_id = models.IntegerField()
    latitude = models.CharField(max_length=25, blank=True, null=True)
    longitude = models.CharField(max_length=25, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_user_tracking'     

class SpUserLocationLogs(models.Model):
    user_id = models.IntegerField()
    particular = models.CharField(max_length=20)
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'sp_user_location_logs'

class TblClUserLeaves(models.Model):
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=100)
    leave_type_id = models.IntegerField()
    leave_status = models.IntegerField(default=0)
    leave_type = models.CharField(max_length=50)
    leave_from_date = models.DateTimeField()
    leave_to_date = models.DateTimeField()
    leave_detail = models.TextField(blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    attachment = models.CharField(max_length=255,null=True)
    is_first_half_day = models.IntegerField(default=0,blank=True, null=True)
    is_last_half_day = models.IntegerField(default=0,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_user_leaves'


class SpNotifications(models.Model):
    row_id = models.IntegerField(blank=True, null=True)
    model_name = models.CharField(max_length=100, blank=True, null=True)
    module = models.CharField(max_length=100, blank=True, null=True)
    sub_module = models.CharField(max_length=100, blank=True, null=True)
    heading = models.TextField()
    activity = models.TextField()
    activity_image = models.CharField(max_length=255, blank=True, null=True)
    from_user_id = models.IntegerField()
    from_user_name = models.CharField(max_length=150)
    to_user_id = models.IntegerField()
    to_user_type = models.IntegerField(default=1,null=True)
    to_user_name = models.CharField(max_length=150)
    icon = models.CharField(max_length=100, blank=True, null=True)
    platform = models.CharField(max_length=50)
    platform_icon = models.CharField(max_length=100)
    read_status = models.IntegerField(default=1)
    notification_type = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_notifications'

class SpFocRequests(models.Model):
    user_id = models.CharField(max_length=20)
    user_name = models.CharField(max_length=100)
    foc_delivery_date = models.DateTimeField()
    foc_status = models.IntegerField()
    request_by_id = models.IntegerField()
    request_by_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_foc_requests'


# New Table by Sushil

class SpUserAttendance(models.Model):
    user_id = models.IntegerField()
    attendance_date_time = models.DateTimeField()
    start_time = models.CharField(max_length=50, blank=True, null=True)
    end_time = models.CharField(max_length=50, blank=True, null=True)
    dis_ss_id = models.IntegerField(blank=True, null=True)
    latitude = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)
    attendance_img = models.CharField(max_length=200, blank=True, null=True)
    working_shift_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField()
    attendance_type = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_attendance'
        


class SpUserLeaves(models.Model):
    user_id = models.IntegerField()
    handover_user_id = models.IntegerField(blank=True, null=True)
    user_name = models.CharField(max_length=100)
    leave_type_id = models.IntegerField()
    leave_status = models.IntegerField(default=0)
    leave_type = models.CharField(max_length=50)
    leave_from_date = models.DateTimeField()
    leave_to_date = models.DateTimeField()
    leave_detail = models.TextField(blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    attachment = models.CharField(max_length=255,null=True)
    is_first_half_day = models.IntegerField(default=0,blank=True, null=True)
    is_last_half_day = models.IntegerField(default=0,blank=True, null=True)
    is_document_required_count = models.IntegerField(default=0)
    
    is_document_upload = models.IntegerField(default=0)
    is_document_required = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_leaves'


class ContractType(models.Model):
    contract_type = models.CharField(max_length=250)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'contract_type'
        

class TblClAllocatedShifts(models.Model):
    user_id = models.IntegerField()
    working_shift_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_cl_allocated_shifts'


class SpUserTracking(models.Model):
    user_id = models.IntegerField()
    latitude = models.CharField(max_length=25, blank=True, null=True)
    longitude = models.CharField(max_length=25, blank=True, null=True)
    velocity = models.FloatField(blank=True, null=True)
    accuracy = models.FloatField(blank=True, null=True)
    distance_travelled = models.FloatField(blank=True, null=True)
    travel_charges = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_tracking'


class TblSsCandidates(models.Model):
    candidate_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    email = models.CharField(max_length=100)
    candidate_image = models.CharField(max_length=500, blank=True, null=True)
    current_designation = models.CharField(max_length=70)
    current_organization = models.CharField(max_length=150)
    total_experience = models.FloatField(default=0)
    current_ctc = models.FloatField(default=0)
    current_location = models.TextField()
    education_qualification = models.CharField(max_length=255)
    education_year = models.CharField(max_length=5, blank=True, null=True)  # This field type is a guess.
    education_college = models.CharField(max_length=255, blank=True, null=True)
    key_skills = models.TextField(blank=True, null=True)
    last_activity = models.DateTimeField()
    status = models.IntegerField()
    resume = models.CharField(max_length=255)
    applied_on = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'tbl_ss_candidates'
        
        
        
        
        
        
        
        
        
        
class SpUserLeavePolicyLedger(models.Model):
    user_id = models.IntegerField()
    leave_policy_id = models.IntegerField()
    leave_type_id = models.IntegerField()
    year_leave_count = models.DecimalField(max_digits=10, decimal_places=2)
    month_leave_count = models.DecimalField(max_digits=10, decimal_places=2)
    consecutive_leave = models.DecimalField(max_digits=10, decimal_places=2)
    credit = models.FloatField(blank=True, null=True)
    debit = models.FloatField(blank=True, null=True)
    balance = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_leave_policy_ledger'
        
        
        
class SpUserLeaveDocument(models.Model):
    user_id = models.IntegerField()
    user_leave_id = models.IntegerField()
    leave_type_document_id = models.IntegerField(blank=True, null=True)
    document = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_leave_document'
        
        

class SpRegularization(models.Model):
    regularization_type = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_regularization'

class SpUserRegularization(models.Model):
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=222)
    regularization_type_id = models.IntegerField()
    regularization_type_name = models.CharField(max_length=222)
    from_date = models.DateField(blank=True, null=True)
    from_time = models.CharField(max_length=22, blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    to_time = models.CharField(max_length=22, blank=True, null=True)
    mobile_no = models.CharField(max_length=10, blank=True, null=True)
    place = models.CharField(max_length=222, blank=True, null=True)
    reason_for_leave = models.CharField(max_length=255, blank=True, null=True)
    manager = models.CharField(max_length=255, blank=True, null=True)
    hod = models.CharField(max_length=255, blank=True, null=True)
    regularization_status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_user_regularization'
        

class SpBMC(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    bmc_code = models.CharField(max_length=45, blank=True, null=True)
    employee = models.ForeignKey(  # Corrected field name
        SpUsers, 
        on_delete=models.CASCADE,
        related_name='reporting_employee',
        null=True,
        blank=True
    )
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = False
        db_table = 'sp_bmc' 


class SpMPP(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    mpp_code = models.CharField(max_length=45, blank=True, null=True)
    bmc = models.ForeignKey(
        SpBMC, 
        on_delete=models.CASCADE,
        related_name='mpps'
    )
    employee = models.ForeignKey(  # Corrected field name
        SpUsers, 
        on_delete=models.CASCADE,
        related_name='reporting_employee_mpp',
        null=True,
        blank=True
    )
    mpp_tr_code = models.CharField(max_length=100, blank=True, null=True)
    wef_date =  models.DateField(blank=True, null=True)
    latitude = models.CharField(max_length=100, blank=True, null=True)
    longitude = models.CharField(max_length=100, blank=True, null=True)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = False
        db_table = 'sp_mpp'        
        
class SpTaVisit(models.Model):
    ser_check = models.CharField(max_length=200,blank=True, null=True)
    user = models.ForeignKey(
        SpUsers, 
        on_delete=models.CASCADE,
        related_name='user_visit'
    )
    user_name = models.CharField(max_length=200, blank=True, null=True)
    bmc = models.ForeignKey(
        SpBMC, 
        on_delete=models.CASCADE,
        related_name='bmc_visit'
    )
    visit_date = models.DateField()
    start_time = models.CharField(max_length=20, blank=True, null=True)
    end_time = models.CharField(max_length=20, blank=True, null=True)
    start_reading = models.IntegerField(blank=True, null=True)
    end_reading = models.IntegerField(blank=True, null=True)
    travel_charge = models.FloatField()
    start_reading_img = models.CharField(max_length=200, blank=True, null=True)
    end_reading_img = models.CharField(max_length=200, blank=True, null=True)
    purpose = models.CharField(max_length=200, blank=True, null=True)
    remark = models.CharField(max_length=200, blank=True, null=True)
    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_ta_visit' 
        
class SpVisits(models.Model):
    user = models.ForeignKey(
        SpUsers, 
        on_delete=models.CASCADE,
        related_name='user_visits'
    )
    bmc = models.ForeignKey(
        SpBMC, 
        on_delete=models.CASCADE,
        related_name='bmc_visits'
    )
    mpp = models.ForeignKey(
        SpMPP, 
        on_delete=models.CASCADE,
        related_name='mpp_visits'
    )
    checkin_datetime = models.DateTimeField()
    checkout_datetime = models.DateTimeField(blank=True, null=True)
    visit_status = models.IntegerField(default = 1)
    total_retail_time = models.TimeField(blank=True, null=True)
    visit_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_visits'
        
class SpMppVisitHistory(models.Model):
    visit = models.ForeignKey(
        SpVisits, 
        on_delete=models.CASCADE,
        related_name='visits'
    )
    bmc = models.ForeignKey(
        SpBMC, 
        on_delete=models.CASCADE,
        related_name='bmc_history'
    )
    mpp = models.ForeignKey(
        SpMPP, 
        on_delete=models.CASCADE,
        related_name='mpps_history'
    )
    user = models.ForeignKey(  # Corrected field name
        SpUsers, 
        on_delete=models.CASCADE,
        related_name='reporting_employee_history'
    )
    visit_date_time = models.DateTimeField()
    visit_date = models.DateField()
    shift = models.IntegerField(db_comment='1=morning,2= Evening')
    arrival_time = models.TimeField()
    departure_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sp_mpp_visit_history'
        
class SpMppVisitHistoryDetails(models.Model):
    sp_mpp_visit_history = models.ForeignKey(
        SpMppVisitHistory, 
        on_delete=models.CASCADE,
        related_name='history_details'
    )
    q1 = models.CharField(max_length=5, db_comment=' Is MPP Premises Clean and Hygienic from Inside and Outside?')
    q2 = models.CharField(max_length=5, db_comment='Proper Notice Board and Display')
    q3 = models.CharField(max_length=5, db_comment=' Is MPP Premises having proper lightning(inside and outside)?')
    q4 = models.CharField(max_length=5, db_comment=' Is MPP having proper furniture and slab?')
    q5 = models.CharField(max_length=5, db_comment='Availability of Procurement Sheet, Paper Roll, Cartage,Cleaning Solution etc.')
    q6 = models.CharField(max_length=5, db_comment='Is DMPCU Online (If no reason and complaint status of the same.)')
    q7 = models.CharField(max_length=5, db_comment='Water Level of Battery')
    q8 = models.CharField(max_length=5, db_comment='Is milk can neat and clean having no milk debris')
    q9 = models.CharField(max_length=5, db_comment='Member carrying milk in plastic/iron container(if yes member code to be marked)')
    q10 = models.CharField(max_length=5, db_comment='Are farmers getting slip/sms')
    q11 = models.CharField(max_length=5, db_comment='Is organoleptic test performed by sahayak?')
    q12 = models.CharField(max_length=5, db_comment='Is Procurement sheet duly filled with carbon copy?')
    q13 = models.CharField(max_length=5, db_comment='No. of Registered Members')
    q14 = models.FloatField(db_comment='No. of Pourers and Pourer%')
    q15 = models.CharField(max_length=10, db_comment='Composite Report( C)')
    q16 = models.CharField(max_length=10, db_comment='Dispatch Report(D)')
    q17 = models.CharField(max_length=10, db_comment='Diff(D-C)')
    q18 = models.CharField(max_length=10, db_comment='Cattle feed Demand(No. of Bag)')
    q19 = models.CharField(max_length=10, db_comment='ASMM Demand(KG)')
    q20 = models.CharField(max_length=10, db_comment='Ghee Demand(Ltr)')
    q21 = models.CharField(max_length=10, db_comment='No. of Membership Form Filled')
    q22 = models.CharField(max_length=10, db_comment='No. of Non-Pourer Members contacted')
    q23 = models.CharField(max_length=10, db_comment='No. of Non-Members Contacted')
    q24 = models.CharField(max_length=250, blank=True, null=True, db_comment='Farmers complain and suggestion if any')
    q25 = models.CharField(max_length=100, blank=True, null=True, db_comment='mpp picture')
    q26 = models.CharField(max_length=100, blank=True, null=True, db_comment='mpp digital signature')

    class Meta:
        managed = False
        db_table = 'sp_mpp_visit_history_details'      

class SpVisitPurpose(models.Model):
    purpose_name = models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = 'sp_visit_purpose'