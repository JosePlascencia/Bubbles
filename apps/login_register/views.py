from __future__ import unicode_literals
from django.shortcuts import render, redirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q
import bcrypt
from .models import *
import tweepy

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
        print "got a post command"
        errors = User.objects.validator(request.POST)
        if len(errors):
            for tag, error in errors.iteritems():
                messages.error(request,error, extra_tags=tag)
            return redirect("/register")
        else:
            users = User.objects.filter(email=request.POST['email'])
            if len(users):
                messages.error(request,"This email is already in use!")
                return redirect("/register")
            else:
                User.objects.create(first_name = request.POST['first_name'],last_name = request.POST['last_name'],email = request.POST['email'],password=bcrypt.hashpw(request.POST['password'].encode(),bcrypt.gensalt()))
                request.session['user'] =  User.objects.get(email=request.POST["email"]).id
                return redirect("/addBubbles")
    elif request.method == "GET":
        print "got a get command"
        return render(request, "login_register/registration.html")

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

def link_twitter(request):
    key = Type.objects.get(name='twitter').key
    secret = Type.objects.get(name='twitter').secret
    auth = tweepy.OAuthHandler(key, secret, 'http://localhost:8000/verification/twitter')

    try:
        redirect_url = auth.get_authorization_url()
        print redirect_url
    except tweepy.TweepError:
        print 'Error! Failed to get request token.'

    request.session['request_token'] =  auth.request_token

    return redirect(redirect_url)

def verification_twitter(request):

    key = Type.objects.get(name='twitter').key
    secret = Type.objects.get(name='twitter').secret
    verifier = request.GET.get('oauth_verifier')

    auth = tweepy.OAuthHandler(key, secret)
    token = request.session['request_token']
    del request.session['request_token']
    auth.request_token = token

    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        print 'Error! Failed to get access token.'

    user = User.objects.get(id=request.session['user'])
    a_type = Type.objects.get(name='twitter')
    if not len(Account.objects.filter(user=user, a_type=a_type)):
        Account.objects.create(key=auth.access_token,secret= auth.access_token_secret,user=user,a_type=a_type)
    else:
        acc = Account.objects.get(user=user, a_type=a_type)
        acc.key = auth.access_token
        acc.secret= auth.access_token_secret
        acc.save()

    return redirect('/addBubbles')

def getTweet(request):
    # auth = tweepy.OAuthHandler('mwGD4LnSsAYe3fHJGgUuHu5Z9', 'Ga3pr3CUZhJMp0lrqrtWQwckINE7R1Jv8NOF0HBbERAdOaBA3X')
    a_type = Type.object.get(name='twitter').id
    user_key = Account.objects.get(user=request.session['user'], a_type=a_type).key
    user_secret = Account.objects.get(user=request.session['user'], a_type=a_type).secret
    
    auth.set_access_token(user_key, user_secret)

    api = tweepy.API(auth)

    # api.update_status('tweepy + oauth! I am awesome')

    public_tweets = api.home_timeline()
    for tweet in public_tweets:
        print tweet.text
    

    acc = Account.objects.get(user=user, a_type=a_type)
    auth.set_access_token(acc.key, acc.secret)

    api = tweepy.API(auth)

    # api.update_status('tweepy + oauth! I am awesome')

    public_tweets = api.home_timeline()
    for tweet in public_tweets:
        print tweet.text
    # auth.set_access_token(auth.access_token, auth.access_token_secret)

    # api = tweepy.API(auth)

    # # api.update_status('tweepy + oauth! I am awesome')

    # public_tweets = api.home_timeline()
    # for tweet in public_tweets:
    #     print tweet.text