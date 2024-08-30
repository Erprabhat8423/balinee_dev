from django.urls import path,re_path
from ..views import *

app_name = 'src'
urlpatterns = [

    # autoload files
    
    path('map-leave-ledger/<str:role_id>', userManagement.mapUserLeavess, name='map-leave-ledger'),
    
    path('firebase-messaging-sw.js', profile.firebase_messaging_sw_js),
    path('opencv.js', profile.opencv_js),
    path('haarcascade_frontalface_default.xml', profile.haarcascade_frontalface_default_xml),

    path('dashboard', profile.index, name='dashboard'),
    path('manage-profile', profile.manageProfile, name='manage-profile'),
    path('update-configuration', profile.updateConfiguration, name='update-configuration'),
    path('update-profile', profile.updateProfile, name='update-profile'),
    path('change-password', profile.changePassword, name='change-password'),
    path('graph-ajaxFilter', profile.ajaxFilter, name='graph-ajaxFilter'),
    
    path('id-card-design', profile.idCardDesign, name='id-card-design'),

    path('organizations', organizations.index, name='organizations'),
    path('ajax-organization-list', organizations.ajaxOrganizationList, name='ajax-organization-list'),
    path('ajax-organization-lists', organizations.ajaxOrganizationLists, name='ajax-organization-lists'),
    path('add-organization', organizations.addOrganization, name='add-organization'),
    path('save-organization', organizations.saveOrganization, name='save-organization'),
    path('edit-organization', organizations.editOrganization, name='edit-organization'),
    path('update-organization', organizations.updateOrganization, name='update-organization'),
    path('get-organization-record', organizations.getOrganizationRecord, name='get-organization-record'),
    path('update-organization-status', organizations.updateOrganizationStatus, name='update-organization-status'),
    path('update-student-status', student.updateStudentStatus, name='update-student-status'),
    path('add-department', organizations.addDepartment, name='add-department'),
    path('save-department', organizations.saveDepartment, name='save-department'),
    path('edit-department', organizations.editDepartment, name='edit-department'),
    path('update-department', organizations.updateDepartment, name='update-department'),
    path('update-department-status', organizations.updateDepartmentStatus, name='update-department-status'),
    path('export-organizations-to-xlsx/<str:columns>', organizations.exportToXlsx, name='export-organizations-to-xlsx'),
    path('export-organizations-to-pdf/<str:columns>', organizations.exportToPDF, name="export-organizations-to-pdf"),
    
    
    path('roles', roleManagement.index, name='roles'),
    path('ajax-role-list', roleManagement.ajaxRoleList, name='ajax-role-list'),
    path('ajax-role-lists', roleManagement.ajaxRoleLists, name='ajax-role-lists'),
    path('add-role', roleManagement.addRole, name='add-role'),
    path('add-role-permission', roleManagement.addRolePermission, name='add-role-permission'),
    path('update-role-status', roleManagement.updateRoleStatus, name='update-role-status'),
    path('edit-role', roleManagement.editRole, name='edit-role'),
    path('role-entity-mapping/<str:role_id>/<str:entity_type>', roleManagement.roleEntityMapping, name='role-entity-mapping'),
    path('save-role-mapping', roleManagement.saveRoleMapping, name='save-role-mapping'),
    path('save-role-unmapping', roleManagement.saveRoleUnmapping, name='save-role-unmapping'),
    path('save-role-leave-policy-mapping', roleManagement.saveRoleLeavePolicyMapping, name='save-role-leave-policy-mapping'),
    path('save-role-attendance-group-mapping', roleManagement.saveRoleAttendanceGroupMapping, name='save-role-attendance-group-mapping'),
    path('save-role-pay-band-mapping', roleManagement.saveRolePayBandMapping, name='save-role-pay-band-mapping'),
    path('save-role-holiday-mapping', roleManagement.saveRoleHolidayMapping, name='save-role-holiday-mapping'),
    path('save-role-salary-addition-mapping', roleManagement.saveRoleSalaryAdditionMapping, name='save-role-salary-addition-mapping'),
    path('save-role-salary-deduction-mapping', roleManagement.saveRoleSalaryDeductionMapping, name='save-role-salary-deduction-mapping'),
    
    path('permission-workflows', permissionWorkflow.index, name='permission-workflows'),
    path('update-permission-workflows', permissionWorkflow.updatePermissionWorkflows, name='update-permission-workflows'),
    path('update-permission-and-workflows', permissionWorkflow.updatePermissionAndWorkflows, name='update-permission-and-workflows'),
    path('remove-permission-and-workflows', permissionWorkflow.removePermissionAndWorkflows, name='remove-permission-and-workflows'),
    
    path('add-short-role/<str:parent_role_id>', roleManagement.addShortRole, name='add-short-role'),
    path('add-short-role-details/<str:role_id>', roleManagement.shortRoleDetails, name='add-short-role-details'),
    path('save-role-activity', roleManagement.saveRoleActivity, name='save-role-activity'),
    path('delete-role-activity/<str:role_activity_id>', roleManagement.deleteRoleActivity, name='delete-role-activity'),

    path('view-map-role-attributes-modal/<str:role_id>', roleManagement.viewMapRoleAttributesModal, name='view-map-role-attributes-modal'),
    path('role-type-attribute-controls/<str:id>', roleManagement.getAttributeControls, name='role-type-attribute-controls'),
    path('update-role-attributes', roleManagement.updateRoleAttributes, name='update-role-attributes'),

    path('contact-cards', contactManagement.index, name='contact-cards'),
    path('add-contact-card', contactManagement.addContactCard, name='add-contact-card'),
    path('edit-contact-card', contactManagement.editContactCard, name='edit-contact-card'),
    path('get-role-type-attributes-form/<str:role_id>', contactManagement.getRoleTypeAttributesForm, name='get-role-type-attributes-form'),
    path('get-role-type-attributes/<str:role_id>', contactManagement.getRoleTypeAttributes, name='get-role-type-attributes'),
    path('admission-procedures-details/<str:admission_procedures_id>', contactManagement.admissionProcedureDetails, name='admission-procedures-details'),
    path('search-departments/<str:location_id>', contactManagement.searchDepartments, name='search-departments'),
    path('search-roles', contactManagement.searchRoles, name='search-roles'),
    path('get-role-organization-option/<str:role_id>', contactManagement.getRoleOrganizationOption, name='get-role-organization-option'),

    path('save-contact', contactManagement.saveContact, name='save-contact'),
    path('update-contact', contactManagement.updateContact, name='update-contact'),
    path('get-user-contact-record', contactManagement.getUserContactRecord, name='get-user-contact-record'),
    path('get-user-attribute-detail/<str:user_id>/<str:attribute_name>', contactManagement.getUserAttributeDetail, name='get-user-attribute-detail'),
    path('ajax-contact-list', contactManagement.ajaxContactList, name='ajax-contact-list'), 
    path('ajax-contact-card-list', contactManagement.ajaxContactCardList, name='ajax-contact-card-list'),
    path('get-role-type-attributes-edit-form/<str:user_id>/<str:role_id>', contactManagement.getRoleTypeAttributesEditForm, name='get-role-type-attributes-edit-form'),
    path('create-student-card', contactManagement.createStudentCard, name='create-student-cardt'),


    

    path('users', userManagement.index, name='users'),
    path('send-email', userManagement.sendEmail, name='send-email'),
    path('ajax-operational-users-list', userManagement.ajaxOperationalUsersList, name='ajax-operational-users-list'),
    path('ajax-non-operational-users-list', userManagement.ajaxNonOperationalUsersList, name='ajax-non-operational-users-list'),
    path('ajax-employee-users-list', userManagement.ajaxEmployeeUsersList, name='ajax-employee-users-list'),
    path('add-user-basic-detail', userManagement.addUserBasicDetail, name='add-user-basic-detail'),
    path('edit-user-basic-detail', userManagement.editUserBasicDetail, name='edit-user-basic-detail'),
    path('add-user-offical-detail', userManagement.addUserOfficalDetail, name='add-user-offical-detail'),
    path('edit-user-offical-detail', userManagement.editUserOfficalDetail, name='edit-user-offical-detail'),
    
    path('add-employee-biometric-details', userManagement.addEmployeeBiometricDetails, name='add-employee-biometric-details'),
    path('edit-employee-biometric-details/<int:employee_id>', userManagement.editEmployeeBiometricDetails, name='edit-employee-biometric-details'),
    path('add-employee-photo', userManagement.addEmployeePhoto,name='add-employee-photo'),

    path('add-user-product-detail', userManagement.addUserProductDetail, name='add-user-product-detail'),
    path('update-user-variant-price', userManagement.updateUserVariantPrice, name='update-user-variant-price'),
    path('edit-user-product-detail', userManagement.editUserProductDetail, name='edit-user-product-detail'),
    path('add-user-document-detail', userManagement.addUserDocumentDetail, name='add-user-document-detail'),
    path('user-geo-tagged', userManagement.userGeoTagged, name='user-geo-tagged'),
    path('update-user-status', userManagement.updateUserStatus, name='update-user-status'),
    path('export-operational-user-to-xlsx/<str:columns>', userManagement.exportOperationalUserToXlsx, name='export-operational-user-to-xlsx'),
    path('export-operational-user-to-pdf/<str:columns>', userManagement.exportOperationalUserToPdf, name='export-operational-user-to-pdf'),
    path('export-non-operational-user-to-xlsx/<str:columns>', userManagement.exportNonOperationalUserToXlsx, name='export-non-operational-user-to-xlsx'),
    path('export-non-operational-user-to-pdf/<str:columns>', userManagement.exportNonOperationalUserToPdf, name='export-non-operational-user-to-pdf'),
    # path('export-employee-to-xlsx/<str:columns>', userManagement.exportEmployeeToXlsx, name='export-employee-to-xlsx'),
    path('export-employee-to-xlsx/<str:columns>/<str:search>/<str:jobs>/<str:depts>/<str:roles>', userManagement.exportEmployeeToXlsx, name='export-employee-to-xlsx'),
    path('export-employee-to-pdf/<str:columns>/<str:search>/<str:jobs>/<str:depts>/<str:roles>', userManagement.exportEmployeeToPdf, name='export-employee-to-pdf'),
    path('import-product-variant', userManagement.importProductVariant, name='import-product-variant'),

    path('add-employee-basic-detail', userManagement.addEmployeeBasicDetail, name='add-employee-basic-detail'),
    path('add-employee-official-detail', userManagement.addEmployeeOfficalDetail, name='add-employee-official-detail'),
    path('add-employee-attendance-detail', userManagement.addEmployeeAttendanceDetail, name='add-employee-attendance-detail'),
    path('add-employee-document-detail', userManagement.addEmployeeDocumentDetail, name='add-employee-document-detail'),

    path('edit-employee-basic-detail/<int:employee_id>', userManagement.editEmployeeBasicDetail, name='edit-employee-basic-detail'),
    path('edit-employee-official-detail/<int:employee_id>', userManagement.editEmployeeOfficalDetail, name='edit-employee-official-detail'),
    path('edit-employee-attendance-detail/<int:employee_id>', userManagement.editEmployeeAttendanceDetail, name='edit-employee-attendance-detail'),
    path('get-user-map', userManagement.getUserMap, name='get-user-map'),
    path('edit-employee-document-detail/<int:employee_id>', userManagement.editEmployeeDocumentDetail, name='edit-employee-document-detail'),

    path('user-short-details/<int:user_id>', userManagement.userShortDetail, name='user-short-details'),
    path('user-details/<int:user_id>', userManagement.userDetail, name='user-details'),
    path('employee-short-details/<int:employee_id>', userManagement.employeeShortDetail, name='employee-short-details'),
    path('employee-details/<int:employee_id>', userManagement.employeeDetail, name='employee-details'),

    path('view-user-role-permission/<int:user_id>', userManagement.viewUserRolePermission, name='view-user-role-permission'),
    path('update-user-role-permission', userManagement.updateUserRolePermission, name='update-user-role-permission'),
    path('check-role-permission', userManagement.checkRolePermision, name='check-role-permission'),
    path('save-role-permission-validity', userManagement.saveRolePermisionValidity, name='save-role-permission-validity'),
    
    path('add-employee-documents', userManagement.addEmployeeDocuments, name='add-employee-documents'),
    path('employee-document-list', userManagement.employeeDocumentList, name='employee-document-list'),
    path('add-employee-new-folder', userManagement.addEmployeeNewFolder, name='add-employee-new-folder'),
    path('add-employee-new-file', userManagement.addEmployeeNewFile, name='add-employee-new-file'),
    path('get-employee-master-details', userManagement.getEmployeeMasterDetails, name='get-employee-master-details'),
    path('reset-user-credential/<str:user_id>', userManagement.resetCredential, name='reset-user-credential'),
    path('reset-user-location', userManagement.resetUserLocation, name='reset-user-location'),

    path('get-leave-type-document-options/<str:leave_type_id>', ajax.leaveTypeDocumentOption, name='get-leave-type-document-options'),
    path('get-state-options/<int:country_id>', ajax.stateOption, name='get-state-options'),
    path('get-city-options/<int:state_id>', ajax.cityOption, name='get-city-options'),
    path('get-organization-department-options/<str:organization_id>', ajax.getOrganizationDepartmentOptions, name='get-organization-department-options'),
    path('get-college-course-options/<str:college_id>', ajax.getCollegeCourseOptions, name='get-college-course-options'),
    
    path('get-options-list', ajax.getOptionsList, name='get-options-list'),
    path('edit-role/<int:role_id>', roleManagement.editRole, name='edit-role'),
    path('role-details/<int:role_id>', roleManagement.roleDetails, name='role-details'),
    
    path('get-district-optionss/<int:state_id>', ajax.districtOptions, name='get-district-optionss'),
    path('get-tehsil-options/<int:district_id>', ajax.tehsilOption, name='get-tehsil-options'),
    # path('get-cities-options/<int:tehsil_id>', ajax.citiesOption, name='get-cities-options'),

    path('get-state-towns/<int:state_id>', ajax.getStateTowns, name='get-state-towns'),
    path('get-zone-towns/<int:zone_id>', ajax.getZoneTowns, name='get-zone-towns'),
    path('get-route-towns/<int:route_id>', ajax.getRouteTowns, name='get-route-towns'),


    path('update-favorite', ajax.updateFavorite, name='update-favorite'),
    path('get-add-role-permission/<int:role_id>', roleManagement.getAddRolePermission, name='get-add-role-permission'),
    path('get-org-department-options/<int:organization_id>', roleManagement.orgDepartmentOption, name='get-org-department-options'),
    path('get-org-role-options/<int:organization_id>', roleManagement.orgRoleOption, name='get-org-role-options'),
    path('get-department-role-options/<int:department_id>', roleManagement.departmentRoleOption, name='get-department-role-options'),
    path('get-grouped-town-options', userManagement.getGroupedTownOptions, name='get-grouped-town-options'),
    path('get-reporting-user-options/<int:role_id>', userManagement.getReportingUserOptions, name='get-reporting-user-options'),
    
   
    path('get-state-route-options/<int:state_id>', ajax.stateRouteOptions, name='get-state-route-options'),
    path('get-route-town-options', ajax.routeTownOptions, name='get-route-town-options'),
    path('get-product-variant-details/<int:product_variant_id>', ajax.productVariantDetails, name='get-product-variant-details'),
    path('get-order-time', ajax.getOrderTime, name='get-order-time'),
    
    path('master-management', master.index, name='master-management'),
    # path('get-room-list', master.ajaxRoomList, name='get-room-list'),
    # path('add-room-list', master.addRoomList,name='add-room-list'),
    # path('edit-room-list/<str:room_id>',master.editRoomList, name='edit-room-list'),
    path('get-room-list', master.ajaxRoomList, name='get-room-list'),
    path('add-room-list', master.addRoomList,name='add-room-list'),
    path('edit-room-list/<str:room_id>',master.editRoomList, name='edit-room-list'),
    path('get-college-room-no', master.getCollegeByRoom, name='get-college-room-no'),
    path('get-room-almira', master.getRoomByAlmirah, name='get-room-almira'),
    path('get-almirah-list', master.ajaxAlmirahList, name='get-almirah-list'),
    path('get-rack-list', master.ajaxRackList, name='get-rack-list'),
    path('add-almirah', master.addAlmirah, name='add-almirah'),
    path('add-rack', master.addRack, name='add-rack'),
    path('edit-almirah/<str:almirah_id>', master.editAlmirahList,name='edit-almirah'),
    path('edit-rack/<str:rack_id>', master.editRackList,name='edit-rack'),
    path('get-college-room-no', master.getCollegeByRoom, name='get-college-room-no'),

    
    

    path('room-status/<str:room_status>', master.updateRoomStatus, name='room-status'),
    path('almira-status/<str:almira_status>', master.updateAlmiraStatus, name='almira-status'),
    path('rack-status/<str:rack_status>', master.updateRackStatus, name='rack-status'),
    # path('master-Search-bar', master.masterSearch, name='master-Search-bar'),
    # path('search-leave-type-list/<str:leave_type_filter>', master.searchLeaveType, name='search-leave-type-list'),
    # path('search-holiday-type-list/<str:holiday_type_filter>', master.searchHolidayType, name='search-holiday-type-list'),
    # path('search-pay-band-list/<str:pay_band_filter>', master.searchPayBand, name='search-pay-band-list'),
    # path('search-attendance-group-list/<str:search_attendance_group_filter>', master.searchAttendanceGroup, name='search-attendance-group-list'),    
    # path('search-salary-addition-type-list/<str:search_salary_addition_filter>', master.searchSalaryAdditionTypeList, name='search-salary-addition-type-list'),
    # path('search-salary-deduction-type-list/<str:search_salary_deduction_filter>', master.searchSalaryDeductionTypeList, name='search-salary-deduction-type-list'),
    path('get-leave-type-documents/<str:leave_type_id>', leaveHolidayMaster.getLeaveTypeDocuments, name='get-leave-type-documents'),
    path('get-leave-type-list', leaveHolidayMaster.ajaxLeaveTypeList, name='get-leave-type-list'),
    path('get-holiday-type-list', leaveHolidayMaster.ajaxHolidayTypeList, name='get-holiday-type-list'),
    
    path('get-group-type-list', master.ajaxGroupTypeList,name='get-group-type-list'),
    path('add-group-type', master.addAGroupType, name='add-group-type'),
    path('edit-group-type/<str:group_type_id>',master.editGroupTypeList, name='edit-group-type'),
    path('update-group-type-status/<str:group_type_id>',master.updateGroupTypeStatus, name='update-group-type-status'),
    
    # path('add-course', organizations.addCourse, name='add-course'),
    # path('view-course', organizations.viewCourse, name='view-course'),
    # path('update-course-status/<str:course_id>',organizations.updateCourseStatus, name='update-course-status'),
    # path('edit-courses/<str:course_id>',organizations.editCourses, name='edit-courses'),
    # path('edit-course/<str:course_id>',organizations.editCourse, name='edit-course'),
    # path('update-branch-status', organizations.updateCourseStatus,name='update-branch-status'),
    
    path('get-document-type-list', master.ajaxDocumentTypeList, name='get-document-type-list'),
    path('add-document-type', master.addDocumentTypeList, name='add-document-type'),
    path('edit-document-type/<str:document_type_id>', master.editDocumentTypeList,name='edit-document-type'),

    # Job Type Master
    path('get-job-type-list', master.ajaxJobTypeList,name='get-job-type-list'),
    path('add-job-type',master.addJobType, name='add-job-type'),
    path('edit-job-type/<str:job_type_id>',master.editJobTypeList, name='edit-job-type'),
    path('update-job-type-status/<str:job_type_id>',master.updateJobTypeStatus, name='update-job-type-status'),
# -------------------------------------------------------------------------------------------------
    # path('search-income-category-type-listt/<str:income_category_id>',master.searchIncomeCategoryList, name='search-income-category-type-list'),
    path('get-income-category-list', master.ajaxIncomeCategoryList,name='get-income-category-list'),
    path('add-income-category-type', master.addIncomeCategoryList,name='add-income-category-type'),
    path('edit-income-category-type/<str:income_category_id>',master.editIncomeCategory, name='edit-income-category-type'),

    # path('search-course-types-list/<str:college_session_id>',master.searchCollegeSessionList, name='search-course-types-list'),
    path('add-college-session', master.addCollegeSession, name='add-college-session'),
    path('edit-college-session/<str:session_id>', master.editCollegeSession, name='edit-college-session'),
    path('get-college-session-types', master.ajaxCollegeSessionList, name='get-college-session-types'),

    # path('search-prviliage-category-list/<str:prviliage_category_id>',master.searchPrviliageCategoryList, name='search-prviliage-category-list'),
    path('get-prviliage-category', master.ajaxPrviliageCategoryList, name='get-prviliage-category'),
    path('add-prviliage-category', master.addPrviliageCategory, name='add-prviliage-category'),
    path('edit-prviliage-category/<str:prviliage_category_id>', master.editPrviliageCategory, name='edit-prviliage-category'),

    # path('search-caste-category-list/<str:caste_category_id>',master.searchCasteCategoryList, name='search-caste-category-list'),
    path('get-caste-category-list', master.ajaxCasteCategoryList, name='get-caste-category-list'),
    path('add-caste-category-type', master.addCasteCategoryList, name='add-caste-category-type'),
    path('edit-caste-category-type/<str:caste_category_id>', master.editCasteCategory, name='edit-caste-category-type'),

    # path('search-districts-list/<str:district_id>',master.searchDistrict, name='search-districts-list'),
    path('get-district-master-list', master.ajaxDistrictList, name='get-district-master-list'),
    path('add-district', master.addDistrict, name='add-district'),
    path('edit-district/<str:district_id>', master.editDistrict, name='edit-district'),

    # path('search-tehsil-list/<str:tehsil_id>',master.searchTehsil, name='search-tehsil-list'),
    path('get-tehsil-master-list', master.ajaxTehsilList, name='get-tehsil-master-list'),
    path('add-tehsil', master.addTehsil, name='add-tehsil'),
    path('edit-tehsil/<str:tehsil_id>', master.editTehsil, name='edit-tehsil'),

    # path('search-section-types-list/<str:section_id>',master.searchSection, name='search-section-types-list'),
    path('get-section-list', master.ajaxSectionList,name='get-section-list'),
    path('add-section', master.addSection, name='add-section'),
    path('edit-section/<str:section_id>', master.editSection, name='edit-section'),
# -----------------------------------------------------------------------------------------------------------------------
    path('add-leave-type', leaveHolidayMaster.addLeaveType, name='add-leave-type'),
    path('edit-leave-type/<str:leave_type_id>', leaveHolidayMaster.editLeaveType, name='edit-leave-type'),
    path('update-leave-type-status/<str:leave_type_id>', leaveHolidayMaster.updateLeaveTypeStatus, name='update-leave-type-status'),

    path('add-holiday-type', leaveHolidayMaster.addHolidayType, name='add-holiday-type'),
    path('edit-holiday-type/<str:holiday_type_id>', leaveHolidayMaster.editHolidayType, name='edit-holiday-type'),
    path('update-holiday-type-status/<str:holiday_type_id>', leaveHolidayMaster.updateHolidayTypeStatus, name='update-holiday-type-status'),
    
    path('get-pay-band-list', master.ajaxPayBandList, name='get-pay-band-list'),
    path('add-pay-band', master.addPayBand, name='add-pay-band'),
    path('edit-pay-band/<str:pay_band_id>', master.editPayBand, name='edit-pay-band'),
    path('update-pay-band-status/<str:pay_band_id>', master.updatePayBandStatus, name='update-pay-band-status'),

    path('get-salary-addition-type-list', master.ajaxSalaryAdditionTypeList, name='get-salary-addition-type-list'),
    path('add-salary-addition-type', master.addSalaryAdditionType, name='add-salary-addition-type'),
    path('edit-salary-addition-type/<str:salary_addition_type_id>', master.editSalaryAdditionType, name='edit-salary-addition-type'),
    path('update-salary-addition-type-status/<str:salary_addition_type_id>', master.updateSalaryAdditionTypeStatus, name='update-salary-addition-type-status'),

    path('get-salary-deduction-type-list', master.ajaxSalaryDeductionTypeList, name='get-salary-deduction-type-list'),
    path('add-salary-deduction-type', master.addSalaryDeductionType, name='add-salary-deduction-type'),
    path('edit-salary-deduction-type/<str:salary_deduction_type_id>', master.editSalaryDeductionType, name='edit-salary-deduction-type'),
    path('update-salary-deduction-type-status/<str:salary_deduction_type_id>', master.updateSalaryDeductionTypeStatus, name='update-salary-deduction-type-status'),


    path('get-attendance-group-list', master.ajaxAttendanceGroupList, name='get-attendance-group-list'),
    path('add-attendance-group', master.addAttendanceGroup, name='add-attendance-group'),
    path('edit-attendance-group/<str:attendance_group_id>', master.editAttendanceGroup, name='edit-attendance-group'),
    path('update-attendance-group-status/<str:attendance_group_id>', master.updateAttendanceGroupStatus, name='update-attendance-group-status'),
    
    path('leave-policies', leaves.index, name='leave-policies'),
    path('leave-status-update', leaves.updatePolicyStatus, name='leave-status-update'),
    path('leave-policies-filter/<str:filter_value>', leaves.ajaxLeaveFilter, name='leave-policies-filter'),
    path('leave-policies-filter-status/<str:filter_value>/<str:filter_status>', leaves.ajaxLeaveFilterStatus, name='leave-policies-filter-status'),
    path('leave-policy-short-details/<str:leave_policy_id>', leaves.leavePolicyShortDetails, name='leave-policy-short-details'),
    path('add-leave-policy', leaves.addLeavePolicy, name='add-leave-policy'),
    path('edit-leave-policy/<str:leave_policy_id>', leaves.editLeavePolicy, name='edit-leave-policy'),
    path('update-leave-policy-status', leaves.updateLeavePolicyStatus, name='update-leave-policy-status'),
    path('ajax-leave-policy-rows', leaves.ajaxLeavePolicyRows, name='ajax-leave-policy-rows'),
    
    #Holidays
    path('holidays', holiday.index, name='holidays'),
    path('add-holiday', holiday.addHoliday, name='add-holiday'),
    path('filter-role-by-organization', holiday.roleByOrganization, name='filter-role-by-organization'),
    path('edit-holiday/<str:holiday_id>', holiday.editHoliday, name='edit-holiday'),
    path('holidays/holiday-calendar', holiday.holidayCalendar, name='holidays/holiday-calendar'),
    path('holidays/filter-holiday/<str:filter_status>', holiday.filterHoliday, name='holidays/filter-holiday'),
    path('update-holiday-status', holiday.updateHolidayStatus, name='update-holiday-status'),
    path('export-holidays-to-xlsx/<str:filter_status>', holiday.exportToXlsx, name="export-holidays-to-xlsx"),
    path('export-holidays-to-pdf/<str:filter_status>', holiday.exportToPDF, name="export-holidays-to-pdf"),
    path('add-pdf/<str:holiday_id>', holiday.addpdf, name="add-pdf"),
    
    path('leave-report', holiday.leaveReport, name='leave-report'),
    path('ajax-leave-report-lists', holiday.ajaxLeaveReportLists, name='ajax-leave-report-lists'),
    path('edit-leave-status', holiday.editLeaveStatus, name='edit-leave-status'),
    path('leave-status-details', holiday.leaveStatusDetails, name='leave-status-details'),
    path('update-leave-status', holiday.updateLeaveStatus, name='update-leave-status'),
    path('update-leave-remark', holiday.updateLeaveRemark, name='update-leave-remark'),
    path('export-leave-report-to-xlsx/<str:columns>/<str:userId>/<str:leave_status>', holiday.leaveExportToXlsx, name='export-leave-report-to-xlsx'),
    path('export-leave-report-to-pdf/<str:columns>/<str:userId>/<str:leave_status>', holiday.leaveExportToPDF, name='export-leave-report-to-pdf'),
    
    

    path('drivers', driver.index, name='drivers'),
    path('ajax-driver-list', driver.ajaxDriverList, name='ajax-driver-list'),
    path('add-driver', driver.addDriver, name='add-driver'),
    path('edit-driver-basic/<int:driver_id>', driver.editDriverBasic, name='edit-driver-basic'),
    path('edit-driver-official/<int:driver_id>', driver.editDriverOfficial, name='edit-driver-official'),
    path('driver-short-details/<int:driver_id>', driver.driverShortDetails, name='driver-short-details'),
    path('driver-details/<int:driver_id>', driver.driverDetails, name='driver-details'),
    path('update-driver-status', driver.updateDriverStatus, name='update-driver-status'),

    path('vehicles', vehicle.index, name='vehicles'),
    path('ajax-vehicle-list', vehicle.ajaxVehicleList, name='ajax-vehicle-list'),
    path('add-vehicle-basic', vehicle.addVehicleBasic, name='add-vehicle-basic'),
    path('edit-vehicle-basic/<int:vehicle_id>', vehicle.editVehicleBasic, name='edit-vehicle-basic'),
    path('edit-vehicle-registration/<int:vehicle_id>', vehicle.editVehicleRegistration, name='edit-vehicle-registration'),
    path('edit-vehicle-other/<int:vehicle_id>', vehicle.editVehicleOther, name='edit-vehicle-other'),
    path('edit-vehicle-route/<int:vehicle_id>', vehicle.editVehicleRoute, name='edit-vehicle-route'),
    path('edit-vehicle-credential/<int:vehicle_id>', vehicle.editVehicleCredential, name='edit-vehicle-credential'),
    path('update-vehicle-status', vehicle.updateVehicleStatus, name='update-vehicle-status'),
    path('vehicle-short-details/<int:vehicle_id>', vehicle.vehicleShortDetails, name='vehicle-short-details'),

    path('vehicle-registration-list/<str:vehicle_id>', vehicle.ajaxRegistrationList, name='vehicle-registration-list'),
    path('add-pollutionDetails/<str:vehicle_id>', vehicle.addPollutionDetails, name='add-pollutionDetails'),
    path('edit-pollutionDetails/<str:pollution_id>', vehicle.editPollutionDetails, name='edit-pollutionDetails'),
    path('add-RegistrationDetails/<str:vehicle_id>', vehicle.addRegistrationDetails, name='add-RegistrationDetails'),
    path('edit-RegistrationDetails/<str:registration_id>', vehicle.editRegistrationDetails, name='edit-RegistrationDetails'),
    path('add-FitnessDetails/<str:vehicle_id>', vehicle.addFitnessDetails, name='add-FitnessDetails'),
    path('edit-FitnessDetails/<str:fitness_id>', vehicle.editFitnesDetails, name='edit-FitnessDetails'),
    path('add-InsuranceDetails/<str:vehicle_id>', vehicle.addInsuranceDetails, name='add-InsuranceDetails'),
    path('edit-InsuranceDetails/<str:insurance_id>', vehicle.editInsuranceDetails, name='edit-InsuranceDetails'),
    path('add-PermitDetails/<str:vehicle_id>', vehicle.addPermitDetails, name='add-PermitDetails'),
    path('edit-PermitDetails/<str:permit_id>', vehicle.editPermitDetails, name='edit-PermitDetails'),
   
    path('students', student.index, name='students'),
    path('ajax-student-list', student.ajaxStudentList, name='ajax-student-list'),
    path('ajax-student-lists', student.ajaxStudentLists, name='ajax-student-lists'),
    path('student-short-details/<str:student_id>', student.studentShortDetail, name='student-short-details'),
    path('filter-student', student.filterStudent, name='filter-student'),
    path('generate-digital-id-card/<str:student_id>', student.generateDigitalIdCard, name='generate-digital-id-card'),
    path('get-student-thumbs/<str:student_id>', student.getStudentThumbs, name='get-student-thumbs'),
    path('generate-id-otp/<str:student_id>', student.generateIdOtp, name='generate-id-otp'),
    path('student/get-by-mobile-number', student.getByMobileNumber, name='student/get-by-mobile-number'),
    path('student/register-face', student.registerFace, name='student/register-face'),
    path('student/get-by-registration-number', student.getByRegistrationNumber, name='student/get-by-registration-number'),
    path('add-student-basic-detail', student.addStudentBasicDetails, name='add-student-basic-detail'),
    path('get-master-details', student.getMasterDetails, name='get-master-details'),
    
    path('get-all-documents',student.getMasterRecord, name='get-all-documents'),
    path('get-documents-details',student.getDocumentData, name='get-documents-details'),
    path('view-documents', student.viewDocuments,name='view-documents'),
    
    # ---------------------------------------------------------------------------------------
    path('add-student-basic-details', student.addNewStudentBasicDetails, name='add-student-basic-details'),
    path('add-student-photo', student.addStudentPhoto, name='add-student-photo'),
    path('edit-student-basic-details', student.editNewStudentBasicDetails, name='edit-student-basic-details'),
    path('add-student-biometric-details', student.addStudentBiometricDetails, name='add-student-biometric-details'),
    path('edit-student-biometric-details', student.editStudentBiometricDetails, name='edit-student-biometric-details'), 
    path('add-student-documents', student.addStudentDocuments, name='add-student-documents'),
    path('student-document-list', student.studentDocumentList, name='student-document-list'),
    path('add-new-folder', student.addNewFolder, name='add-new-folder'),
    path('add-new-file', student.addNewFile, name='add-new-file'),
    path('filter-by-organization', student.filterByOrganization, name='filter-by-organization'),
    path('id-card-editor', student.IdCardEditor, name='id-card-editor'),
    path('image-grabcut', student.ImageGrabCut, name='image-grabcut'),
    path('qr-generator', student.QRGeneration, name='qr-generator'),
    path('id-card-save', student.IDCardSave, name='id-card-save'),
    path('id-card-download', student.IDCardDownload, name='id-card-download'),
    path('show-maps-view', student.showMapsView, name='show-maps-view'),
    path('add-coordinates', student.addCoordinates, name='add-coordinates'),


    # Attendance    
    path('attendance/mark-student-attendance', attendance.markStudentAttendance, name='attendance/mark-student-attendance'),
    path('attendance/new-mark-student-attendance', attendance.newmarkStudentAttendance, name='attendance/new-mark-student-attendance'),
    path('attendance/mark-student-attendance-new', attendance.markStudentAttendanceNew, name='attendance/mark-student-attendance-new'),
    path('attendance/get-student-data/<str:student_id>', attendance.getStudentData, name='attendance/get-student-data'),
    path('attendance/student-attendance-report', attendance.studentAttendanceReport, name='attendance/student-attendance-report'),
    path('attendance/filter-student-attendance-report', attendance.filterStudentAttendanceReport, name='attendance/filter-student-attendance-report'),
    path('attendance/ajax-student-attendance-lists', attendance.ajaxStudentAttendanceLists, name='attendance/ajax-student-attendance-lists'),
    path('student-attendance-details/<str:student_id>', attendance.studentAttendanceDetail, name='student-attendance-details'),

    path('attendance/attendance-summary', attendance.indexSummary, name='attendance/attendance-summary'),
    path('attendance/filter-attendance-summary', attendance.filterSummary, name='attendance/filter-attendance-summary'),
    path('export-attendance-summary-report-to-xlsx/<str:college_id>/<str:course>/<str:sem_year>/<str:filter_date>', attendance.exportToXlsx, name='export-attendance-summary-report-to-xlsx'),
    path('attendance/employee-attendance-summary', attendance.EmployeeSummary, name='attendance/employee-attendance-summary'),
    path('attendance/filter-employee-attendance-summary', attendance.filterEmployeeAttendanceSummary , name='attendance/filter-employee-attendance-summary'),
    path('export-employee-attendance-summary-report-to-xlsx/<str:college_id>/<str:department>/<str:filter_date>', attendance.exportEmployeeAttendanceToXlsx, name='export-employee-attendance-summary-report-to-xlsx'),
    # path('attendance/attendance-stats', attendance.attendanceStat, name='attendance/attendance-stats'),
    # path('attendance/ajax-attendance-stats', attendance.ajaxAttendanceStat, name='attendance/ajax-attendance-stats'),
    # path('attendance/export-attendance-stats/<str:date>', attendance.attendanceStatsExportToXlsx, name='attendance/export-attendance-stats'),

    # path('attendance/attendance-stats', attendance.attendanceStat, name='attendance/attendance-stats'),
    # path('attendance/get-attendance-zone', attendance.getAttendaceZone, name='attendance/get-attendance-zone'),
    # path('attendance/get-register-zone', attendance.getRegisterZone, name='attendance/get-register-zone'),
    # path('attendance/ajax-attendance-stats', attendance.ajaxAttendanceStat, name='attendance/ajax-attendance-stats'),
    # path('attendance/export-attendance-stats/<str:from_date>/<str:to_date>/<str:branch>/<str:semester>', attendance.attendanceStatsExportToXlsx, name='attendance/export-attendance-stats'),
    # path('attendance/export-attendance-stats-reports/<str:list>/<str:branch>/<str:semester>', attendance.attendanceReportExportToXlsx, name='attendance/export-attendance-stats-reports'),
    # path('attendance/filter-register-report', attendance.filterRegisterZone, name='attendance/filter-register-report'),
    
    path('attendance/attendance-stats', attendance.attendanceStat, name='attendance/attendance-stats'),
    path('attendance/get-attendance-zone', attendance.getAttendaceZone, name='attendance/get-attendance-zone'),
    path('attendance/get-register-zone', attendance.getRegisterZone, name='attendance/get-register-zone'),
    path('attendance/ajax-attendance-stats', attendance.ajaxAttendanceStat, name='attendance/ajax-attendance-stats'),
    path('attendance/export-attendance-stats/<str:from_date>/<str:to_date>/<str:branch>/<str:semester>', attendance.attendanceStatsExportToXlsx, name='attendance/export-attendance-stats'),
    path('attendance/export-attendance-stats-reports/<str:list>/<str:branch>/<str:semester>/<str:from_date>/<str:to_date>', attendance.attendanceReportExportToXlsx, name='attendance/export-attendance-stats-reports'),
    path('attendance/filter-register-report', attendance.filterRegisterZone, name='attendance/filter-register-report'),
    
    path('attendance/attendance-report', attendance.attendanceReport, name='attendance/attendance-report'),
    path('attendance/ajax-attendance-report', attendance.ajaxattendanceReport, name='attendance/ajax-attendance-report'),
    path('attendance/export-attendance-report/<str:from_date>/<str:to_date>/<str:semester>', attendance.attendanceReportExportToXlsx, name='attendance/export-attendance-report'),
    path('attendance/export-students-attendance-report/<str:branch_id>/<str:check>/<str:semester>/<str:from_date>/<str:to_date>', attendance.attendanceStudentsReportExportToXlsx, name='attendance/export-students-attendance-report'),
    path('attendance/get-attendance-report', attendance.getAttendaceReport, name='attendance/get-attendance-report'),

    # Firebase notification
    path('save-web-firebase-token', ajax.saveWebFirebaseToken, name='save-web-firebase-token'),
    path('notify-web', ajax.notifyWeb, name='notify-web'),
    
    path('match-face', ajax.matchFace, name='match-face'),
    path('face-image-upload', ajax.regEncodes, name='face-image-upload'),
    path('face-encodings-register', ajax.trainFile, name='face-encodings-register'),
    
    #Teachers View
    path('teacher/login', teachers.login),
    path('teacher/all-registered-students', teachers.getRegisteredList),
    path('teacher/get-questionnaire', teachers.getQuestionnaire),
    path('teacher/post-questionnaire', teachers.postQuestionnaire),
    path('teacher/get-districts', teachers.getDistrictUsingStateID),
    path('teacher/get-tehsil', teachers.getTehsilUsingDistrictID),
    path('teacher/get-village', teachers.getVillageUsingTehsilID),
    path('teacher/save-visit-otp', teachers.VisitOTP),
    path('teacher/homepage', teachers.HomePageAPI),
    path('teacher/visited-student', teachers.getVisitedStudents),
    path('teacher/visited-details', teachers.visitedStudentDetail),

    #Admin
    path('admin/dashboard', admin.HomePageAPI, name='admin/dashboard'),
    path('admin/visit-mapview', admin.visitMapView, name='admin/visit-mapview'),
    path('admin/visited-student', admin.getVisitedStudents, name="admin/visited-student"),
    path('admin/visited-details', admin.visitedStudentDetail, name="admin/visited-details"),
    
    # School Visit
    path('teacher/school-visit', teachers.schoolVisit),
    path('teacher/individual-visit', teachers.individualVisit),
    path('teacher/visit-list', teachers.visitList),
    path('teacher/visit-details', teachers.visitDetails),

    # Widgets
    path('school-visit-mapview', widgets.schoolVisitMapview, name='school-visit-mapview'),
    path('ajax-user-tracking', widgets.ajaxschoolVisit, name='ajax-user-tracking'),
    path('school-visit-details', widgets.schoolVisitDetails, name='school-visit-details'),
    path('export-school-visits/<str:visit_type>/<str:user_id>/<str:date_from>/<str:date_to>', widgets.exportSchoolVisits, name='export-school-visits'),
    
    # Entrance Exam
    path('entrance/registration', entrance_exam.entranceRegistration),
    
    path('get-district-options/<int:state_id>', entranceExamView.districtOption, name='get-district-options'),
    path('get-tehsil-options/<int:district_id>', entranceExamView.tehsilOption, name='get-tehsil-options'),
    path('get-village-options/<int:tehsil_id>', entranceExamView.villageOption, name='get-village-options'),

    path('entrance/enrolled-students', entranceExamView.enrolledStudents, name='entrance/enrolled-students'),
    path('entrance/filter-candidates', entranceExamView.ajaxEnrolledCandidate , name='entrance/filter-candidates'),
    path('entrance/export-candidates/<str:filter_year>/<str:filter_course>/<str:filter_date>/<str:filter_status>', entranceExamView.exportEnrolledListtXLS , name='entrance/export-candidates'),
    
    path('entrance/filter-candidate-result', entranceExamView.ajaxCandidateResult , name='entrance/filter-candidate-result'),
    path('entrance/register-candidate', entranceExamView.addEntranceCandidate, name='entrance/register-candidate'),
    path('entrance/candidate-details/<str:candidate_id>', entranceExamView.getCandidateDetails , name='entrance/candidate-details'),
    path('entrance/edit-candidate/<str:candidate_id>', entranceExamView.editRegistration , name='entrance/edit-candidate'),
    path('entrance/edit-registration', entranceExamView.editCandidate , name='entrance/edit-registration'),
    path('entrance/update-registration', entranceExamView.saveRegistration , name='entrance/update-registration'),

    path('entrance/candidate-result', entranceExamView.candidateResult, name='entrance/candidate-result'),
    # path('entrance/result-details/<str:candidate_id>', entranceExamView.getResultCandidateDetails, name='entrance/result-details'),
    path('entrance/result-details/<str:candidate_id>/<str:quiz_date>', entranceExamView.getResultCandidateDetails, name='entrance/result-details'),
    path('entrance/export-marksheet/<str:filter_date>/<str:filter_percentage>', entranceExamView.exportResultXLS, name='entrance/export-marksheet'),
    
    path('entrance/send-result-sms', entranceExamView.sendResultSMS, name='entrance/send-result-sms'),
    
    path('get-branch-list', ajax.getBranchList, name='get-branch-list'),
    path('get-all-branch-list', ajax.getAllBranchList, name='get-all-branch-list'),
    path('get-branch-sem-year-list', ajax.getBranchSemYearList, name='get-branch-sem-year-list'),
    path('get-student-registration-no', ajax.getStudentRegistrationNo, name='get-student-registration-no'),
    
    
    path('employee-id-card-editor', employees.employeeIdCardEditor,name='employee-id-card-editor'),
    path('employee-qr-generator', employees.employeeQRGeneration,name='employee-qr-generator'),
    path('employee-id-card-save', employees.employeeIDCardSave,name='employee-id-card-save'),
    path('employee-id-card-download', employees.employeeIDCardDownload,name='employee-id-card-download'),
    
    path('attendance/mark-employee-attendance', employees.markEmployeeAttendance,name='attendance/mark-employee-attendance'),
    path('employee/get-by-employee-id', employees.getByEmployeeId,name='employee/get-by-employee-id'),
    path('get-employee-thumbs/<str:emp_id>',employees.getEmployeeThumbs, name='get-employee-thumbs'),

    path('attendance/employee-attendance-report', employees.employeeAttendanceReport,name='attendance/employee-attendance-report'),
    path('attendance/filter-employee-attendance-report', employees.filterEmployeeAttendanceReport,name='attendance/filter-employee-attendance-report'),
    path('attendance/ajax-employee-attendance-lists', attendance.ajaxStudentAttendanceLists,name='attendance/ajax-employee-attendance-lists'),
    path('employee-attendance-details/<str:user_id>',employees.employeeAttendanceDetail, name='employee-attendance-details'),
    path('student/filter-student-list', student.filterStudentList,name='student/filter-student-list'),
    
    path('user-notification', report.userNotification),
    
    path('monthly-attendance-report', report.staffAttendanceSummary, name='monthly-attendance-report'),
    path('attendance/filter-staff-attendance-summary', report.filterStaffAttendanceSummary, name='attendance/filter-staff-attendance-summary'),
    path('export-staff-attendance-summary-report-to-xlsx/<str:filter_date>', report.exportToXlsx, name='export-staff-attendance-summary-report-to-xlsx'),
    path('staff-attendance-reports/<str:user_id>/<str:MonthDate>', report.staffMonthlyAttendance, name='staff-attendance-reports'),
    
    path('ajax-attendance-reports', report.ajaxAttendanceReports, name='ajax-attendance-reports'),
    path('export-attendance-report-to-xlsx/<str:columns>/<str:attendance_start_date>/<str:attendance_end_date>/<str:role_id>', report.exportAttendanceReport, name='export-attendance-report-to-xlsx'),
    path('user-geo-attendance', report.userGeoAttendance, name='user-geo-attendance'),
    
    
    
    path('regularization-report', report.regularizationReport, name='regularization-report'),
    path('ajax-regularization-report-list', report.ajaxRegularizationReportLists, name='ajax-regularization-report-list'),
    path('update-regularization-remark', report.updateRegularizationRemark, name='update-regularization-remark'),
    path('update-regularization-status', report.updateRegularizationStatus, name='update-regularization-status'),
    path('export-regularization-report-to-xlsx/<str:columns>/<str:userId>/<str:regularization_status>', report.regularizationExportToXlsx, name='export-regularization-report-to-xlsx'),


    path('daily-attendance-report', attendance.attendanceReports, name='daily-attendance-report'),
    # path('ajax-daily-attendance-report', attendance.attendanceReports, name='daily-attendance-report'),
    path('view-details/<int:id>', attendance.viewDetails, name='view-details'),  
    path('month-performance-report/<str:month>/<str:year>', attendance.monthPerormanceReport, name='month-performance-report'), 
    
    
    path('user-tracking-report', userManagement.userTrackingReport, name='user-tracking-report'),
    path('ajax-user-tracking/<str:user_id>', userManagement.ajaxUserTracking, name='ajax-user-tracking'),


    path('user-travel-summary', userManagement.userTravelSummary, name='user-travel-summary'),
    path('ajax-user-travel-summary-report', userManagement.ajaxuserTravelSummary, name='ajax-user-travel-summary-report'),
    path('get-travel-user-list', ajax.travelUserOption, name='get-travel-user-list'),
    path('export-user-travel-summary/<str:travel_date>/<str:user_id>/<str:travel_month_picker>/<str:time_period>', userManagement.exportUserTravelSummary, name='export-user-travel-summary'),

    path('user-tracking-report-view/<str:user_id>/<str:trac_date>', userManagement.userTrackingReportView, name='user-tracking-report-view'),
    
]