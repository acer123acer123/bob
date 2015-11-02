import re
import select2.fields
from django.db import models
from django.db.models import Q
from datetime import date, datetime
from time import strptime
from django.conf import settings
from django.views.generic.list import ListView
from school.models import *
from school.mailgun import *
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from school.forms import CourseCatalogForm, SemesterForm, NewFamilyForm, NewFamilyMemberForm, ContactForm
from school.forms import EmailClassForm, EventForm, EventEnrollmentForm , EventAddEnrollmentForm, EmailGroupForm, EmailEventForm
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.forms.models import modelformset_factory, BaseModelFormSet, formset_factory, inlineformset_factory
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404, render_to_response, render, redirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.template import RequestContext, loader, Context
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.hashers import make_password, check_password, is_password_usable
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.db.models import Count
from stronghold.decorators import public
from django.core.mail import send_mail, EmailMultiAlternatives, BadHeaderError
from collections import defaultdict
import string, random
from django.forms.widgets import CheckboxSelectMultiple
from django.db import transaction
from post_office import mail



def email_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size)) + '@NOTSET.com'

def username_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size)) 


@public
def index(request):
    is_ie = False
    if request.META.has_key('HTTP_USER_AGENT'):
        user_agent = request.META['HTTP_USER_AGENT']
 
        # Test IE 1-9
        pattern = "msie [1-9]\."
        prog = re.compile(pattern, re.IGNORECASE)
        match = prog.search(user_agent)
 
    if match:
        is_ie = True  # NOOOOOO

    return render_to_response('school/index.html', {'is_ie': is_ie,}, context_instance=RequestContext(request))

def thanks(request):
    return render_to_response('school/changes_made.html', {}, context_instance=RequestContext(request))

def NewFamilyForm_error(request):
    return render_to_response('school/family/post_form_NewFamilyForm_error.html', {}, context_instance=RequestContext(request))

def NewFamilyForm_success(request):
    return render_to_response('school/family/post_form_NewFamilyForm_success.html', {}, context_instance=RequestContext(request))

class CourseScheduleMixin(object):
    model = CourseCatalog
    def get_context_data(self, **kwargs):
        kwargs.update({'object_name':'CourseCatalog', 'active_semester': self.request.session.get('active_semester'),})
        return kwargs

class CourseCatalogFormMixin(CourseScheduleMixin):
    form_class = CourseCatalogForm
    template_name = 'school/course_catalog/new_edit_form.html'

class AllCourseCatalogList(ListView):
    model = CourseCatalog
    template_name = 'school/course_catalog/list.html'
    paginate_by=10
    def get_queryset(self):
        qs = self.model.objects.all()
        s = self.request.GET.get('s')
        if s:
            return qs.filter(Q(course_name__icontains=s) | Q(course_desc__icontains=s) | Q(teacher__family_member__family__name__icontains=s) | Q(teacher__family_member__first_name__icontains=s))
        else:
            return qs

class CourseCatalogDetail(CourseScheduleMixin, DetailView):
    model = CourseCatalog
    template_name = 'school/course_catalog/detail.html'

class NewCourseCatalog(CourseCatalogFormMixin, CreateView):
    model = CourseCatalog
    pass

class EditCourseCatalog(CourseCatalogFormMixin, UpdateView):
    model = CourseCatalog
    pass

class DeleteCourseCatalog(CourseScheduleMixin, DeleteView):
    model = CourseCatalog
    template_name = 'school/course_catalog/confirm_delete.html'
    def get_success_url(self):
        return reverse('couresecatalog_list')

def active_student_list(request):
    context = RequestContext(request)
    #s_list = Student.objects.all().order_by('grade__order', 'family_member__last_name')
    s_list = Student.objects.filter(family_member__is_active=1).order_by('grade__order', 'family_member__last_name')
    return render_to_response('school/family/active_student_list.html', {
        's_list': s_list, }, context)

def active_family_member_head_list(request):
    context = RequestContext(request)
    f_list = Family.objects.select_related().filter(is_active=1).order_by('name')
    return render_to_response('school/family/active_family_member_head_list.html', {
        'f_list': f_list, }, context)

def ScheduleList(request):
    context = RequestContext(request)
    if request.session.get('active_semester', False):
        active_semester = request.session['active_semester']
        semester_is_active = Semester.objects.get(name=active_semester)
        if not semester_is_active.is_active:
            return render_to_response('school/schedule/wrong_semester.html', {}, context_instance=RequestContext(request))
        s_list = Schedule.objects.filter(semester=active_semester)
        family_student_list = Student.objects.filter(family_member__family=request.user.family).filter(family_member__is_active='True')
        family_assistant_list = Assistant.objects.filter(family_member__family=request.user.family)
        fed=Family.objects.filter(name=request.user.family).dates('family_benefits__enrollment_date','day')
        family_enrollment_date=""
        for i in fed:
            family_enrollment_date=i

        for schedule in s_list:
            schedule.enrolled_family_student_ids = schedule.get_enrolled_family_student_ids(
                family_student_list, active_semester)
            schedule.enrolled_family_assistant_ids = schedule.get_enrolled_family_assistant_ids(
                family_assistant_list, active_semester)

        return render_to_response('school/schedule/list.html', {
            's_list': s_list,
            'semester_is_active': semester_is_active,
            'family_student_list': family_student_list,
            'family_assistant_list': family_assistant_list,
            'family_enrollment_date': family_enrollment_date,
            'today': datetime.now().date(),
        }, context)
    else:
        return redirect('semester_information')


def semester_information(request):
    if request.method == 'POST':
        form = SemesterForm(request.POST)
        if form.is_valid():
            request.session['active_semester'] = form.cleaned_data['semester']
        return redirect('/school/thanks/')
    else:
        form = SemesterForm()

    context = RequestContext(request,{
        'form': form,
    })
    return render_to_response('school/schedule/set_active_semester.html', context)

class FamilyBaseFormSet(BaseModelFormSet):
    def add_fields(self, form, index):
        super(FamilyBaseFormSet, self).add_fields(form, index)
        form.fields['state'].widget.attrs['class'] = 'input-mini'
        form.fields['zip_code'].widget.attrs['class'] = 'input-small'
        form.fields['emergency_notes'].widget.attrs['rows'] = '2'
        form.fields['notes'].widget = forms.HiddenInput()
        form.fields['is_active'].widget = forms.HiddenInput()
        form.fields['family_benefits'].widget = forms.HiddenInput()

class FamilyMemberBaseFormSet(BaseModelFormSet):
    def add_fields(self, form, index):
        super(FamilyMemberBaseFormSet, self).add_fields(form, index)
        form.fields['email_list'].widget = CheckboxSelectMultiple()
        form.fields['email_list'].queryset = EmailList.objects.get_user()
        form.fields['first_name'].widget.attrs['class'] = 'input-small'
        form.fields['first_name'].required = True
        form.fields['first_name'].error_messages = {'required': 'Please enter a first name'}
        form.fields['middle_name'].widget.attrs['class'] = 'input-mini'
        form.fields['last_name'].widget.attrs['class'] = 'input-small'
        form.fields['last_name'].required = True
        form.fields['last_name'].error_messages = {'required': 'Please enter a last name'}
        form.fields['state'].widget.attrs['class'] = 'input-mini'
        form.fields['zip_code'].widget.attrs['class'] = 'input-small'
        form.fields['gender'].widget = forms.HiddenInput()
        form.fields['family'].widget = forms.HiddenInput()
        #form.fields['username'].widget = forms.HiddenInput()
        form.fields['password'].widget = forms.PasswordInput()
        form.fields['last_login'].widget = forms.HiddenInput()
        form.fields['date_joined'].widget = forms.HiddenInput()
        form.fields['family_member_role'].widget = forms.HiddenInput()
        form.fields['notes'].widget = forms.HiddenInput()
        form.fields['is_superuser'].widget = forms.HiddenInput()
        #form.fields['is_active'].widget = forms.HiddenInput()
        form.fields['is_staff'].widget = forms.HiddenInput()

    def clean(self):
        super(FamilyMemberBaseFormSet, self).clean()
        for form in self.forms:
            if not is_password_usable(form.cleaned_data['password']):
                form.instance.password = make_password(form.cleaned_data['password'])

def manage_family_member(request):

    FamilyInlineFormSet = modelformset_factory(Family, extra=0, formset=FamilyBaseFormSet, exclude=('',) )
    FamilyMemberInlineFormSet = modelformset_factory(FamilyMember,
        extra=0, formset=FamilyMemberBaseFormSet, exclude=('',))
    emaillist = EmailList.objects.filter(is_active=True)
    emaillist = EmailList.objects.get_user()
    if request.method == "POST":
        #family_formset = FamilyInlineFormSet(request.POST,  request.FILES,
                #queryset=Family.objects.filter(id=request.user.family.id), prefix='f')
        #family_member_formset = FamilyMemberInlineFormSet(request.POST, request.FILES,
        #        queryset=FamilyMember.objects.filter(family=request.user.family.id), prefix='fm')
        family_formset = FamilyInlineFormSet(request.POST, prefix='f')
        family_member_formset = FamilyMemberInlineFormSet(request.POST, prefix='fm')
        if family_formset.is_valid() and family_member_formset.is_valid():
            family_formset.save()
            for form in family_member_formset:
                fmform = form.save(commit=False)
                #new_password = form.cleaned_data.get('new_password')

                
                    
                matches = fmform.email_list.get_admin().all()
                elist=[]
                for e in matches:
                    elist.append(e) 
                fmform.save()
                form.save_m2m()
                for ae in elist:
                    fmform.email_list.add(ae)

            return redirect('/school/thanks/')
    else:
        family_formset = FamilyInlineFormSet(queryset=Family.objects.filter(id=request.user.family.id), prefix='f')
        family_member_formset = FamilyMemberInlineFormSet(queryset=FamilyMember.objects.filter(family=request.user.family.id), prefix='fm')

    context = RequestContext(request,{
        'emaillist': emaillist,
        'family_formset': family_formset,
        'family_member_formset': family_member_formset,
    })

    return render_to_response("school/family/manage_family_members.html", context)


class StudentBaseFormSet(BaseModelFormSet):

    def add_fields(self, form, index):
        super(StudentBaseFormSet, self).add_fields(form, index)
        form.fields['food_allergies'].widget.attrs['rows'] = '2'
        form.fields['notes'].widget.attrs['rows'] = '1'
        form.fields['grade'].widget.attrs['class'] = 'span5'
        form.fields['birth_date'].widget.attrs['class'] = 'input-small'
        #form.fields['emergency_notes'].widget.attrs['rows'] = '2'

def manage_student(request):
    student_name_dict = {}
    for a in Student.objects.filter(family_member__family_id=request.user.family.id):
        student_name_dict[a.family_member.id]=a.family_member.first_name
    StudentInlineFormSet = modelformset_factory(Student, extra=0, formset=StudentBaseFormSet, exclude=('schedule',))
    if request.method == "POST":
        student_formset = StudentInlineFormSet(request.POST, request.FILES,
                queryset=Student.objects.filter(family_member__family_id=request.user.family.id))
        if student_formset.is_valid():
            student_formset.save()
            return redirect('/school/thanks/')
    else:
        student_formset = StudentInlineFormSet(queryset=Student.objects.filter(family_member__family_id=request.user.family.id))

    context = RequestContext(request,{
        'student_formset': student_formset,
        'student_name_dict': student_name_dict,
    })
    return render_to_response("school/family/manage_student.html", context)

def EnrollStudent(request, family_member, schedule_id, semester_period_id):
    st = Student.objects.get(family_member=family_member)
    sc = Schedule.objects.get(pk=schedule_id)
    sm = request.session.get('active_semester')
    sp = SemesterPeriod.objects.get(pk=semester_period_id)
    enrollment = StudentEnroll(student=st, schedule_id=sc.id)
    test_enrollment = StudentEnroll.objects.filter(student=st, schedule__semester=sm, schedule__semester_period=sp)
    if test_enrollment:
        test_enrollment.delete()

    enrollment.save()
    return redirect('/school/ScheduleList')

def EnrollAssistant(request, family_member, schedule_id, semester_period_id):
    st = Assistant.objects.get(family_member=family_member)
    sc = Schedule.objects.get(pk=schedule_id)
    sm = request.session.get('active_semester')
    sp = SemesterPeriod.objects.get(pk=semester_period_id)
    enrollment = AssistantEnroll(assistant=st, schedule_id=sc.id)
    test_enrollment = AssistantEnroll.objects.filter(assistant=st, schedule__semester=sm, schedule__semester_period=sp)
    if test_enrollment:
        test_enrollment.delete()

    enrollment.save()
    return redirect('/school/ScheduleList')

def GetFamilyScheduleReport(request, family_id=None, csv=None):
    # Displays a cross reference table with sudents as rows and
    #    semester periods as columns.
    # Currently, the family filter and printable is not in use. They are
    #    placed here for possible use in the future.

    context = RequestContext(request)

    if request.session.get('active_semester', False):
        if family_id:
            fn = family_id
        else:
            fn = request.user.family
        sm = request.session.get('active_semester')

        # Fetch all the enrolled data; this puts them in a list of tuples like
        # [("Chris", "Math", "1st_Period"), ("Kim", "Science", "3rd_Period"), ... ]
        student_enrolls = StudentEnroll.objects.filter(schedule__semester=sm).values_list('student__family_member__first_name', 'student__family_member__last_name', 'student__family_member__family__name', 'schedule__course_catalog__course_name', 'schedule__semester_period__name')

        assistant_enrolls = AssistantEnroll.objects.filter(schedule__semester=sm).values_list('assistant__family_member__first_name', 'assistant__family_member__last_name', 'assistant__family_member__family__name', 'schedule__course_catalog__course_name', 'schedule__semester_period__name')

        teacher_enrolls = Schedule.objects.filter(semester=sm).values_list('teacher__family_member__first_name', 'teacher__family_member__last_name', 'teacher__family_member__family__name', 'course_catalog__course_name', 'semester_period__name')


        # get names of all periods in a flat list like: ['1st_Period', '2nd_Period', '3rd_Period']
        periods=SemesterPeriod.objects.filter(semester=sm).values_list('name', flat=True).order_by('name')

        # enumerate(periods) is a generator that has data in the form
        # [(0, '1st_Period'), (1, '2nd_Period'), (2, '3rd_Period')] -- it enumerates the list.
        # I then use a list comprehension to reverse it:
        # [(period,i) for i,period in enumerate(periods)] is
        # [('1st_Period', 0), ('2nd_Period', 1), ...]
        # and then convert that list of paired tuples into a dictionary:
        # {'1st_Period': 0, '2nd_Period': 1, '3rd_Period': 2}
        # period_dict['3rd_Period'] returns 2; indicating that classes that are third period
        # should fall into a students schedule in the third slot of the list
        # (first element of list is 0)
        period_dict = dict([(period,i) for i,period in enumerate(periods)])
        period_list = list(period_dict.items()) 


        # a defaultdict that when a new student (not previously stored) is seen
        # initializes that student to have an empty schedule.
        # the empty schedule is an empty list that is as long as the number of periods,
        # with each period an empty string ''
        # student_dict once fully populated will be of form
        # {'Chris': ['Math', '', 'Science'], 'Kim': ['', 'History', 'Science']}
        # Note student_dict['Chris'] = ['Math', '', 'Science'] and
        # student_dict['Chris'][0] = 'Math'
        students_dict = defaultdict(lambda: [""]*len(periods))
        for (student_first_name, student_last_name, student_family, course, period) in student_enrolls:
            # go through the list of enrolls and assign courses to the schedule in the appropriate spots.
            students_dict['(' + student_family +') ' + student_first_name + ' ' + student_last_name][period_dict[period]] = course

        # [['Chris', ['Math', '', 'Science']], ['Kim', ['', 'History', 'Science']],]
        student_list = sorted(list(students_dict.items()))
   
        # Now, let's do the same thing for assistants.
        assistants_dict = defaultdict(lambda: [""]*len(periods))
        for (assistant_first_name, assistant_last_name, assistant_family, course, period) in assistant_enrolls:
            # go through the list of enrolls and assign courses to the schedule in the appropriate spots.
            assistants_dict['(' + assistant_family +') ' + assistant_first_name + ' ' + assistant_last_name][period_dict[period]] = course

        # [['Chris', ['Math', '', 'Science']], ['Kim', ['', 'History', 'Science']],]
        assistant_list = sorted(list(assistants_dict.items()))
   
        # Now, let's do the same thing for teachers.
        teachers_dict = defaultdict(lambda: [""]*len(periods))
        for (teacher_first_name, teacher_last_name, teacher_family, course, period) in teacher_enrolls:
            # go through the list of enrolls and assign courses to the schedule in the appropriate spots.
            teachers_dict['(' + teacher_family +') ' + teacher_first_name + ' ' + teacher_last_name][period_dict[period]] = course

        # [['Chris', ['Math', '', 'Science']], ['Kim', ['', 'History', 'Science']],]
        teacher_list = sorted(list(teachers_dict.items()))
    
        if csv:
            htmlTemplate='school/schedule/family_schedule_report.csv'
            lCsvFile = render_to_string(htmlTemplate, { 
                'student_list': student_list,
                'assistant_list': assistant_list,
                'teacher_list': teacher_list,
                'periods': periods,
            })
            lResponse = HttpResponse(content_type="text/csv")
            lResponse['Content-Disposition'] = "attachment; filename=family_schedule.csv"
            lResponse.write(lCsvFile)
            return lResponse
        else:
            htmlTemplate='school/schedule/family_schedule_report.html'

        return render_to_response(htmlTemplate, {
            'student_list': student_list,
            'assistant_list': assistant_list,
            'teacher_list': teacher_list,
            'periods': periods,
        }, context)

    else:
        return redirect('semester_information')


def GetFamilySchedule(request, family_id=None, printable=None):
    context = RequestContext(request)
    if printable:
       htmlTemplate='school/schedule/family_schedule_printable.html'
    else:
       htmlTemplate='school/schedule/family_schedule.html'


    if request.session.get('active_semester', False):
        if family_id:
            fn = family_id
        else:
            fn = request.user.family
        sm = request.session.get('active_semester')

        se = StudentEnroll.objects.filter(student__family_member__family=fn, schedule__semester=sm.id).select_related().order_by('student', 'schedule__semester_period')
        sa = AssistantEnroll.objects.filter(assistant__family_member__family=fn, schedule__semester=sm.id).select_related().order_by('assistant','schedule__semester_period')
        te = Schedule.objects.filter(teacher__family_member__family=fn, semester=sm.id)
        semester_name = Semester.objects.get(name=sm)
        return render_to_response(htmlTemplate, {
            'se': se,
            'sa': sa,
            'te': te,
        }, context)

    else:
        return redirect('semester_information')

def CourseEnrollList(request, printable=None):
    context = RequestContext(request)
    if printable:
       htmlTemplate='school/schedule/my_course_enroll_list_printable.html'
    else:
       htmlTemplate='school/schedule/my_course_enroll_list.html'

    if request.session.get('active_semester', False):
        fn = request.user.id
        sm = request.session.get('active_semester')

        te = Schedule.objects.select_related().filter(teacher__family_member=fn, semester=sm)

        return render_to_response(htmlTemplate, {
            'te': te,
        }, context)

    else:
        return redirect('semester_information')

#def AllCourseEnrollList(request):
#    context = RequestContext(request)
#    if request.session.get('active_semester', False):
#        fn = request.user.id
#        sm = request.session.get('active_semester')
#
#        te = Schedule.objects.select_related().filter(semester=sm).prefetch_related('teacher')
#
#        return render_to_response('school/schedule/course_enroll_list.html', {
#            'te': te,
#        }, context)
#
#    else:
#        return redirect('semester_information')
def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def AllCourseEnrollList(request, csv=None):
    # See docs/multi-dictionary for schedule_array layout including sample data

    context = RequestContext(request)

    if request.session.get('active_semester', False):
        from collections import OrderedDict
        fn = request.user.id
        sm = request.session.get('active_semester')

        semester_dates = SemesterDates.objects.filter(semester=sm)
        schedule = Schedule.objects.filter(semester=sm).select_related()
        student_enrolls = StudentEnroll.objects.filter(schedule__semester = sm).values_list('schedule__pk', 'student__family_member__first_name', 'student__family_member__last_name', 'student__grade__name', 'student__birth_date').order_by('student__family_member__last_name')
        assistant_enrolls = AssistantEnroll.objects.filter(schedule__semester = sm).values_list('schedule__pk', 'assistant__family_member__first_name', 'assistant__family_member__last_name').order_by('assistant__family_member__last_name')
        #schedule_array={}
        schedule_array=OrderedDict()
        for a in schedule:
            schedule_array[a.id]={'course':a.course_catalog.course_name, 'students': [], 'teachers': a.teacher.all(), 'assistants': [], 'grades': a.semester_grade.all(), 'period':a.semester_period, 'location':a.course_location} 

        for (pk, fname, lname, grade, birth) in student_enrolls:
            schedule_array[pk]['students'].append([fname + ' ' + lname, grade, calculate_age(birth)])

        for (pk, fname, lname) in assistant_enrolls:
            schedule_array[pk]['assistants'].append(fname + ' ' + lname)

        # Sort the array by period
        #schedule_array=sorted(schedule_array.iteritems(), key=lambda (k,v): schedule_array[k]['period'])
        #schedule_array=sorted(schedule_array.iteritems(), key=lambda (k,v): (schedule_array[k]['period'], schedule_array[k]['course']))
        if csv:
            #import xlwt
            #response = HttpResponse(content_type='application/ms-excel')
            #response['Content-Disposition'] = 'attachment; filename=attendance_sheets_report.xls'
            #wb = xlwt.Workbook(encoding='utf-8')
            #ws = wb.add_sheet("Attendance")
          
            #row_num = 0
            
            #font_style = xlwt.XFStyle()
            #font_style.font.bold = True

            #for c in schedule:
            #    row_num += 1
            #    row = [
        #           schedule_array[c.id]['course']
        #        ]
        #        for col_num in xrange(len(row)):
        #           ws.write(row_num, col_num, row[col_num], font_style)
        #       row_num += 1
        #       row = [
        #           "Instructor:",
        #           " ",
        #           schedule_array[c.id]['location'].name,
        #            ]
        #        for col_num in xrange(len(row)):
        #           ws.write(row_num, col_num, row[col_num], font_style)
        #       for a in schedule_array[c.id]['assistants']:
        #           row_num += 1
        #           row = [
        #                a,
        #            ]
        #            for col_num in xrange(len(row)):
        #               ws.write(row_num, col_num, row[col_num], font_style)
        #    wb.save(response)
        #    return response 
            htmlTemplate='school/schedule/attendance_sheets_report.csv'
            lCsvFile = render_to_string(htmlTemplate, {
                'semester_dates': semester_dates,
                'schedule': schedule,
                'schedule_array': schedule_array,
            })
            lResponse = HttpResponse(content_type="text/csv")
            lResponse['Content-Disposition'] = "attachment; filename=attendance_sheets_report.csv"
            lResponse.write(lCsvFile)
            return lResponse
        else:
            htmlTemplate='school/schedule/course_enroll_list.html'

        return render_to_response(htmlTemplate, {
            'semester_dates': semester_dates,
            'schedule': schedule,
            'schedule_array': schedule_array,
        }, context)
    else:
        return redirect('semester_information')


def AttendanceCSV(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

    # The data is hard-coded here, but you could load it from a database or
    # some other source.
    csv_data = (
        ('First row', 'Foo', 'Bar', 'Baz'),
        ('Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"),
    )

    t = loader.get_template('school/schedule/attendancecsv.txt')
    c = Context({
        'data': csv_data,
    })
    response.write(t.render(c))
    return response

def add_new_FamilyMember(request):
    form = NewFamilyMemberForm(request.POST or None)
    if form.is_valid():
        model_instance = form.save(commit=False)
        model_instance.family = Family.objects.get(id=request.user.family.id)
        model_instance.family_member_role_id = 1
        model_instance.email = email_generator()
        model_instance.password = "I am not setting a password"
        first_name = form.cleaned_data['first_name']
        first_name = first_name.replace(" ", "")
        last_name = form.cleaned_data['last_name']
        last_name = last_name.replace(" ", "")
        username = first_name+"."+last_name
        model_instance.last_login=datetime.now().date()
        if len(username) > 30:
            username = username[:30]

        if FamilyMember.objects.filter(username=username).exists():
            username=last_name+"."+username_generator()
        model_instance.username=username
        model_instance.save()

        family_member = FamilyMember.objects.get(username=username)
        student_post = Student.objects.create(family_member = family_member, grade_id = 1, birth_date = '2000-01-01')

        return redirect('/school/student_information/')

    return render(request, 'school/family/add_new_FamilyMember.html', { 'form': form,})

@public
def post_form_NewFamilyForm(request):
    family_name_unique=0
    form = NewFamilyForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data['username']
        first_name = form.cleaned_data['first_name']
        first_name = first_name.replace(" ", "")
        last_name = form.cleaned_data['last_name']
        last_name = last_name.replace(" ", "")
        password = make_password(form.cleaned_data['password'])
        address1 = form.cleaned_data['address1']
        address2  = form.cleaned_data['address2']
        city = form.cleaned_data['city']
        state = form.cleaned_data['state']
        zip_code = form.cleaned_data['zip_code']
        email_address = form.cleaned_data['email_address']
        phone_number = form.cleaned_data['phone_number']
        cell_phone_number = form.cleaned_data['cell_phone_number']
        gender = form.cleaned_data['gender']
        reason_for_registration = form.cleaned_data['reason_for_registration']
        if Family.objects.filter(name=last_name).exists():
            if Family.objects.filter(name=last_name+"."+first_name).exists():
                return redirect('/school/NewFamilyForm_error/')
            else:
                name = last_name+"."+first_name
        else:
                name = last_name
        post = Family.objects.create(name=name,
                                         address1=address1,
                                         city=city,
                                         state=state,
                                         zip_code=zip_code,
                                         is_active=0,
                                         email_address=email_address,
                                         cell_phone_number=cell_phone_number,
                                         phone_number=phone_number)

        #username = first_name+"."+last_name
        #if len(username) > 30:
        #    username = username[:30]

        if FamilyMember.objects.filter(username=username).exists():
            if FamilyMember.objects.filter(username=username+".123").exists():
                return redirect('/school/NewFamilyForm_error/')
            else:
                username = username+".123"

        family = Family.objects.get(name=name)
        post = FamilyMember.objects.create(username=username,
                                        family=family,
                                        password=password,
                                        gender=gender,
                                        is_superuser=0,
                                        last_login=datetime.now().date(),
                                        first_name=first_name,
                                        last_name=last_name,
                                        email=email_address,
                                        is_staff=0,
                                        is_active=0)
        family_member = FamilyMember.objects.get(username=post.username)
        assistant_post = Assistant.objects.create(family_member = family_member)
        teacher_post = Teacher.objects.create(family_member = family_member)
        context = RequestContext(request,{
            'username':username,
            'password':password,
        })

        subject = "FRED: New family has registered (" + last_name + ")"
        reason_for_registration_string = ', '.join(request.POST.getlist('reason_for_registration'))
        message = "The " + last_name + " family has registered on FRED.  The reason for registration: " + reason_for_registration_string
        sender = "kimberly.ryan@gmail.com"
        recipients = ('kimberly.ryan@gmail.com')
        text_content = strip_tags(message)
        #a = send_simple_message(sender, recipients, subject, message) 
        if reason_for_registration_string.find('co-op') > -1:
            mail.send(
                [email_address],
                'kimberly.ryan@gmail.com',
                template='Welcome_Co-op',
            )
        elif reason_for_registration_string.find('High') > -1:
            mail.send(
                [email_address],
                'kimberly.ryan@gmail.com',
                template='Welcome_HighSchool',
            )
        elif reason_for_registration_string.find('Events') > -1:
            mail.send(
                [email_address],
                'kimberly.ryan@gmail.com',
                template='Welcome_Events',
            )
        else: 
            mail.send(
                [email_address],
                'kimberly.ryan@gmail.com',
                template='Welcome_Co-op',
            )

        return render_to_response('school/family/post_form_NewFamilyForm_success.html', context)


    return render(request, 'school/family/post_form_NewFamilyForm.html', { 'form': form,})

    

def EmailClassTeacher(request, schedule_id):
    sc = Schedule.objects.get(pk=schedule_id)
    sm = request.session.get('active_semester')
    form = EmailClassForm(request.POST or None)
    if form.is_valid():
        schedules = Schedule.objects.get(pk=schedule_id)
        a = [p.family_member.family.email_address for p in schedules.teacher.all()]
        recipients = list(set(a))

        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        sender = request.user.family.email_address
        text_content = strip_tags(message)
        a = send_simple_message(sender, recipients, subject, message) 
        return redirect('/school/thanks')

    return render(request, "school/schedule/email_teacher.html", { 'form': form, 'schedule_name': sc, })

def EmailClassAssistant(request, schedule_id):
    sc = Schedule.objects.get(pk=schedule_id)
    sm = request.session.get('active_semester')
    form = EmailClassForm(request.POST or None)
    if form.is_valid():
        schedules = Schedule.objects.get(pk=schedule_id)
        a = [p.assistant.family_member.family.email_address for p in schedules.get_assistant_list()]
        recipients = list(set(a))

        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        sender = request.user.family.email_address
        text_content = strip_tags(message)
        a = send_simple_message(sender, recipients, subject, message) 
        return redirect('/school/thanks')
    return render(request, "school/schedule/email_assistant.html", { 'form': form, 'schedule_name': sc, })


def EmailClass(request, schedule_id):
    sc = Schedule.objects.get(pk=schedule_id)
    sm = request.session.get('active_semester')
    form = EmailClassForm(request.POST or None)
    if form.is_valid():
        schedules = Schedule.objects.get(pk=schedule_id)
        a = [p.student.family_member.family.email_address for p in schedules.get_student_list()]
        a = a + [p.assistant.family_member.family.email_address for p in schedules.get_assistant_list()]
        a = a + [p.family_member.family.email_address for p in schedules.teacher.all()]
        recipients = list(set(a))

        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        #sender = "administrator@flchomegroup.com"
        sender = request.user.family.email_address
        text_content = strip_tags(message)
        a = send_simple_message(sender, recipients, subject, message) 
        return redirect('/school/thanks')

    return render(request, "school/schedule/email_class.html", { 'form': form, 'schedule_name': sc,})


class EventList(ListView):
    model = Event
    template_name = 'school/event/event_list.html'
    def get_queryset(self):
        qs =  Event.objects.filter(event_date__gte=datetime.today())
        return qs
   
class EventCreate(CreateView):
    model = Event
    fields = '__all__'
    template_name = 'school/event/event_form.html'
    success_url = reverse_lazy('event_list')

class EventUpdate(UpdateView):
    model = Event
    fields = '__all__'
    template_name = 'school/event/event_form.html'
    success_url = reverse_lazy('event_list')

class EventDelete(DeleteView):
    model = Event
    template_name = 'school/event/event_confirm_delete.html'
    success_url = reverse_lazy('event_list')

class EventAddEnrollment(CreateView):
    model = EventEnrollment
    template_name = 'school/event/event_enrollment.html'
    success_url = reverse_lazy('event_list')
    form_class = EventAddEnrollmentForm

    def get_initial(self):
        title = self.kwargs['pk']
        family = self.request.user.family.id
        return {
            'title':title,
            'family':family,
        }
 
class EventDeleteEnrollment(DeleteView):
    model = EventEnrollment
    template_name = 'school/event/event_confirm_delete_enrollment.html'
    success_url = reverse_lazy('event_list')

def EmailEvent(request, event_id):
    eid = Event.objects.get(pk=event_id)
    form = EmailEventForm(request.POST or None)
    if form.is_valid():
        event = Event.objects.get(pk=event_id)
        a = [p.family.email_address for p in event.get_enrolled()]
        recipients = list(set(a))

        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        #sender = "administrator@flchomegroup.com"
        sender = request.user.family.email_address
        text_content = strip_tags(message)
        a = send_simple_message(sender, recipients, subject, text_content) 
        return redirect('/school/thanks')

    return render(request, "school/event/email_event.html", { 'form': form, 'event_name': eid,})

@staff_member_required
def EmailGroup(request):
    form = EmailGroupForm(request.POST or None)
    if form.is_valid():

        selectedId = form.cleaned_data['name']
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        #sender = "administrator@flchomegroup.com"
        sender = request.user.family.email_address

        a = EmailList.objects.get(name=selectedId)
        #a = [p.email for p in emailusers.get_email_list()]
        recipients = a.alias + "@mg.flchomegroup.com"
        

        text_content = strip_tags(message + '\n\n\n' + a.footer )
        a = send_simple_message(sender, recipients, subject, text_content) 
        return redirect('/school/thanks')

    return render(request, "school/admin/email_group.html", { 'form': form,})

class CopyClassEnrollmentForm1(forms.Form):
    original_semester=forms.ModelChoiceField(queryset=Semester.objects.filter(is_active=True))
    new_semester=forms.ModelChoiceField(queryset=Semester.objects.filter(is_active=True))

class CopyClassEnrollmentForm2(forms.Form):
    original_class = forms.ModelChoiceField(queryset=Schedule.objects.filter(), empty_label=None)
    new_class = forms.ModelChoiceField(queryset=Schedule.objects.filter(), empty_label=None)
    
    def __init__(self, *args, **kwargs):
        original_semester = kwargs.pop('original_semester')
        new_semester = kwargs.pop('new_semester')
        super (CopyClassEnrollmentForm2,self).__init__(*args,**kwargs)
        self.fields['original_class'].queryset = Schedule.objects.filter(semester=original_semester)
        self.fields['new_class'].queryset = Schedule.objects.filter(semester=new_semester)

@staff_member_required
def copy_class_enrollment1(request):
    form = CopyClassEnrollmentForm1(request.POST)
    if request.method == 'POST' and form.is_valid():
        request.session['original_semester'] = form.cleaned_data['original_semester']
        request.session['new_semester'] = form.cleaned_data['new_semester']
        return HttpResponseRedirect(reverse('copy_class_enrollment2'))
        
    else:
        form = CopyClassEnrollmentForm1()

    return render(request, "school/admin/copy_class_enrollment1.html", { 'form': form,})

@staff_member_required
def copy_class_enrollment2(request):
    original_semester = request.session['original_semester']
    new_semester = request.session['new_semester']
    if request.method == 'POST':
        form = CopyClassEnrollmentForm2(request.POST, original_semester=original_semester, new_semester=new_semester)
        if form.is_valid():
            original_class = form.cleaned_data['original_class']
            new_class = form.cleaned_data['new_class']
            #new_class_id = Schedule.objects.get(course_catalog=new_class)
            original_students = StudentEnroll.objects.filter(schedule=original_class)
            StudentEnroll.objects.filter(schedule=new_class).delete()
            for a in original_students:
                a.pk=None
                a.schedule_id = new_class.id
                a.save()
            return redirect('/school/thanks')
    else:
        form = CopyClassEnrollmentForm2(original_semester=original_semester, new_semester=new_semester)

    return render(request, "school/admin/copy_class_enrollment2.html", { 'form': form,})


#def object_list(request, model):
    #obj_list = model.objects.all()
    #template_name = 'mysite/%s_list.html' % model.__name__.lower()
    #return render(request, template_name, {'object_list': obj_list})


@staff_member_required
def increment_grade(request):
    context = RequestContext(request)
    if request.method == 'POST':
        tconfirmation = request.POST['textConfirmation']
        if tconfirmation == "INCREMENT":
            a = Student.objects.all()
            with transaction.atomic():
                for eachStudent in a:
                    currentStudent = Student.objects.select_for_update().get(pk=eachStudent.id)
                    currentStudent.grade = eachStudent.get_next_grade
                    currentStudent.save()
            return redirect('/school/thanks')
            
    s_list = Student.objects.select_related()
    return render_to_response('school/admin/increment_grade.html', {
        's_list': s_list, }, context)


def GetAttendanceSheets(request, family_id=None, csv=None):

    context = RequestContext(request)

    if request.session.get('active_semester', False):
        if family_id:
            fn = family_id
        else:
            fn = request.user.family
        sm = request.session.get('active_semester')

        semester_dates = SemesterDates.objects.filter(semester=sm)
        schedule = Schedule.objects.filter(semester=sm).prefetch_related()
        schedule_list = schedule.values_list('course_catalog__course_name', \
            flat=True).order_by('semester_period__name')

        # Students
        student_dict=dict([(s,[]) for s in list(schedule_list)])
        student_enrolls = StudentEnroll.objects.filter(schedule__semester = sm).values_list( \
                'student__family_member__first_name', 'student__family_member__last_name', \
                'schedule__course_catalog__course_name').order_by('student__family_member__last_name')
        for (fname, lname, course) in student_enrolls:
            student_dict[course].append(fname + ' ' + lname)

        #Assistants
        assistants_dict=dict([(s,[]) for s in list(schedule_list)])
        assistants_enrolls = AssistantEnroll.objects.filter(schedule__semester = sm).values_list( \
                'assistant__family_member__first_name', 'assistant__family_member__last_name', \
                'schedule__course_catalog__course_name').order_by('assistant__family_member__last_name')
        for (fname, lname, course) in assistants_enrolls:
            assistants_dict[course].append(fname + ' ' + lname)

        #Teachers
        teachers_dict=dict([(s,[]) for s in list(schedule_list)])
        teachers_enrolls = Schedule.objects.filter(semester = sm).values_list( \
                'teacher__family_member__first_name', 'teacher__family_member__last_name', \
                'course_catalog__course_name')
        for (fname, lname, course) in teachers_enrolls:
            teachers_dict[course].append(fname + ' ' + lname)
        for k in teachers_dict.keys():
            teachers_dict[k].sort()


        if csv:
            htmlTemplate='school/schedule/attendance_sheets_report.csv'
            lCsvFile = render_to_string(htmlTemplate, {
                'semester_dates': semester_dates,
                'schedule': schedule,
                'student_dict': student_dict,
                'assistants_dict': assistants_dict,
                'teachers_dict': teachers_dict,
            })
            lResponse = HttpResponse(content_type="text/csv")
            lResponse['Content-Disposition'] = "attachment; filename=attendance_sheets_report.csv"
            lResponse.write(lCsvFile)
            return lResponse
        else:
            htmlTemplate='school/schedule/attendance_sheets_report.html'

        return render_to_response(htmlTemplate, {
            'semester_dates': semester_dates,
            'schedule': schedule,
            'student_dict': student_dict,
            'assistants_dict': assistants_dict,
            'teachers_dict': teachers_dict,
        }, context)

    else:
        return redirect('semester_information')

#def GetAttendanceSheets(request, family_id=None, csv=None):
#
#    context = RequestContext(request)
#
#    if request.session.get('active_semester', False):
#        if family_id:
#            fn = family_id
#        else:
#            fn = request.user.family
#        sm = request.session.get('active_semester')
#
#        semester_dates = SemesterDates.objects.filter(semester=sm)
#        schedule = Schedule.objects.filter(semester=sm)
#        student_enrolls = StudentEnroll.objects.filter(schedule__semester = sm).values_list('schedule__pk', 'student__family_member__first_name', 'student__family_member__last_name', 'student__grade', 'student__birth_date').order_by('student__family_member__last_name')
#        assistant_enrolls = AssistantEnroll.objects.filter(schedule__semester = sm).values_list('schedule__pk', 'assistant__family_member__first_name', 'assistant__family_member__last_name').order_by('assistant__family_member__last_name')
#        schedule_array={}
#        for a in schedule:
#           schedule_array[a.id]={'course':a.course_catalog.course_name, 'students': [], 'teachers': a.teacher.all(), 'assistants': [], 'grades': a.semester_grade.all(), 'period':a.semester_period, 'location':a.course_location} 
#
#       for (pk, fname, lname, grade, birth) in student_enrolls:
#           schedule_array[pk]['students'].append([fname + ' ' + lname, grade, birth])
#
#       for (pk, fname, lname) in assistant_enrolls:
#           schedule_array[pk]['assistants'].append(fname + ' ' + lname)
#
#    
#        if csv:
#            htmlTemplate='school/schedule/attendance_sheets_report.csv'
#            lCsvFile = render_to_string(htmlTemplate, {
#                'semester_dates': semester_dates,
#                'schedule': schedule,
#               'schedule_array': schedule_array,
#            })
#            lResponse = HttpResponse(content_type="text/csv")
#            lResponse['Content-Disposition'] = "attachment; filename=attendance_sheets_report.csv"
#            lResponse.write(lCsvFile)
#            return lResponse
#        else:
#            htmlTemplate='school/schedule/attendance_sheets_report.html'
#
#        return render_to_response(htmlTemplate, {
#            'semester_dates': semester_dates,
#            'schedule': schedule,
#           'schedule_array': schedule_array,
#        }, context)
#
#    else:
#        return redirect('semester_information')
#

@public
@csrf_exempt
def send_email(request):
    # TO DO
    #    Send email if the user is not authorized to send to list
    if request.method == 'POST':
        mail_data = request.FILES
        sender    = request.POST.get('sender')
        subject   = request.POST.get('subject', '')
        maillist, space, msubject = subject.partition(' ')
        new_recipient = "%s@mg.flchomegroup.com" % maillist
        #body_plain   = request.POST.get('stripped-text', 'i am not found')
        #body_plain   = request.POST.get('body-plain', 'i am not found')
        body_plain   = request.POST.get('body-html', 'Error: No text in message body. You must add a message.')
        body_html   = request.POST.get('body-html', ' ')

        mtest = validate_list(new_recipient)
        if mtest:
            mail = EmailMultiAlternatives(msubject, body_plain, sender, [new_recipient])
            for field, value in mail_data.items():
                mail.attach(value.name, value.read(), value.content_type)
            mail.content_subtype = "html"
            mail.attach_alternative(body_html, "text/html")
            mail.send()
        else:
            recipient = sender
            subject = "FAILED: " + msubject
            message = "Your message failed because " + new_recipient + " doesn't exist."
            a = send_simple_message("postmaster@mg.flchomegroup.com", recipient, subject, message) 
    else:
        subject = "kim_tes this    is     cool! Indeed"
        mlist, space, rest = subject.partition(' ')
        new_recipient = "%s@mg.flchomegroup.com" % mlist
        a = validate_list(new_recipient)
        if validate_list(new_recipient):
                return HttpResponse("GOOD")
        return HttpResponse(a)
        
    return HttpResponse('OK')

def contact_email(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            your_email = form.cleaned_data['your_email']
            message = form.cleaned_data['message']
            try:
                send_mail(subject, message, your_email, ['chris.ryan.12345@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('/school/thanks/')
    return render(request, "school/contact_email.html", {'form': form})

@csrf_exempt
@public
def checkusername(request):
    username = request.POST.get('username', False)
    showLogin = request.POST.get('showLogin', False)
    if showLogin:
        showLogin="<a href='http://play.flchomegroup.com/accounts/login/'>Sign in instead.</a>"
    else:
        showLogin=""
    if username:
        u = FamilyMember.objects.filter(username=username).count()
        if u != 0:
            res = "<span class='label label-danger'>User name exists</span>"
        else:
            res = "<span class='label label-success'>Available</span>"
    else:
        res = ""

    return HttpResponse('%s' % res)

