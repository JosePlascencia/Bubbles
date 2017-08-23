from __future__ import unicode_literals
from django.shortcuts import render, redirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q
import bcrypt
from .models import *

def index(request):
    if 'user' not in request.session:
        request.session['user'] = 0
    return render(request, "login_register/index.html")

def wall(request):
    return render(request, "login_register/wall.html")

def addBubbles(request):
    return render(request, "login_register/addBubbles.html")

def register(request):
    if request.method == "POST":
        errors = User.objects.validator(request.POST)
        if len(errors):
            for tag, error in errors.iteritems():
                messages.error(request,error, extra_tags=tag)
            return redirect("/")
        else:
            users = User.objects.filter(email=request.POST['email'])
            if len(users):
                messages.error(request,"This email is already in use!")
                return redirect("/")
            else:
                User.objects.create(first_name = request.POST['first_name'],last_name = request.POST['last_name'],email = request.POST['email'],password=bcrypt.hashpw(request.POST['password'].encode(),bcrypt.gensalt()))
                request.session['user'] =  User.objects.get(email=request.POST["email"]).id
                return redirect("/addBubbles")

def login(request):
    if request.method == "POST":
        user = User.objects.filter(email=request.POST['email'])
        if len(user):
            if bcrypt.checkpw(request.POST['password'].encode(),user[0].password.encode()):
                request.session['user'] = user[0].id
                return redirect("/wall")
            else:
                messages.error(request,"Failed to validate password!")
                return redirect("/")
        else:
            messages.error(request,"Failed to find email in Database...")
            return redirect("/")

def logout(request):
    request.session['user'] = 0
    return redirect("/")