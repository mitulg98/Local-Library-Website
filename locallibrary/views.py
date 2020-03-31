from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render 
from django.core.exceptions import PermissionDenied
from calendar import HTMLCalendar
import datetime

def permission_denied_error(request):
	raise PermissionDenied

def response_error_handler(request):
	return HttpResponse("Error handler content", status=403)

def func(request):
	title="This Year"
	year=int(datetime.date.today().year)
	month=int(datetime.date.today().month)
	cal=HTMLCalendar().formatmonth(year,month)
	return render(request,'index.html',{'title':title,'cal':cal})

handler403=response_error_handler