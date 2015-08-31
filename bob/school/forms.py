from django import forms
from django.forms import ModelForm
from school.models import CourseCatalog, CourseType, SemesterGrade, Schedule, StudentEnroll, Family, FamilyMember, Event, EventEnrollment, EmailList

class CourseCatalogForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
	super(CourseCatalogForm, self).__init__(*args, **kwargs)
	#self.fields['course_name'].widget.attrs['class'] = "form-control"
	#self.fields['course_desc'].widget.attrs['class'] = "form-control"
	self.fields['teacher'].widget.attrs['class'] = "form-control"
	self.fields['course_type'].widget.attrs['class'] = "form-control"
	self.fields['semester_grade'].widget.attrs['class'] = "form-control"
	#self.fields['needs_course_room'].widget.attrs['class'] = "form-control"
	#self.fields['needs_student'].widget.attrs['class'] = "form-control"
        self.fields['teacher'].queryset = self.fields['teacher'].queryset.select_related('family_member')
    class Meta:
    	model=CourseCatalog
	fields = [ 'course_name', 'course_desc',  'teacher', 'course_min_size', 'course_max_size', 'needs_course_room', 'needs_student', 'preferred_assistants', 'setup_time', 'cleanup_time',  'course_type', 'fee_course', 'fee_material', 'semester_grade'] 

class SemesterForm(forms.ModelForm):
    class Meta:
	model=Schedule
	fields = [ 'semester' ]

class EmailClassForm(forms.Form):
    subject = forms.CharField(max_length=100, widget=forms.Textarea(attrs={'class':'field span12', 'rows': 1}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class':'field span12', 'rows': 20}))

class EmailEventForm(forms.Form):
    subject = forms.CharField(max_length=100, widget=forms.Textarea(attrs={'class':'field span12', 'rows': 1}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class':'field span12', 'rows': 20}))

class NewFamilyForm(forms.Form):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    first_name = forms.CharField(max_length=200)
    last_name = forms.CharField(max_length=200)
    password = forms.CharField(widget=forms.PasswordInput())
    address1 = forms.CharField( max_length=200)
    address2 = forms.CharField(max_length=200, required=False)
    city = forms.CharField(max_length=20)
    state = forms.CharField(max_length=2)
    zip_code = forms.CharField(max_length=10)
    email_address = forms.EmailField()
    phone_number = forms.CharField(max_length=20, required=False)
    cell_phone_number = forms.CharField(max_length=20)
    gender = forms.ChoiceField(GENDER_CHOICES)
    # The following are only used for the email that is sent out.
    REGISTRATION_CHOICES = (
	('co-op', 'co-op'),
	('High School or Professional Classes', 'High School/Professional Classes'),
	('Events', 'Events'),
    )
    reason_for_registration = forms.MultipleChoiceField(required=False,
        widget=forms.CheckboxSelectMultiple, choices=REGISTRATION_CHOICES)



class NewFamilyMemberForm(forms.ModelForm):
    class Meta:
	model = FamilyMember
	fields = ('first_name','last_name','phone_number', 'cell_phone_number','gender')

class EventForm(forms.ModelForm):
    class Meta:
	model = Event
	fields = ('title', 'description', 'family', 'event_max_size', )

class EventEnrollmentForm(forms.ModelForm):
    class Meta:
	model = EventEnrollment
        fields = '__all__'

class EventAddEnrollmentForm(forms.ModelForm):
    class Meta:
	model = EventEnrollment
        fields = '__all__'

class EmailGroupForm(forms.Form):
    name = forms.ModelChoiceField(queryset=EmailList.objects.filter(is_active=True),empty_label=None)
    subject = forms.CharField(max_length=100, widget=forms.Textarea(attrs={'class':'field span12', 'rows': 1}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class':'field span12', 'rows': 20}))

class ContactForm(forms.Form):
    your_email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea)
