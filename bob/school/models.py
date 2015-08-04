from school.mailgun import *
from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import  AbstractUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db.models import F, Sum
from django.core.exceptions import ObjectDoesNotExist, ValidationError, NON_FIELD_ERRORS
import select2.fields
import select2.models

# Create your models here.

class SemesterGrade(models.Model):
    name = models.CharField(max_length=50)
    next_grade = models.ForeignKey('SemesterGrade',blank=True, null=True)
    order = models.IntegerField()

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Semester: Grades'
    
    def __unicode__(self):
        return self.name

class CourseLocation(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Course: Locations'

    def __unicode__(self):
        return self.name

class CourseType(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Course: Types'

    def __unicode__(self):
        return self.name

class PersonContactDataType(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name_plural = 'People: Contact Data Types'

    def __unicode__(self):
        return self.name

class FamilyBenefits(models.Model):
    role = models.CharField(verbose_name='Family Role', max_length=25 )
    enrollment_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['role']
        verbose_name_plural = 'Family Role/Benefits'
    
    def __unicode__(self):
        return self.role

   
class Family(models.Model):
    name = models.CharField(verbose_name="Family name", max_length=200)
    address1 = models.CharField(verbose_name="Address", max_length=200)
    address2 = models.CharField(verbose_name="Address", max_length=200, blank=True)
    city = models.CharField(verbose_name="City", max_length=20)
    state = models.CharField(verbose_name="State", max_length=2)
    zip_code = models.CharField(verbose_name="Zip code", max_length=10)
    is_active = models.BooleanField(verbose_name="Active")
    family_workflow = models.ManyToManyField('FamilyWorkflow', verbose_name="Workflow", blank=True, null=True)
    family_benefits = models.ForeignKey(FamilyBenefits, verbose_name='Role/Benefits', null=True, blank=True)
    notes = models.TextField(blank=True)
    email_address = models.EmailField(verbose_name="Main email address", blank=True, unique=True)
    phone_number = models.CharField(verbose_name="Main phone number", max_length=20, blank=True)
    cell_phone_number = models.CharField(verbose_name="Cell phone number", max_length=20)
    emergency_name = models.CharField(verbose_name="Emergency Contact", max_length=50, blank=True)
    emergency_phone_number = models.CharField(verbose_name="Emergency phone number", max_length=20, blank=True)
    emergency_notes = models.TextField(blank=True)



    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Family Record'

    def __unicode__(self):
        return self.name


class FamilyWorkflow(models.Model):
    name = models.CharField(max_length=50, default='Name')
    description = models.TextField(blank=True)
    order = models.IntegerField()

    class Meta:
        verbose_name_plural = 'Family: Workflow'
        ordering = ['order']


    def __unicode__(self):
        return u'%s' %  (self.name)


class Semester(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(verbose_name="Active")

    class Meta:
        verbose_name_plural = 'Semester: Semester List'

    def __unicode__(self):
        return self.name

class SemesterDates(models.Model):
    semester = models.ForeignKey(Semester)
    class_date = models.DateField()

    class Meta:
        verbose_name_plural = 'Semester: Class Dates'

    def __unicode__(self):
        return u'%s (%s)' %  (self.class_date, self.semester)


class SemesterPeriod(models.Model):
    name = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()
    period_number = models.IntegerField()
    semester = models.ForeignKey(Semester)

    class Meta:
        ordering = ['semester', 'period_number']
        verbose_name_plural = 'Semester: Period List'

    def __unicode__(self):
        return u'%s (%s)' %  (self.name, self.semester)


class PersonGrade(models.Model):
    name = models.CharField(verbose_name='Grade name/number:', max_length=25)
    next_grade = models.ForeignKey('PersonGrade')
    order = models.IntegerField()

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'People: Grade List'
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('grade-detail', kwargs={'pk': self.pk})


class FamilyMemberRole(models.Model):
    role = models.CharField(max_length=20)
    is_household_head = models.BooleanField(verbose_name='Considered a parent role')

    def  __unicode__(self):
        return self.role

class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = CustomUserManager.normalize_email(email)
        user = self.model(email=email,
                          is_staff=False, is_active=True, is_superuser=False,
                          last_login=now, date_joined=now, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, family=None, **extra_fields):
        if not family:
            if Family.objects.filter(name='Not Assigned').exists():
                family=Family.objects.get(name='Not Assigned')
            else: 
                family= Family(
                   name="Not Assigned",
                   address1="...",
                   city="...",
                   state="..",
                   zip_code="....."
                )
                family.save()

        u = self.create_user(email, password, **extra_fields)
        u.family = family
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u


class FamilyMember(AbstractUser):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    family = select2.fields.ForeignKey(Family, blank=True, null=True, js_options={'width':10})
    middle_name = models.CharField(verbose_name='Middle name', max_length=50, blank=True)
    family_member_role = models.ForeignKey(FamilyMemberRole, blank=True, null=True)
    address1 = models.CharField(verbose_name="Address", max_length=200, blank=True)
    address2 = models.CharField(verbose_name="Address", max_length=200, blank=True)
    city =  models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zip_code = models.CharField(max_length=9, blank=True)
    notes = models.TextField(blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone_number = models.CharField(verbose_name="Main phone number", max_length=20, blank=True)
    cell_phone_number = models.CharField(verbose_name="Cell phone number", max_length=20, blank=True)
    email_list = models.ManyToManyField('EmailList', verbose_name="Email Lists", blank=True, null=True)
   

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    objects = CustomUserManager()

    class Meta:
        ordering = ['family', 'last_name', 'first_name']
        verbose_name_plural = 'Family Member Records'

    def __unicode__(self):
        return u'%s %s (%s)' %  (self.first_name, self.last_name, self.family)

    def _get_full_name(self):
        "Returns the person's full name."
        return '%s %s' % (self.first_name, self.last_name)
    full_name = property(_get_full_name) 

class Teacher(models.Model):
    family_member = models.OneToOneField(FamilyMember, verbose_name='name')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['family_member']
        verbose_name_plural = 'People: Teachers'

    def __unicode__(self):
        return u'%s' %  (self.family_member)


class Assistant(models.Model):
    family_member = models.OneToOneField(FamilyMember, verbose_name='name')
    notes = models.TextField(blank=True)
    schedule = models.ManyToManyField('Schedule', through='AssistantEnroll')


    class Meta:
        verbose_name_plural = 'People: Assistant'

    def __unicode__(self):
        return u'%s' %  (self.family_member)


class StudentType(models.Model):
    type = models.CharField(verbose_name='Student Type', max_length=25)

    class Meta:
        ordering = ['type']
        verbose_name_plural = 'People: Student Types'
    
    def __unicode__(self):
        return self.type


class Student(models.Model):
    family_member =models.OneToOneField(FamilyMember, verbose_name='name')
    grade = models.ForeignKey(PersonGrade, blank=True, verbose_name='Grade', null=True)
    type = models.ForeignKey(StudentType, verbose_name='Type', blank=True, null=True, default=2)
    food_allergies = models.TextField(blank=True, verbose_name='Allergies')
    birth_date = models.DateField(verbose_name='Birth date',blank=True, null=True)
    notes = models.TextField(blank=True)
    emergency_name = models.CharField(verbose_name="Emergency Contact", max_length=50, blank=True)
    emergency_phone_number = models.CharField(verbose_name="Emergency phone number", max_length=20, blank=True)
    emergency_notes = models.TextField(blank=True)
    schedule = models.ManyToManyField('Schedule', through='StudentEnroll')

    def age(self):
        import datetime
        if self.birth_date > datetime.date.today().replace(year = self.birth_date.year):
            return datetime.date.today().year - self.birth_date.year - 1
        else:
            return datetime.date.today().year - self.birth_date.year

    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'People: Students'
        ordering = ['family_member']

    def __unicode__(self):
        return u'%s' %  (self.family_member)

    def get_parent_list(self):
        return FamilyMember.objects.filter(family = self.family_member.family, family_member_role__is_household_head=True)

    @property
    def get_next_grade(self):
        p = PersonGrade.objects.get(name = self.grade)
        return p.next_grade

class PersonPhone(models.Model):
    extension = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=20)
    family_member = models.OneToOneField(FamilyMember)
    person_contact_data_type = models.ForeignKey(PersonContactDataType)

    class Meta:
        verbose_name_plural = 'People: Phone Numbers'

class FamilyMemberEmail(models.Model):
    email_address = models.EmailField()
    family_member = models.OneToOneField(FamilyMember)
    person_contact_data_type = models.ForeignKey(PersonContactDataType)

    class Meta:
        verbose_name_plural = 'People: Email Addresses' 

class CourseCatalog(models.Model):
    course_name = models.CharField(verbose_name="Course name", max_length=50)
    course_desc = models.TextField(verbose_name="Course Description")
    teacher = models.ForeignKey(Teacher, blank=True, null=True, verbose_name='Course Owner', on_delete=models.PROTECT)
    course_min_size = models.IntegerField(verbose_name="Min Class Size", default=3)
    course_max_size = models.IntegerField(verbose_name="Max Class Size", default=20)
    needs_course_room = models.TextField(verbose_name="Classroom Resources Required", blank=True)
    needs_student = models.TextField(verbose_name="Student Resources Required", blank=True)
    preferred_assistants = models.IntegerField(verbose_name="Number of Assistants Required", default=1)
    setup_time = models.IntegerField(verbose_name="Setup minutes required before", default=5)
    cleanup_time = models.IntegerField(verbose_name="Teardown minutes required after class", default=5)
    private_notes = models.TextField(blank=True)
    course_type = models.ForeignKey(CourseType, verbose_name="Course Type")
    fee_course = models.CharField(max_length="10", blank="True", verbose_name="Course Fee", default="$0.00")
    fee_material = models.CharField(max_length="10", blank="True", verbose_name="Material Fee", default="$0.00")
    semester_grade = models.ManyToManyField(SemesterGrade, verbose_name="Grades")

    class Meta:
        verbose_name_plural = 'Course: Course Catalog'
        permissions = (('view_coursecatalog', 'Can view course catalog'),)
        ordering = ['course_name']

    def __unicode__(self):
        return self.course_name

    def get_absolute_url(self):
        return reverse('coursecatalog_detail', kwargs={'pk': self.id})
    
    def get_update_url(self):
        return reverse('coursecatalog_update', kwargs={'pk': self.id})
    
    def get_delete_url(self):
        return reverse('coursecatalog_delete', kwargs={'pk': self.id})


class StudentEnroll(models.Model):
    schedule = select2.fields.ForeignKey('Schedule', js_options={'width':10})
    student = select2.fields.ForeignKey('Student', js_options={'width':10})

    class Meta:
        verbose_name_plural = 'Schedule: Student Enrollment' 
        ordering = ['student', 'schedule']

    def __unicode__(self):
        return u'%s' %  (self.student)

    #def validate_unique(self, exclude=None):
        #""" Verifies Enrollment uniqueness (may raise ValidationError).
            #The Exceptions generated here are caught and rendered by Django admin and ModelForms. """
        #if self.student:
            #enrollments = Schedule.objects.filter(student=self.student)
            #for enrollment in enrollments: # When Enrollment exists, verify same object as being edited:
                #if enrollment.pk != self.pk:
                    #error_msg = 'Existing Enrollment'
                    #raise ValidationError({NON_FIELD_ERRORS: [error_msg]})
        #super(StudentEnroll, self).validate_unique()
    
    def course_semester_info(self):
        return ("%s" % (self.schedule.semester))

    def course_period_info(self):
        return ("%s" % (self.schedule.semester_period))


class AssistantEnroll(models.Model):
    schedule = select2.fields.ForeignKey('Schedule', js_options={'width':20})
    assistant = select2.fields.ForeignKey('Assistant', js_options={'width':20})


    class Meta:
        verbose_name_plural = 'Schedule: Assistant Enrollment'
        ordering = ['assistant', 'schedule']

    def __unicode__(self):
        return u'%s' %  (self.assistant)

    #def validate_unique(self, exclude=None):
     #   """ Verifies Enrollment uniqueness (may raise ValidationError).
     #       The Exceptions generated here are caught and rendered by Django admin and ModelForms. """
     #   if self.assistant:
     #       #enrollments = Schedule.objects.filter(assistant=self.assistant, semester=self.semester, semester_period=self.semester_period)
     #       enrollments = Schedule.objects.filter(assistant=self.assistant, schedule__semester=sm, schedule__semester_period=sp)
     #       for enrollment in enrollments: # When Enrollment exists, verify same object as being edited:
     #           if enrollment.pk != self.pk:
     #               error_msg = 'Existing Enrollment'
     #               raise ValidationError({NON_FIELD_ERRORS: [error_msg]})
     #   super(AssistantEnroll, self).validate_unique()

    def course_semester_info(self):
        return ("%s" % (self.schedule.semester))

    def course_period_info(self):
        return ("%s" % (self.schedule.semester_period))

class ScheduleStudentManager(models.Manager):
    def get_query_set(self,si):
        return super(ScheduleStudentManager, self).get_query_set().filter(schedule_id=self.semester_id)
        
class Schedule(models.Model):
    semester = select2.fields.ForeignKey(Semester, verbose_name='Semester', js_options={'width':10})
    course_location = select2.fields.ForeignKey(CourseLocation, verbose_name='Location', js_options={'width':10})
    course_catalog = select2.fields.ForeignKey(CourseCatalog, verbose_name='Course', on_delete=models.PROTECT, js_options={'width':10})
    teacher = models.ManyToManyField(Teacher, verbose_name='Teacher')
    semester_period = models.ForeignKey(SemesterPeriod, verbose_name='Semester Period')
    semester_grade = models.ManyToManyField(SemesterGrade, verbose_name='Grades')
    order = models.IntegerField(verbose_name='Display Order', blank=True, null=True)

    objects = models.Manager()
    student_objects = ScheduleStudentManager()

    class Meta:
        verbose_name_plural = 'Schedule: Master Schedule' 
        ordering = ['semester', 'semester_period', 'order' ]

    def __unicode__(self):
        return u'%s (%s)' %  (self.course_catalog, self.semester_period)

    def get_num_students(self):
        return StudentEnroll.objects.filter(schedule = self.id).count()

    def get_num_assistants(self):
        return AssistantEnroll.objects.filter(schedule = self.id).count()

    def get_assistant_list(self):
        return AssistantEnroll.objects.filter(schedule = self.id)

    def get_student_list(self):
        return StudentEnroll.objects.filter(schedule = self.id)

    def get_enrolled_family_student_ids(self, family_student_list, semester):
        result = []
        family_student_ids = [i.id for i in family_student_list]
        student_enrolls = StudentEnroll.objects.filter(
            student_id__in=family_student_ids,
            schedule=self,
            schedule__semester=semester,
            schedule__semester_period=self.semester_period
        )
        for enroll in student_enrolls:
            result.append(enroll.student.id)

        return result

    def get_enrolled_family_assistant_ids(self, family_assistant_list, semester):
        result = []
        family_assistant_ids = [i.id for i in family_assistant_list]
        assistant_enrolls = AssistantEnroll.objects.filter(
            assistant_id__in=family_assistant_ids,
            schedule=self,
            schedule__semester=semester,
            schedule__semester_period=self.semester_period
        )
        for enroll in assistant_enrolls:
            result.append(enroll.assistant.id)

        return result


class EventFeePer(models.Model):
    fee_per = models.CharField(max_length=25 )

    class Meta:
        ordering = ['fee_per']
        verbose_name_plural = 'Events: Fee Per'
    
    def __unicode__(self):
        return self.fee_per
  

class Event(models.Model):
    title = models.CharField(max_length=255, verbose_name="Title of Event")
    description = models.TextField()
    family = select2.fields.ForeignKey(Family, blank=True, null=True, js_options={'width':10}, verbose_name="Host Family")
    event_max_size = models.IntegerField(verbose_name="Limit", default=20)
    fee_event = models.CharField(max_length=20, verbose_name="Cost for Event") 
    fee_per = models.ForeignKey(EventFeePer, blank=True, null=True, verbose_name="Cost Per ____")
    event_date = models.DateField(blank=True, null=True, verbose_name="Date (MM/DD/YYYY)")
    event_time = models.TimeField(blank=True, null=True, verbose_name="Time (HH:MM AM|PM)")
    event_registration_date = models.DateField(blank=True, null=True, verbose_name="Registration Ends (MM/DD/YYYY)")
    is_cancelled = models.BooleanField(verbose_name="Cancelled")
    
    class Meta:
        ordering = ['event_date']
        verbose_name_plural = 'Events'
    def __unicode__(self):
        return u"%s" % self.title
    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'pk': self.pk})
    def get_enrolled(self):
        return self.eventenrollment_set.select_related('eventenrollment').order_by('family')
    def get_num_children(self):
        return self.eventenrollment_set.select_related('eventenrollment').aggregate(num_children=Sum('count_child'))
    def get_num_adults(self):
        return self.eventenrollment_set.select_related('eventenrollment').aggregate(num_adults=Sum('count_adult'))
    def get_num_total(self):
        a=self.eventenrollment_set.select_related('eventenrollment').aggregate(num_adults=Sum('count_adult')).values()[0]
        c=self.eventenrollment_set.select_related('eventenrollment').aggregate(num_children=Sum('count_child')).values()[0]
        ttl=a+c
        if self.event_max_size <= ttl:
            return True
        return False

class EventEnrollment(models.Model):
    title = select2.fields.ForeignKey(Event)
    family = select2.fields.ForeignKey(Family)
    count_adult = models.IntegerField(verbose_name="Adults", default=0)
    count_child = models.IntegerField(verbose_name="Children", default=0)
    notes = models.TextField(blank=True)
    is_paid = models.BooleanField(verbose_name="Paid")
    
    class Meta:
        verbose_name_plural = 'Events: Enrollment'

    def __unicode__(self):
        return u'%s (%s)' %  (self.title, self.family)

class EmailListQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(is_active=True)
    def managed_by_user(self):
        return self.filter(is_managed_by_user=True)
    def managed_by_admin(self):
        return self.filter(is_managed_by_user=False)

class EmailListManager(models.Manager):
    def get_queryset(self):
        return EmailListQuerySet(self.model, using=self._db)
    def get_admin(self):
        return self.get_queryset().active().managed_by_admin()
    def get_user(self):
        return self.get_queryset().active().managed_by_user()

class EmailList(models.Model):
    alias = models.CharField(max_length=10, default='mylist', verbose_name="Email (I will add @mg.flchomegroup.com)")
    name = models.CharField(max_length=50, default='My List', verbose_name="Display Name")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(verbose_name="Active")
    is_managed_by_user = models.BooleanField(verbose_name="User Managed")

    objects = EmailListManager()

    class Meta:
        verbose_name_plural = 'Email: Lists'

    def __unicode__(self):
        return u'%s' %  (self.name)

    
#Testing Email Templates
#class EmailTemplates(models.Model):
    #name = models.CharField(max_length=50, verbose_name="Email Template Name")
    #description = models.CharField(max_length=255, verbose_name="Description of template")
    #subject = models.CharField(max_length=255, verbose_name="Subject of email")
    #email_body = models.TextField(verbose_name="Body of email")

    #class Meta:
        #verbose_name_plural = 'Email: Templates'

    #def __unicode__(self):
    #    return u'%s' %  (self.name)





FamilyMember._meta.get_field('email')._unique = True
