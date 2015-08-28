from django.conf.urls import patterns, include, url
from school.views import *

coursecatalog_TEMP_urls = patterns('school.views',
    url(r'^CourseCatalogDetail$', view=CourseCatalogDetail.as_view(), name='coursecatalog_detail'),
    url(r'^Update$', view=EditCourseCatalog.as_view(), name='coursecatalog_update'),
    url(r'^Delete$', view=DeleteCourseCatalog.as_view(), name='coursecatalog_delete'),
)

urlpatterns = patterns('school.views',
    url(r'^$', 'index', ),
    url(r'^(?P<pk>[\w-]+).coursecatalog/', include(coursecatalog_TEMP_urls)),

)



# General URLs
urlpatterns += patterns('school.views',
    url(r'^thanks/$', 'thanks', name='changes_made',  ),
    url(r'^NewFamilyForm_error/$', 'NewFamilyForm_error', name='NewFamilyForm_error',  ),
    url(r'^NewFamilyForm_success/$', 'NewFamilyForm_success', name='NewFamilyForm_success',  ),
)

# Course Catalog URLs
urlpatterns += patterns('school.views',
    url(r'^CatalogAll$', view=AllCourseCatalogList.as_view(), name='all_coursecatalog_list',  ),
    url(r'^CatalogAll/(?P<page>\w+)/$', view=AllCourseCatalogList.as_view(), name='all_coursecatalog_list',  ),
    url(r'^CatalogAll/(\w+)/(\w+)/$', view=AllCourseCatalogList.as_view(), name='all_coursecatalog_list',  ),
    url(r'^NewCourseCatalog', NewCourseCatalog.as_view(), name='coursecatalog_add'),
)

# Schedule URLs
urlpatterns += patterns('school.views',
    url(r'^AttendanceSheetsReport$', GetAttendanceSheets,  name='attendance_sheets_report',  ),
    url(r'^ScheduleList$', ScheduleList,  name='schedule_list',  ),
    url(r'^FamilyScheduleReport$', GetFamilyScheduleReport,  name='family_schedule_report',  ),
    url(r'^FamilyScheduleCSV$', GetFamilyScheduleReport, {'csv': '1'}, name='family_schedule_csv',  ),
    url(r'^FamilySchedule$', GetFamilySchedule,  name='family_schedule',  ),
    url(r'^FamilySchedulePrintable$', GetFamilySchedule, {'printable': '1'}, name='family_schedule_printable',  ),
    url(r'^FamilySchedule/(?P<family_id>\d+)/$', GetFamilySchedule,  name='family_schedule',  ),
    url(r'^CourseEnrollList$', CourseEnrollList,  name='course_enroll_list',  ),
    url(r'^CourseEnrollListPrintable$', CourseEnrollList, {'printable': '1'}, name='course_enroll_list_printable',  ),
    url(r'^AllCourseEnrollList$', AllCourseEnrollList,  name='all_course_enroll_list',  ),
    url(r'^AttendanceSheetsCSV$', AllCourseEnrollList, {'csv': '1'}, name='attendance_sheets_csv',  ),
    url(r'^EnrollStudent/(?P<family_member>\d+)/(?P<schedule_id>\d+)/(?P<semester_period_id>\d+)/$', EnrollStudent,  name='enroll_student',  ),
    url(r'^EnrollAssistant/(?P<family_member>\d+)/(?P<schedule_id>\d+)/(?P<semester_period_id>\d+)/$', EnrollAssistant,  name='enroll_assistant',  ),
    url(r'^EmailClass/(?P<schedule_id>\d+)/$', EmailClass,  name='email_class',  ),
    url(r'^EmailClassTeacher/(?P<schedule_id>\d+)/$', EmailClassTeacher,  name='email_class_teacher',  ),
    url(r'^EmailClassAssistant/(?P<schedule_id>\d+)/$', EmailClassAssistant,  name='email_class_assistant',  ),
    url(r'^EmailGroup$', EmailGroup,  name='email_group',  ),
)


# Semester URLs
urlpatterns += patterns('school.views',
    url(r'^semester_information/$', 'semester_information', name='semester_information'),
)

# Family URLs
urlpatterns += patterns('school.views',
    url(r'^family_member_information/$', 'manage_family_member', name='manage_family_member'),
    url(r'^student_information/$', 'manage_student', name='manage_student'),
    url(r'^NewFamilyForm$', 'post_form_NewFamilyForm', name='post_form_NewFamilyForm'),
    url(r'^NewFamilyMember$', 'add_new_FamilyMember', name='add_new_FamilyMember'),
    url(r'^ActiveFamilyMemberHeadList$', 'active_family_member_head_list', name='active_family_member_head_list'),
    url(r'^ActiveStudentList$', 'active_student_list', name='active_student_list'),

)

# Event URLs
urlpatterns += patterns('school.views',
    url(r'^Events$', EventList.as_view(), name='event_list'),
    url(r'^Events/$', EventList.as_view(), name='event_list'),
    url(r'^Events/new$', EventCreate.as_view(), name='event_new'),
    url(r'^Events/edit/(?P<pk>\d+)$', EventUpdate.as_view(), name='event_edit'),
    url(r'^Events/delete/(?P<pk>\d+)$', EventDelete.as_view(), name='event_delete'),
    url(r'^Events/new/enrollment/(?P<pk>\d+)$', EventAddEnrollment.as_view(), name='event_add_enrollment'),
    url(r'^Events/delete/enrollment/(?P<pk>\d+)$', EventDeleteEnrollment.as_view(), name='event_delete_enrollment'),
    url(r'^EmailEvent/(?P<event_id>\d+)/$', EmailEvent,  name='email_event',  ),
)

# Admin URLs
urlpatterns += patterns('school.views',
    url(r'^IncrementGrade/$', increment_grade, name='increment_grade', ),
    url(r'^CopyClassEnrollment1/$', copy_class_enrollment1, name='copy_class_enrollment1', ),
    url(r'^CopyClassEnrollment2/$', copy_class_enrollment2, name='copy_class_enrollment2', ),
)

# Email URLs
urlpatterns += patterns('school.views',
    url(r'^sendEmail/$', send_email, name='send_email', ),
    url(r'^contact/$', contact_email, name='contact_email',),
)

