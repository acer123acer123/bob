*************************
**** INTRODUCTION *******
*************************

Home schooling is a tough job, as any parent will tell you, but it is made
a bit easier by local cooperatives that offer resources such as teaching,
social opportunities, field trips, etc.

Home school cooperatives, therefore, have unique needs that cannot be
easily satisified with off-the-shelf software.  And, if one is found
that meets most of the needs of the coopertative, the price is usually
too expensive for the group.

This project was created because our local home school cooperative needed
a way to manage students, courses, registration, events, and other tasks.

There was nothing available that could perform all of these functions so 
this project was created.

*************************
**** FEATURES ***********
*************************

	- The main goal was to make the software completely modular
		to achieve the greatest flexibility in every area
		(semesters, periods, enrollment dates, permissions, etc)
	- Mobile Friendly !!!
	- New family registration with (simple) workflow
	- Parental oversight and control of all child profiles and activities
	- Multiple roles for each family member: Teacher, Assistant, Student
	- Parent (teacher) can create courses including descriptions, required resources, etc.
	- Parent can enroll each child in classes, view family schedule
	- Parent can enroll themselves as assistants
	- Event management including registration for events
	- Reporting (ad-hoc and pre-configured)
	- Email list management (via Mailgun)
	- Each member can Opt-in/out email list through a simple interface
	- Parents can email teachers, assistants, students
	- Full administration site (Django Admin application)
	- Administrators can impersonate users (for troubleshooting)

*************************
**** HOSTING FEATURE ****
*************************
	We recognized that your cooperative may not have the time or experience to
	install, configure, and learn to use this application. Your time is better 
	spent teaching your children.

	We welcome you to download this application to your own servers for free but
	if you need help or would rather not spend the time managing it just let us know.

	We are available to install/configure and host your school.  

	We are not out to make a profit on this service so our costs aim to just 
	cover the cost of hosting and the time to manage the application for you.
	
	
	Email Christopher.Ryan@gmail.com for more information.


*************************
**** SCREENSHOTS ********
*************************

<p>
<h2>Home Screen</h2>
![alt tag](https://cloud.githubusercontent.com/assets/5222071/9633604/a4c8e4a6-515b-11e5-8fa8-e9605d556a32.png "Home Screen")


<p>
<h2>Student Enrollment</h2>
![alt tag](https://cloud.githubusercontent.com/assets/5222071/9633601/a28e162a-515b-11e5-977d-47468c339ed4.png "Enrollment")


<p>
<h2>Family Member Profile</h2>
![alt tag](https://cloud.githubusercontent.com/assets/5222071/9633603/a3b716a0-515b-11e5-95a5-7c5b6640c2df.png "Family Member Profile")


*************************
**** DOCUMENTATION ******
*************************

In the "documents" folder are files that contain information about this project:

	- DatabaseSchema.pptx - PowerPoint of the original database schema. This
				is not updated but very close to accurate.

	- FRED_2_Presentation_Outline_2014.docx - A Word document that 
				provides an overview of what this application is
				and how it can be used. It was created for
				a user training session.

	- FRED_Administrative_Guide.doc - The administration guide for the application.

	- *PDF files - These are documents that walk a user through the most
			common functions of the site:  Family enrollment, 
			Adding a course, and New Family Registration


************************
**** DEMO **************
************************
A demo is available at:

http://demo.flchomegroup.com

*******************************************************
**** I COULD REALLY USE SOME HELP WITH THIS CODE ******
*******************************************************

If you find this application useful and are proficient in Django, I could really use some help with this code. You'll find that it is not efficient (I'm not a programmer) and I would really like to make it so. I'd also like to replace a few of the functions with AJAX and am struggling with how to best handle that.  

I would welcome help with:

	- Updating / creating additional documentation
	- Reviewing the code and maybe finding just one or two areas that
	  you would be intersted in modifying and making more efficient
	- Reviewing the database calls and modifying them to be more efficient
	- Reviewing the database schema and suggesting indexes and other hints
	  to make it run faster.
