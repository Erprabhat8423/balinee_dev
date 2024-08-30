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
    pincode = models.CharField(max_length=8)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_addresses'


class SpAttendanceConfigs(models.Model):
    user = models.ForeignKey('SpUsers', on_delete=models.CASCADE)
    attendance_image_1 = models.CharField(max_length=255)
    attendance_image_2 = models.CharField(max_length=255)
    attendance_image_3 = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_attendance_configs'


class SpBasicDetails(models.Model):
    user = models.ForeignKey('SpUsers', on_delete=models.CASCADE)
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=25)
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    aadhaar_nubmer = models.CharField(max_length=15, blank=True, null=True)
    pan_number = models.CharField(max_length=20, blank=True, null=True)
    cin = models.CharField(max_length=20, blank=True, null=True)
    gstin = models.CharField(max_length=20, blank=True, null=True)
    working_shift = models.ForeignKey('SpWorkingShifts', on_delete=models.CASCADE, blank=True, null=True)
    working_shift_name = models.CharField(max_length=50, blank=True, null=True)
    date_of_joining = models.DateField(blank=True, null=True)
    personal_email = models.CharField(max_length=50, blank=True, null=True)
    outlet_owned = models.CharField(max_length=50, blank=True, null=True)
    outstanding_amount = models.FloatField(blank=True, null=True)
    opening_crates = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_basic_details'


class SpCities(models.Model):
    state = models.ForeignKey('SpStates', on_delete=models.CASCADE)
    state_name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_cities'

class SpColorCodes(models.Model):
    color = models.CharField(max_length=50)
    code = models.CharField(max_length=15)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_color_codes'

class SpContactNumbers(models.Model):
    user = models.ForeignKey('SpUsers', on_delete=models.CASCADE)
    country_code = models.CharField(max_length=10)
    contact_type = models.CharField(max_length=50)
    contact_type_name = models.CharField(max_length=25, blank=True, null=True)
    contact_number = models.CharField(max_length=15)
    is_primary = models.IntegerField(default=0)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_contact_numbers'


class SpContactPersons(models.Model):
    user = models.ForeignKey('SpUsers', on_delete=models.CASCADE)
    contact_person_name = models.CharField(max_length=100)
    designation = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_contact_persons'


class SpContactTypes(models.Model):
    contact_type = models.CharField(max_length=100)
    status = models.IntegerField()
    create_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_contact_types'


class SpCountries(models.Model):
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_countries'

class SpContainers(models.Model):
    container = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_containers'


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
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_departments'


class SpDistributorAreaAllocations(models.Model):
    user = models.ForeignKey('SpUsers', on_delete=models.CASCADE)
    zone = models.ForeignKey('SpZones', on_delete=models.CASCADE)
    zone_name = models.CharField(max_length=100)
    town = models.ForeignKey('SpTowns', on_delete=models.CASCADE)
    town_name = models.CharField(max_length=100, null=True)
    route_id = models.IntegerField()
    route_name = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_distributor_area_allocations'


class SpDistributorProducts(models.Model):
    user = models.ForeignKey('SpUsers', on_delete=models.CASCADE)
    sku_code = models.CharField(max_length=50)
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=100)
    product_variant_id = models.CharField(max_length=50)
    product_mrp = models.FloatField()
    product_sale_price = models.FloatField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_distributor_products'


class SpFavorites(models.Model):
    user = models.ForeignKey('SpUsers', on_delete=models.CASCADE)
    favorite = models.CharField(max_length=100, blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_favorites'


class SpModules(models.Model):
    module_name = models.CharField(max_length=100)
    link = models.CharField(max_length=100, blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_modules'


class SpOrganizations(models.Model):
    organization_name = models.CharField(max_length=150)
    landline_country_code = models.CharField(max_length=10)
    landline_state_code = models.CharField(max_length=10)
    landline_number = models.CharField(max_length=15)
    mobile_country_code = models.CharField(max_length=10)
    mobile_number = models.CharField(max_length=15)
    email = models.CharField(max_length=50)
    address = models.TextField(blank=True, null=True)
    pincode = models.CharField(max_length=8, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_organizations'


class SpPermissions(models.Model):
    permission = models.CharField(max_length=100)
    slug = models.CharField(max_length=150)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_permissions'

class SpProductClass(models.Model):
    product_class = models.CharField(max_length=50)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_product_class'

class SpProductUnits(models.Model):
    unit = models.CharField(max_length=100)
    largest_unit = models.CharField(max_length=50)
    conversion_value = models.FloatField()
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_product_units'

class SpProductVariantImages(models.Model):
    product_variant = models.ForeignKey('SpProductVariants', models.DO_NOTHING)
    image_url = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_product_variant_images'


class SpProductVariants(models.Model):
    product = models.ForeignKey('SpProducts', models.DO_NOTHING)
    product_name = models.CharField(max_length=50)
    item_sku_code = models.CharField(max_length=25)
    variant_quantity = models.IntegerField()
    variant_unit_id = models.IntegerField()
    variant_unit_name = models.CharField(max_length=25)
    variant_name = models.CharField(max_length=255)
    variant_size = models.CharField(max_length=255)
    no_of_pouch = models.IntegerField()
    container_size = models.CharField(max_length=100)
    variant_color_code = models.CharField(max_length=15)
    mrp = models.FloatField()
    sp_distributor = models.FloatField()
    sp_superstockist = models.FloatField()
    sp_employee = models.FloatField()
    valid_from = models.DateField()
    valid_to = models.DateField()
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_product_variants'

class SpProductVariantsHistory(models.Model):
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=255)
    product_variant_id = models.IntegerField()
    mrp = models.FloatField()
    sp_distributor = models.FloatField()
    sp_superstockist = models.FloatField()
    sp_employee = models.FloatField()
    valid_from = models.DateField()
    valid_to = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_product_variants_history'

class SpProducts(models.Model):
    product_class = models.ForeignKey(SpProductClass, models.DO_NOTHING)
    product_class_name = models.CharField(max_length=50)
    product_name = models.CharField(max_length=100)
    container = models.ForeignKey(SpContainers, models.DO_NOTHING)
    container_name = models.CharField(max_length=50)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_products'

class SpRolePermissions(models.Model):
    role = models.ForeignKey('SpRoles', on_delete=models.CASCADE)
    module = models.ForeignKey(SpModules, on_delete=models.CASCADE, blank=True, null=True)
    sub_module = models.ForeignKey('SpSubModules', on_delete=models.CASCADE, blank=True, null=True)
    permission = models.ForeignKey(SpPermissions, on_delete=models.CASCADE, blank=True, null=True)
    workflow = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_role_permissions'


class SpRoleWorkflowPermissions(models.Model):
    role_id = models.IntegerField()
    module_id = models.IntegerField(blank=True, null=True)
    sub_module_id = models.IntegerField()
    permission_id = models.IntegerField()
    level_id = models.IntegerField()
    level = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    workflow_level_dept_id = models.IntegerField(null=True)
    workflow_level_role_id = models.IntegerField()
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

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
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_roles'


class SpRoutes(models.Model):
    route = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_routes'


class SpSchemes(models.Model):
    name = models.CharField(max_length=255)
    state_id = models.CharField(max_length=100)
    route_id = models.CharField(max_length=100)
    town_id = models.CharField(max_length=100)
    scheme_start_date = models.DateField()
    scheme_end_date = models.DateField()
    scheme_type = models.IntegerField()
    applied_on_variant_id = models.IntegerField(blank=True, null=True)
    applied_on_variant_name = models.CharField(max_length=255, blank=True, null=True)
    minimum_order_quantity = models.IntegerField()
    free_variant_id = models.IntegerField()
    free_variant_name = models.CharField(max_length=255)
    container_quantity = models.IntegerField()
    pouch_quantity = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_schemes'


class SpStates(models.Model):
    country = models.ForeignKey(SpCountries, on_delete=models.CASCADE)
    country_name = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

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
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_sub_modules'


class SpTowns(models.Model):
    zone_id = models.CharField(max_length=255)
    zone_name = models.CharField(max_length=255)
    town = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_towns'


class SpUserAreaAllocations(models.Model):
    user = models.ForeignKey('SpUsers', on_delete=models.CASCADE)
    zone = models.ForeignKey('SpZones', on_delete=models.CASCADE)
    zone_name = models.CharField(max_length=100, null=True)
    town = models.ForeignKey('SpTowns', on_delete=models.CASCADE)
    town_name = models.CharField(max_length=100,null=True)
    route_id = models.IntegerField(blank=True, null=True)
    route_name = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_user_area_allocations'


class SpUserAttendanceLocations(models.Model):
    user = models.ForeignKey('SpUsers', on_delete=models.CASCADE)
    attendance_config_id = models.IntegerField()
    distributor_ss_id = models.IntegerField()
    distributor_ss_name = models.CharField(max_length=255)
    periphery = models.IntegerField()
    timing = models.CharField(max_length=100)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_user_attendance_locations'


class SpUserDocuments(models.Model):
    user = models.ForeignKey('SpUsers', on_delete=models.CASCADE)
    aadhaar_card = models.CharField(max_length=255, blank=True, null=True)
    pan_card = models.CharField(max_length=255, blank=True, null=True)
    cin = models.CharField(max_length=255, blank=True, null=True)
    gstin = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_user_documents'

class SpUserProductVariants(models.Model):
	user_id = models.IntegerField()
	product_id = models.IntegerField()
	product_name = models.CharField(max_length=50)
	product_variant_id = models.IntegerField()
	item_sku_code = models.CharField(max_length=25)
	variant_quantity = models.IntegerField()
	variant_unit_id = models.IntegerField()
	variant_unit_name = models.CharField(max_length=25)
	variant_name = models.CharField(max_length=255)
	variant_size = models.CharField(max_length=255)
	no_of_pouch = models.IntegerField()
	container_size = models.CharField(max_length=100)
	variant_color_code = models.CharField(max_length=15)
	mrp = models.FloatField()
	sp_distributor = models.FloatField(default=0)
	sp_superstockist = models.FloatField(default=0)
	sp_employee = models.FloatField(default=0)
	valid_from = models.DateField()
	valid_to = models.DateField()
	created_at = models.DateTimeField()
	updated_at = models.DateTimeField()

	class Meta:
		managed = False
		db_table = 'sp_user_product_variants'

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
    workflow = models.TextField(blank=True, null=True)
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_user_role_permissions'


class SpUserRoleWorkflowPermissions(models.Model):
    user = models.ForeignKey('SpUsers', models.DO_NOTHING)
    role_id = models.IntegerField()
    module_id = models.IntegerField(blank=True, null=True)
    sub_module_id = models.IntegerField()
    permission_id = models.IntegerField()
    level_id = models.IntegerField()
    level = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    workflow_level_dept_id = models.IntegerField()
    workflow_level_role_id = models.IntegerField()
    status = models.IntegerField()
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_user_role_workflow_permissions'
        

class SpUserSchemes(models.Model):
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=255)
    scheme_id = models.IntegerField()
    scheme_name = models.CharField(max_length=255)
    state_id = models.IntegerField()
    route_id = models.CharField(max_length=100)
    town_id = models.CharField(max_length=100)
    scheme_start_date = models.DateField()
    scheme_end_date = models.DateField()
    scheme_type = models.IntegerField()
    applied_on_variant_id = models.IntegerField(blank=True, null=True)
    applied_on_variant_name = models.CharField(max_length=255, blank=True, null=True)
    minimum_order_quantity = models.IntegerField()
    free_variant_id = models.IntegerField()
    free_variant_name = models.CharField(max_length=255)
    container_quantity = models.IntegerField()
    pouch_quantity = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_user_schemes'



class SpUsers(AbstractBaseUser):
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'official_email'

    salutation = models.CharField(max_length=10)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50,null=True)
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
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    objects = UserManager()

    class Meta:
        managed = False
        db_table = 'sp_users'


class SpWorkflowLevels(models.Model):
    level = models.CharField(max_length=15)
    priority = models.CharField(max_length=10, blank=True, null=True)
    color = models.CharField(max_length=10)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_workflow_levels'


class SpWorkingShifts(models.Model):
    working_shift = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_working_shifts'


class SpZones(models.Model):
    zone = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_zones'

class SpCountryCodes(models.Model):
    country_code = models.CharField(max_length=10)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_country_codes'

class SpAppVersions(models.Model):
    version = models.CharField(max_length=100)
    status = models.CharField(default=0, max_length=100)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sp_app_versions'

class AuthtokenToken(models.Model):
    key  = models.CharField(max_length=40)
    created = models.DateTimeField()
    user_id  = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'authtoken_token'

class ProductVariantTemplate(models.Model):
    store_name = models.CharField(max_length=222, blank=True, null=True)
    role = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product_variant_template'

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)        
