from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext, ugettext_lazy as _

from models import *
admin.site.register(CourseLocation)
admin.site.register(CourseType)
admin.site.register(StudentType)
admin.site.register(FamilyMemberRole)
admin.site.register(FamilyBenefits)
admin.site.register(FamilyWorkflow)
# Testing Email Templates
#admin.site.register(EmailTemplates)


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'duplicate_username': _("A user with that username already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }
    username = forms.RegexField(label=_("Username"), max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = FamilyMember
        fields = ('username',)

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            FamilyMember._default_manager.get(username=username)
        except FamilyMember.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    username = forms.RegexField(
        label=_("Username"), max_length=30, regex=r"^[\w.@+-]+$",
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    password = ReadOnlyPasswordHashField(label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>."))

    class Meta:
        model = FamilyMember
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class FamilyMemberAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('family', 'first_name', 'middle_name', 'last_name', 'family_member_role', 'gender')}),
        (_('Contact info (if different from the main family record)'), {'fields': ('address1', 'address2', 'city', 'state', 'zip_code', 'email', 'email_list')}),
    	(_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2' )}
        ),
    )

    UserAdmin.list_display = ('family', 'first_name', 'last_name', 'username', 'is_staff', 'date_joined', 'is_active',  'family_member_role',)

    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

class STAAdminForm(forms.ModelForm):
    class Meta:
	model = Teacher
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(STAAdminForm, self).__init__(*args, **kwargs)
	self.fields['family_member'].queryset = FamilyMember.objects.order_by('last_name', 'first_name')


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('family_member', 'notes',)
    form = STAAdminForm
    search_fields = ('family_member__first_name', 'family_member__last_name')

class AssistantAdmin(admin.ModelAdmin):
    list_display = ('family_member', 'notes',)
    form = STAAdminForm
    search_fields = ('family_member__first_name', 'family_member__last_name')

class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'family_member', 'grade', 'type', 'notes',)
    form = STAAdminForm
    search_fields = ('family_member__first_name', 'family_member__last_name')

class SemesterPeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'semester', 'start_time', 'end_time',)
    list_filter = ('semester',)

class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active',)
    list_filter = ('name',)

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('course_catalog', 'semester', 'semester_period', 'course_location', 'order',)
    list_filter = ('semester',)

class SemesterDatesAdmin(admin.ModelAdmin):
    list_display = ('semester', 'class_date',)
    list_filter = ('semester',)

class CourseCatalogAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'teacher', 'course_type', 'preferred_assistants', 'course_max_size', 'id', )
    search_fields = ('course_name',)

class AssistantEnrollAdmin(admin.ModelAdmin):
    list_display = ('assistant', 'schedule', 'course_semester_info', 'course_period_info',)
    list_filter = ('schedule__semester',)
    search_fields = ('assistant__family_member__first_name', 'assistant__family_member__last_name')

class StudentEnrollAdmin(admin.ModelAdmin):
    list_display = ('student','schedule', 'course_semester_info', 'course_period_info',)
    list_filter = ('schedule__semester',)
    search_fields = ('student__family_member__first_name', 'student__family_member__last_name')

class FamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'address1', 'phone_number', 'is_active', 'email_address', 'family_benefits',)
    search_fields = ('name', 'email_address')

class PersonGradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'next_grade',)

class SemesterGradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'next_grade',)

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_cancelled', 'event_max_size', 'event_date', )
    search_fields = ('title',)

class EventEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'family', 'count_adult', 'count_child',)

class EmailListAdmin(admin.ModelAdmin):
    list_display = ('name', 'alias', 'is_active','is_managed_by_user',)


	
# Now register the new UserAdmin...
admin.site.register(SemesterGrade, SemesterGradeAdmin)
admin.site.register(PersonGrade, PersonGradeAdmin)
admin.site.register(FamilyMember, FamilyMemberAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Assistant, AssistantAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(CourseCatalog, CourseCatalogAdmin)
admin.site.register(StudentEnroll, StudentEnrollAdmin)
admin.site.register(AssistantEnroll, AssistantEnrollAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Family, FamilyAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(EventFeePer)
admin.site.register(EventEnrollment, EventEnrollmentAdmin)
admin.site.register(EmailList, EmailListAdmin)
admin.site.register(SemesterPeriod, SemesterPeriodAdmin)
admin.site.register(SemesterDates, SemesterDatesAdmin)
admin.site.register(Semester, SemesterAdmin)
