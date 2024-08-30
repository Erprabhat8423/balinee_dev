from django.urls import path,re_path
from ..views import *

app_name = 'src'
urlpatterns = [
    path('api/verify-id-pin', auth.verifyIdPin),
    path('api/login', auth.login),
    path('api/approval-requests', auth.approvalRequests),
    path('api/update-policy-status', auth.updatePolicyStatus),
    path('api/update-holiday-status', auth.updateHolidayStatus),
    path('api/notification-list', auth.notificationList),
    path('api/teacher-login', teachers.login),
    path('api/student-document-list', students.studentDocumentList),
    path('api/upload-document', students.uploadDocument),
    
    path('api/employee-document-list', teachers.employeeDocumentList),
    path('api/upload-employee-document', teachers.uploadEmployeeDocument),
    
    # Admin App Api's
    path('api/student-attendance-list', admin.studentAttendanceList),
    path('api/employee-attendance-list', admin.employeeAttendanceList),
    path('api/student-attendance-master-data', admin.studentAttendanceMasterData),
    path('api/dashboard-data', admin.dashboardData),
    path('api/dashboard', admin.dashboard),
    path('api/visited-student', admin.getVisitedStudents),
    path('api/visited-details', admin.visitedStudentDetail),
    path('api/visit-mapview', admin.visitMapView),
    path('api/student-QR-data', admin.studentQRData),
    
    # Employee App Api's
    path('api/user-attendance', auth.userAttendance),
    path('api/check-attendances', auth.checkAttendance),
    path('api/get-dashboard-data',auth.getDashboardData),
    path('api/get-attendance-dashboard-data',auth.getAttendanceData),
    path('api/get-master-data', auth.getMasterData),

    path('api/save-tracking-data', auth.saveUserTracking),
    path('api/user-location-log', auth.userLocationLog),
    path('api/apply-leave', auth.applyLeave),
    path('api/applied-leaves', auth.appliedLeaves),
    path('api/update-user-location', auth.updateUserLocation),
    path('api/logout', auth.logout),
    
    path('api/user-location-log', auth.userLocationLog),
    
    # Recruiter App APIs
    path('api/candidate-list', candidate_api.candidateList),
    path('api/update-candidate-status', candidate_api.updateCandidateStatus),
    
    
    path('api/handover-leave-request-list', auth.handOverLeaveRequestList),
    path('api/leave-forword', auth.leaveForword),
    path('api/upload-pending-leave-document', auth.uploadPendingUserLeaveDocument),
    
    path('api/save-user-regularization-data',auth.saveUserRegularizationData),
    
    path('cron/user-day-out', auth.userDayOut),
    
    # new api's
    path('api/save-ta-visit', visitManagement.saveTAVisit),
    path('api/get-ta-data', visitManagement.getVisitData),
    path('api/create-visit-Check-in', visitManagement.createVisitCheckin),
    path('api/create-visit-Check-out', visitManagement.createVisitCheckout),
    path('api/visit-list', visitManagement.visitList),
    path('api/visit-history-list', visitManagement.visitHistoryList),
    path('api/save-mpp-visit-history', visitManagement.saveMppVisitHistory),
    path('api/visit-history-details', visitManagement.visitHistoryDetails),
    
    
]