from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Q
from django.http import Http404
from .models import Movie,Myrating
from django.contrib import messages
from .forms import UserForm
from django.db.models import Case, When
from .recommendation import Myrecommend
from .pso_recommendation import recommendMovie
import numpy as np 
import pandas as pd
from django.http import HttpResponse


def profile(request):
	curr_user = request.user
	movies_rated = Myrating.objects.filter(user=curr_user)

	context = {'movies': movies_rated}

	return render(request,'web/profile.html',{'movies':movies_rated})


# for recommendation
def recommend(request):
	if not request.user.is_authenticated:
		return redirect("login")
	if not request.user.is_active:
		raise Http404
	user = request.user
	movies_recommended = recommendMovie(user)
	
	return render(request,'web/recommend.html',{'movies_recommended':movies_recommended})


# List view
def index(request):
	movies = Movie.objects.all()
	query  = request.GET.get('q')
	if query:
		movies = Movie.objects.filter(Q(title__icontains=query)).distinct()
		return render(request,'web/list.html',{'movies':movies})
	return render(request,'web/list.html',{'movies':movies})


# detail view
def detail(request,movie_id):
	if not request.user.is_authenticated:
		return redirect("login")
	if not request.user.is_active:
		raise Http404
	movies = get_object_or_404(Movie,id=movie_id)
	#for rating
	curr_rating = 0
	my_rating_object = [x for x in Myrating.objects.filter(user=request.user, movie=movies)]
	if len(my_rating_object) != 0:
		curr_rating = my_rating_object[0].rating

	if request.method == "POST":
		rate = request.POST['rating']
		# ratingObject = Myrating()
		# ratingObject.user   = request.user
		# ratingObject.movie  = movies
		# ratingObject.rating = rate
		# ratingObject.save()

		# try:
		
		print(my_rating_object)
		if len(my_rating_object) == 0:
			ratingObject = Myrating()
			ratingObject.user   = request.user
			ratingObject.movie  = movies
			ratingObject.rating = rate
			ratingObject.save()
		else:
			obj = my_rating_object[0]
			obj.rating = rate
			obj.save()

		messages.success(request,"Your Rating is submited ")
		return redirect("index")

	# GET REQUEST	
	return render(request,'web/detail.html',{'movies':movies, 'rating': curr_rating})


# Register user
def signUp(request):
	form =UserForm(request.POST or None)
	if form.is_valid():
		user      = form.save(commit=False)
		username  =	form.cleaned_data['username']
		password  = form.cleaned_data['password']
		user.set_password(password)
		user.save()
		user = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				login(request,user)
				return redirect("index")
	context ={
		'form':form
	}
	return render(request,'web/signUp.html',context)				


# Login User
def Login(request):
	if request.method=="POST":
		username = request.POST['username']
		password = request.POST['password']
		user     = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				login(request,user)
				return redirect("index")
			else:
				return render(request,'web/login.html',{'error_message':'Your account disable'})
		else:
			return render(request,'web/login.html',{'error_message': 'Invalid Login'})
	return render(request,'web/login.html')

#Logout user
def Logout(request):
	logout(request)
	return redirect("login")




