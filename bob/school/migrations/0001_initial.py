# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import select2.fields
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='FamilyMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, verbose_name='username')),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(unique=True, max_length=254, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('middle_name', models.CharField(max_length=50, verbose_name=b'Middle name', blank=True)),
                ('address1', models.CharField(max_length=200, verbose_name=b'Address', blank=True)),
                ('address2', models.CharField(max_length=200, verbose_name=b'Address', blank=True)),
                ('city', models.CharField(max_length=255, blank=True)),
                ('state', models.CharField(max_length=2, blank=True)),
                ('zip_code', models.CharField(max_length=9, blank=True)),
                ('notes', models.TextField(blank=True)),
                ('gender', models.CharField(max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female')])),
                ('phone_number', models.CharField(max_length=20, verbose_name=b'Main phone number', blank=True)),
                ('cell_phone_number', models.CharField(max_length=20, verbose_name=b'Cell phone number', blank=True)),
            ],
            options={
                'ordering': ['family', 'last_name', 'first_name'],
                'verbose_name_plural': 'Family Member Records',
            },
        ),
        migrations.CreateModel(
            name='Assistant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('notes', models.TextField(blank=True)),
                ('family_member', models.OneToOneField(verbose_name=b'name', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'People: Assistant',
            },
        ),
        migrations.CreateModel(
            name='AssistantEnroll',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('assistant', select2.fields.ForeignKey(to='school.Assistant')),
            ],
            options={
                'ordering': ['assistant', 'schedule'],
                'verbose_name_plural': 'Schedule: Assistant Enrollment',
            },
        ),
        migrations.CreateModel(
            name='CourseCatalog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_name', models.CharField(max_length=50, verbose_name=b'Course name')),
                ('course_desc', models.TextField(default=b'Add description', verbose_name=b'Course Description')),
                ('course_min_size', models.IntegerField(default=3, verbose_name=b'Min Class Size')),
                ('course_max_size', models.IntegerField(default=20, verbose_name=b'Max Class Size')),
                ('needs_course_room', models.TextField(verbose_name=b'Classroom Resources Required', blank=True)),
                ('needs_student', models.TextField(verbose_name=b'Student Resources Required', blank=True)),
                ('preferred_assistants', models.IntegerField(default=1, verbose_name=b'Number of Assistants Required')),
                ('setup_time', models.IntegerField(default=5, verbose_name=b'Setup minutes required before')),
                ('cleanup_time', models.IntegerField(default=5, verbose_name=b'Teardown minutes required after class')),
                ('private_notes', models.TextField(blank=True)),
                ('fee_course', models.CharField(default=b'$0.00', max_length=b'10', verbose_name=b'Course Fee', blank=b'True')),
                ('fee_material', models.CharField(default=b'$0.00', max_length=b'10', verbose_name=b'Material Fee', blank=b'True')),
            ],
            options={
                'ordering': ['course_name'],
                'verbose_name_plural': 'Course: Course Catalog',
                'permissions': (('view_coursecatalog', 'Can view course catalog'),),
            },
        ),
        migrations.CreateModel(
            name='CourseLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'Course: Locations',
            },
        ),
        migrations.CreateModel(
            name='CourseType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'Course: Types',
            },
        ),
        migrations.CreateModel(
            name='EmailList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alias', models.CharField(default=b'mylist', max_length=10, verbose_name=b'Email (I will add @mg.flchomegroup.com)')),
                ('name', models.CharField(default=b'My List', max_length=50, verbose_name=b'Display Name')),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(verbose_name=b'Active')),
                ('is_managed_by_user', models.BooleanField(verbose_name=b'User Managed')),
            ],
            options={
                'verbose_name_plural': 'Email: Lists',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name=b'Title of Event')),
                ('description', models.TextField()),
                ('event_max_size', models.IntegerField(default=20, verbose_name=b'Limit')),
                ('fee_event', models.CharField(max_length=20, verbose_name=b'Cost for Event')),
                ('event_date', models.DateField(null=True, verbose_name=b'Date (MM/DD/YYYY)', blank=True)),
                ('event_time', models.TimeField(null=True, verbose_name=b'Time (HH:MM AM|PM)', blank=True)),
                ('event_registration_date', models.DateField(null=True, verbose_name=b'Registration Ends (MM/DD/YYYY)', blank=True)),
                ('is_cancelled', models.BooleanField(verbose_name=b'Cancelled')),
            ],
            options={
                'ordering': ['event_date'],
                'verbose_name_plural': 'Events',
            },
        ),
        migrations.CreateModel(
            name='EventEnrollment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count_adult', models.IntegerField(default=0, verbose_name=b'Adults')),
                ('count_child', models.IntegerField(default=0, verbose_name=b'Children')),
                ('notes', models.TextField(blank=True)),
                ('is_paid', models.BooleanField(verbose_name=b'Paid')),
            ],
            options={
                'verbose_name_plural': 'Events: Enrollment',
            },
        ),
        migrations.CreateModel(
            name='EventFeePer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fee_per', models.CharField(max_length=25)),
            ],
            options={
                'ordering': ['fee_per'],
                'verbose_name_plural': 'Events: Fee Per',
            },
        ),
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name=b'Family name')),
                ('address1', models.CharField(max_length=200, verbose_name=b'Address')),
                ('address2', models.CharField(max_length=200, verbose_name=b'Address', blank=True)),
                ('city', models.CharField(max_length=20, verbose_name=b'City')),
                ('state', models.CharField(max_length=2, verbose_name=b'State')),
                ('zip_code', models.CharField(max_length=10, verbose_name=b'Zip code')),
                ('is_active', models.BooleanField(verbose_name=b'Active')),
                ('notes', models.TextField(blank=True)),
                ('email_address', models.EmailField(unique=True, max_length=254, verbose_name=b'Main email address', blank=True)),
                ('phone_number', models.CharField(max_length=20, verbose_name=b'Main phone number', blank=True)),
                ('cell_phone_number', models.CharField(max_length=20, verbose_name=b'Cell phone number')),
                ('emergency_name', models.CharField(max_length=50, verbose_name=b'Emergency Contact', blank=True)),
                ('emergency_phone_number', models.CharField(max_length=20, verbose_name=b'Emergency phone number', blank=True)),
                ('emergency_notes', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'Family Record',
            },
        ),
        migrations.CreateModel(
            name='FamilyBenefits',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(max_length=25, verbose_name=b'Family Role')),
                ('enrollment_date', models.DateField(null=True, blank=True)),
            ],
            options={
                'ordering': ['role'],
                'verbose_name_plural': 'Family Role/Benefits',
            },
        ),
        migrations.CreateModel(
            name='FamilyMemberEmail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email_address', models.EmailField(max_length=254)),
                ('family_member', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'People: Email Addresses',
            },
        ),
        migrations.CreateModel(
            name='FamilyMemberRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(max_length=20)),
                ('is_household_head', models.BooleanField(verbose_name=b'Considered a parent role')),
            ],
        ),
        migrations.CreateModel(
            name='FamilyWorkflow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'Name', max_length=50)),
                ('description', models.TextField(blank=True)),
                ('order', models.IntegerField()),
            ],
            options={
                'ordering': ['order'],
                'verbose_name_plural': 'Family: Workflow',
            },
        ),
        migrations.CreateModel(
            name='PersonContactDataType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name_plural': 'People: Contact Data Types',
            },
        ),
        migrations.CreateModel(
            name='PersonGrade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=25, verbose_name=b'Grade name/number:')),
                ('order', models.IntegerField()),
                ('next_grade', models.ForeignKey(to='school.PersonGrade')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'People: Grade List',
            },
        ),
        migrations.CreateModel(
            name='PersonPhone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('extension', models.CharField(max_length=10)),
                ('phone_number', models.CharField(max_length=20)),
                ('family_member', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
                ('person_contact_data_type', models.ForeignKey(to='school.PersonContactDataType')),
            ],
            options={
                'verbose_name_plural': 'People: Phone Numbers',
            },
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(null=True, verbose_name=b'Display Order', blank=True)),
                ('course_catalog', select2.fields.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name=b'Course', to='school.CourseCatalog')),
                ('course_location', select2.fields.ForeignKey(verbose_name=b'Location', to='school.CourseLocation')),
            ],
            options={
                'ordering': ['semester', 'semester_period', 'order'],
                'verbose_name_plural': 'Schedule: Master Schedule',
            },
        ),
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('is_active', models.BooleanField(verbose_name=b'Active')),
            ],
            options={
                'verbose_name_plural': 'Semester: Semester List',
            },
        ),
        migrations.CreateModel(
            name='SemesterDates',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('class_date', models.DateField()),
                ('semester', models.ForeignKey(to='school.Semester')),
            ],
            options={
                'verbose_name_plural': 'Semester: Class Dates',
            },
        ),
        migrations.CreateModel(
            name='SemesterGrade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('order', models.IntegerField()),
                ('next_grade', models.ForeignKey(blank=True, to='school.SemesterGrade', null=True)),
            ],
            options={
                'ordering': ['order', 'name'],
                'verbose_name_plural': 'Semester: Grades',
            },
        ),
        migrations.CreateModel(
            name='SemesterPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('period_number', models.IntegerField()),
                ('semester', models.ForeignKey(to='school.Semester')),
            ],
            options={
                'ordering': ['semester', 'period_number'],
                'verbose_name_plural': 'Semester: Period List',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('food_allergies', models.TextField(verbose_name=b'Allergies', blank=True)),
                ('birth_date', models.DateField(null=True, verbose_name=b'Birth date', blank=True)),
                ('notes', models.TextField(blank=True)),
                ('emergency_name', models.CharField(max_length=50, verbose_name=b'Emergency Contact', blank=True)),
                ('emergency_phone_number', models.CharField(max_length=20, verbose_name=b'Emergency phone number', blank=True)),
                ('emergency_notes', models.TextField(blank=True)),
                ('family_member', models.OneToOneField(verbose_name=b'name', to=settings.AUTH_USER_MODEL)),
                ('grade', models.ForeignKey(verbose_name=b'Grade', blank=True, to='school.PersonGrade', null=True)),
            ],
            options={
                'ordering': ['family_member'],
                'verbose_name': 'Student',
                'verbose_name_plural': 'People: Students',
            },
        ),
        migrations.CreateModel(
            name='StudentEnroll',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('schedule', select2.fields.ForeignKey(to='school.Schedule')),
                ('student', select2.fields.ForeignKey(to='school.Student')),
            ],
            options={
                'ordering': ['student', 'schedule'],
                'verbose_name_plural': 'Schedule: Student Enrollment',
            },
        ),
        migrations.CreateModel(
            name='StudentType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=25, verbose_name=b'Student Type')),
            ],
            options={
                'ordering': ['type'],
                'verbose_name_plural': 'People: Student Types',
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('notes', models.TextField(blank=True)),
                ('family_member', models.OneToOneField(verbose_name=b'name', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['family_member'],
                'verbose_name_plural': 'People: Teachers',
            },
        ),
        migrations.AddField(
            model_name='student',
            name='schedule',
            field=models.ManyToManyField(to='school.Schedule', through='school.StudentEnroll'),
        ),
        migrations.AddField(
            model_name='student',
            name='type',
            field=models.ForeignKey(default=2, blank=True, to='school.StudentType', null=True, verbose_name=b'Type'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='semester',
            field=select2.fields.ForeignKey(verbose_name=b'Semester', to='school.Semester'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='semester_grade',
            field=models.ManyToManyField(to='school.SemesterGrade', verbose_name=b'Grades'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='semester_period',
            field=models.ForeignKey(verbose_name=b'Semester Period', to='school.SemesterPeriod'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='teacher',
            field=models.ManyToManyField(to='school.Teacher', verbose_name=b'Teacher'),
        ),
        migrations.AddField(
            model_name='familymemberemail',
            name='person_contact_data_type',
            field=models.ForeignKey(to='school.PersonContactDataType'),
        ),
        migrations.AddField(
            model_name='family',
            name='family_benefits',
            field=models.ForeignKey(verbose_name=b'Role/Benefits', blank=True, to='school.FamilyBenefits', null=True),
        ),
        migrations.AddField(
            model_name='family',
            name='family_workflow',
            field=models.ManyToManyField(to='school.FamilyWorkflow', null=True, verbose_name=b'Workflow', blank=True),
        ),
        migrations.AddField(
            model_name='eventenrollment',
            name='family',
            field=select2.fields.ForeignKey(to='school.Family'),
        ),
        migrations.AddField(
            model_name='eventenrollment',
            name='title',
            field=select2.fields.ForeignKey(to='school.Event'),
        ),
        migrations.AddField(
            model_name='event',
            name='family',
            field=select2.fields.ForeignKey(verbose_name=b'Host Family', blank=True, to='school.Family', null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='fee_per',
            field=models.ForeignKey(verbose_name=b'Cost Per ____', blank=True, to='school.EventFeePer', null=True),
        ),
        migrations.AddField(
            model_name='coursecatalog',
            name='course_type',
            field=models.ForeignKey(verbose_name=b'Course Type', to='school.CourseType'),
        ),
        migrations.AddField(
            model_name='coursecatalog',
            name='semester_grade',
            field=models.ManyToManyField(to='school.SemesterGrade', verbose_name=b'Grades'),
        ),
        migrations.AddField(
            model_name='coursecatalog',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name=b'Course Owner', blank=True, to='school.Teacher', null=True),
        ),
        migrations.AddField(
            model_name='assistantenroll',
            name='schedule',
            field=select2.fields.ForeignKey(to='school.Schedule'),
        ),
        migrations.AddField(
            model_name='assistant',
            name='schedule',
            field=models.ManyToManyField(to='school.Schedule', through='school.AssistantEnroll'),
        ),
        migrations.AddField(
            model_name='familymember',
            name='email_list',
            field=models.ManyToManyField(to='school.EmailList', null=True, verbose_name=b'Email Lists', blank=True),
        ),
        migrations.AddField(
            model_name='familymember',
            name='family',
            field=select2.fields.ForeignKey(blank=True, to='school.Family', null=True),
        ),
        migrations.AddField(
            model_name='familymember',
            name='family_member_role',
            field=models.ForeignKey(blank=True, to='school.FamilyMemberRole', null=True),
        ),
        migrations.AddField(
            model_name='familymember',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='familymember',
            name='user_permissions',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions'),
        ),
    ]
