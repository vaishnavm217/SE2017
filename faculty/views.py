from __future__ import unicode_literals
from django.template.context import RequestContext
import json as simplejson
from django.http import HttpResponse
import json
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template import loader
from django.shortcuts import render_to_response
from home.models import *
from home.models import Assignment
from .forms import UploadFileForm
from home.serializers import *
import easygui
import json
from django.utils import timezone 
import datetime
from datetime import datetime
from django.utils import formats
from dateutil.parser import parse

def index(request):
	all_events = Events.objects.all()
	serializer = EventsSerializer(all_events, many=True)
	a=[]
	for i in serializer.data:

		a.append({"title":i["Event_Name"],"start":i["Event_Date"],"allDay":True})
	print serializer.data
	return render(request, 'fullcalendar/calendar.html',{"Events":json.dumps(a)})
	
	
	
def ViewProfs(request):
    CourseList = []
    if request.user.personnel.Role.Role_name == 'Faculty':
	request.session['Prof_Name']=request.user.username
        person_id = request.user.personnel.Person_ID
        IC = Instructors_Courses.objects.all()
        for i in range(0, len(IC)):
            if person_id == IC[i].Inst_ID.Person_ID:
                CourseList.append(IC[i].Course_ID.Course_Name)
	if CourseList==[]:
            flag=0
	    
	else:
            flag=1
    template = loader.get_template('prof.html')
    context = {'flag':flag,'Courses':CourseList,'Prof_Name':request.session['Prof_Name']}
    return HttpResponse(template.render(context, request))


def CoursePage(request):		
	if request.POST.get('action')=='Save':
		
		course=Courses.objects.get(Course_Name=request.session['course'])
		course.Course_description = request.POST.get('coursedes')
		try:
        		course.save()
		except:
			easygui.msgbox("Oops!Data Too Long.",title="ERROR")
					
	else:   
		request.session['course'] =request.POST.get('dropdown')	
	course=get_object_or_404(Courses,Course_Name=request.session['course']) 				
    	template = loader.get_template('prof1.html')
    	context = {'Course':course,'CourseName':request.session['course']}
    	return HttpResponse(template.render(context, request))
	
	


def AddAssignment(request):
    s=0
    if request.method == 'POST':
        form =request.FILES.get('file')
  	date_joined =datetime.now()
	if parse(request.POST.get('enddate'))>=date_joined:
		courses = Courses.objects.all()
		for corse in courses:
			if corse.Course_Name == request.session['course']:
		            course = Courses.objects.get(Course_Name=corse.Course_Name)
		            break
		instance = Assignment(Course_ID=course, Assignment_File=request.FILES['file'],End_Time=request.POST.get('enddate'))
		instance.save()
	    	s=1
	else:
		s=2    
	return render(request, 'forms.html',{'CourseName':request.session['course'],'s':s})
	    
    else:
	
		if 'course' in request.session:
        		form = UploadFileForm()
			s=0        
    			return render(request, 'forms.html',{'CourseName':request.session['course'],'form': form, 'request': request,'s':s})
		else:
			easygui.msgbox("please select a course",title="ERROR")
			return redirect('http:../ViewProfs/')

def ViewAssignment(request):
     asslist = []
     Assignments = Assignment.objects.all()
     for ass in Assignments:
	if 'course' in request.session:
     		if ass.Course_ID.Course_Name ==request.session['course'] and ass.End_Time.date()!=datetime.strptime('1900-01-01',"%Y-%m-%d").date():
			print ass.Assignment_File
			asslist.append(ass)
	else:
		easygui.msgbox("please select a course",title="ERROR")
		return redirect('http:../ViewProfs/')
     return render(request, 'assignment.html', {'Assignments': asslist,'CourseName':request.session['course']})
  

    
def OfferCourses(request):
    if request.method == 'POST':
        person_id = request.user.personnel.Person_ID
        person = Personnel.objects.get(Person_ID=person_id)
        courseids = request.POST.getlist('courses[]')
        for cid in courseids:
            corse = Courses.objects.get(Course_ID=cid)
            IC = Instructors_Courses(Course_ID=corse, Inst_ID=person, Start_Date='2017-1-1',End_Date='2017-1-1')
            IC.save()
	return redirect('http:../offercourses/')
	
	
    else:
        IC = Instructors_Courses.objects.all()
        IClist = []
	courselist=[]
        for ic in IC:
            IClist.append(ic.Course_ID)
        person_id = request.user.personnel.Person_ID
        courses = Courses.objects.all()
        courses1 = []
        for corse in courses:
            if corse not in IClist:
                courses1.append(corse)
	for course in courses:
		courselist.append(course.Course_ID)
		courselist.append(course.Course_Name)
		
        template = loader.get_template('reg.html')
        context = {'Courses': courses1,'Courses1':json.dumps(courselist), 'IC': IC, 'Prof_Name': request.user.username}
    	return HttpResponse(template.render(context, request))

def ViewAttendance(request):	
    	studentcount={}
	sessioncount=0
	coursestudents=Students_Courses.objects.all()
	students=Attendance.objects.all()
    	classes=Attendance_Session.objects.all()
	for Class in classes:
		try:
			if Class.Course_Slot.Course_ID.Course_Name==request.session['course']:
				sessioncount=sessioncount+1
		except:
			easygui.msgbox("      please select a course       ",title="ERROR")
			return redirect('http:../ViewProfs/')
			
		
	for student in coursestudents:
		value=[0,1]
		if student.Course_ID.Course_Name==request.session['course']:
			value[0]=student.Student_ID.LDAP.username
			value[1]=sessioncount
			studentcount[student.Student_ID.Person_ID]=value	
	for student in students:
		if student.ASession_ID.Course_Slot.Course_ID.Course_Name==request.session['course'] and student.Marked=='P':
			studentcount[student.Student_ID.Person_ID][1]=studentcount[student.Student_ID.Person_ID][1]-1
	if request.method=="POST":
		return HttpResponse(request.POST.get('abc'))			    
    	template = loader.get_template('attendance.html')
    	context = {'classes':studentcount,'CourseName':request.session['course'],'workingdays':sessioncount}
    	return HttpResponse(template.render(context, request))	

def MyLibrary(request):
    s=0
    libfiles=[]
    if request.method == 'POST':
	courses = Courses.objects.all()
	libfiles=request.FILES.getlist("files")
	for corse in courses:
		if corse.Course_Name == request.session['course']:
			course = Courses.objects.get(Course_Name=corse.Course_Name)
		        break
	for libfile in libfiles:
		instance = Assignment(Course_ID=course, Assignment_File=libfile,End_Time='1900-01-01')
		instance.save()
	s=1
	asslist = []
     	Assignments = Assignment.objects.all()
     	for ass in Assignments:
		if ass.Course_ID.Course_Name ==request.session['course'] and ass.End_Time.date()==datetime.strptime('1900-01-01',"%Y-%m-%d").date():
			asslist.append(ass)       
    	return render(request, 'lib.html',{'MyLibList':asslist,'CourseName':request.session['course'],'s':s})
	
	    
    else:
	asslist = []
	s=0 
     	Assignments = Assignment.objects.all()
     	for ass in Assignments:
		if ass.Course_ID.Course_Name ==request.session['course'] and ass.End_Time.date()==datetime.strptime('1900-01-01',"%Y-%m-%d").date():
			asslist.append(ass)       
    	return render(request, 'lib.html',{'MyLibList':asslist,'CourseName':request.session['course'],'s':s})
	

