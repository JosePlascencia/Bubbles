from __future__ import unicode_literals
from django.shortcuts import render, redirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q
import bcrypt
from .models import *
import tweepy
from datetime import datetime
import time

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
    
    consumer = Type.objects.get(name='twitter')
    auth = tweepy.OAuthHandler(consumer.key, consumer.secret)

    user = User.objects.get(id=request.session['user'])
    a_type = Type.objects.get(name='twitter')
    acc = Account.objects.get(user=user, a_type=a_type)
    auth.set_access_token(acc.key, acc.secret)

    api = tweepy.API(auth)

    public_tweets = api.home_timeline()
    tweets=[]
    for tweet in public_tweets:
        json = tweet._json

        img = ''
        if 'media' in json['entities']:
            if 'media_url_https' in json['entities']['media'][0]:
                img = json['entities']['media'][0]['media_url_https']
        
        created_at = json['created_at']
        arr = created_at.split(' ')
        created_at = " ".join(arr[0:4])
        created_at = " ".join([created_at,arr[5]])
        date_formatted = datetime.strptime(created_at, '%a %b %d %H:%M:%S %Y')
        sec = time.mktime(date_formatted.timetuple())
        tweets.append(['twitter', {'name' : json['user']['name'], 'desc': json['text'], 'screename': json['user']['screen_name'], 'img': img, 'date': json['created_at']}, sec])

    # api.update_status('tweepy + oauth! I am awesome')
