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
import urllib
import urllib2
import requests
from operator import itemgetter
import math


###########Override Tweepy stream listener####################################
class MyStreamListener(tweepy.StreamListener):
    def on_data(self, data):
        print data
        return true

    def on_error(self, status_code):
        print status_code

###########Retrieve Twitter posts##############################################
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
        tweets.append(['twitter', {'name' : json['user']['name'], 'desc': json['text'], 'screenname': json['user']['screen_name'], 'img': img, 'date': json['created_at']}, int(sec)])

    mystream = tweepy.Stream(auth=api.auth, listener=MyStreamListener())

    print mystream

    return tweets


###########Retrieve Instagram posts##############################################
def getInstagram(request):
    user = User.objects.get(id=request.session['user'])
    a_type = Type.objects.get(name='instagram')
    access_token = Account.objects.get(user=user,a_type=a_type).key

    user_follows = requests.get('https://api.instagram.com/v1/users/self/follows?access_token=' + access_token)
    content = user_follows.json()

    # Gets the list of user IDs who User follows
    user_follows_id_list = []
    for id in content['data']:
        user_follows_id_list.append(id['id'])

    # Gets all the post of all the User friends
    user_friend_posts = []
    for user in user_follows_id_list:
        temp = (requests.get('https://api.instagram.com/v1/users/' + user + '/media/recent/?access_token=' + access_token))
        user_friend_posts.append(temp.json())

    # Filters through all the data to take only post info
    cleaned_data = []
    for useful_data in user_friend_posts:
        cleaned_data.append(useful_data['data'])

    # Filters further to get specific data about the instagrams
    instagrams=[]
    for per_user in cleaned_data:
        for per_post in per_user:
            instagrams.append(['instagram', {'name' : per_post['user']['full_name'], 'desc': '', 'screenname': per_post['user']['username'], 'img': per_post['images']['standard_resolution']['url'], 'date': per_post['created_time']}, int(per_post['created_time']) + 25200])
    return instagrams


def index(request):
    if 'user' not in request.session:
        request.session['user'] = 0
    return render(request, "login_register/index.html")

def wall(request):
    comments = []

    #TODO:validate if twitter or instagram are added as accounts
    try:
        comments += getTweet(request)
    except:
        pass
    try:
        comments += getInstagram(request)
    except:
        pass

    array = sorted(comments, key=itemgetter(2))
    
    user = User.objects.get(id=request.session['user'])
    twitter = Type.objects.get(name="twitter")
    instagram = Type.objects.get(name="instagram")

    context = {
        'posts' : array,
        'name' : user.first_name,
        'twitter' : Account.objects.filter(user=user,a_type=twitter),
        'instagram' : Account.objects.filter(user=user,a_type=instagram)
    }

    return render(request, "login_register/wall.html", context)

def addBubbles(request):
    user = User.objects.get(id=request.session['user'])
    twitter = Type.objects.get(name="twitter")
    instagram = Type.objects.get(name="instagram")

    context = {
        'name' : user.first_name,
        'twitter' : Account.objects.filter(user=user,a_type=twitter),
        'instagram' : Account.objects.filter(user=user,a_type=instagram)
    }
    return render(request, "login_register/addBubbles.html", context)

def register(request):
    if request.method == "POST":
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

    # api.update_status('tweepy + oauth! I am awesome')


def link_instagram(request):
    key = Type.objects.get(name='instagram').key
    secret = Type.objects.get(name='instagram').secret
    redirect_url = 'https://api.instagram.com/oauth/authorize/?client_id=' + key + '&redirect_uri=http://localhost:8000/verification/instagram&response_type=code&scope=public_content+follower_list+comments+relationships+likes'
    return redirect(redirect_url)


def verification_instagram(request):
    code = request.GET.get('code')
    key = Type.objects.get(name='instagram').key
    secret = Type.objects.get(name='instagram').secret

    post_data = {'client_id': key, 'client_secret': secret, 'grant_type': 'authorization_code', 'redirect_uri': 'http://localhost:8000/verification/instagram', 'code': code}

    response= requests.post('https://api.instagram.com/oauth/access_token', data=post_data)
    content = response.json()
    access_token = content['access_token']

    user = User.objects.get(id=request.session['user'])
    a_type = Type.objects.get(name='instagram')
    if not len(Account.objects.filter(user=user, a_type=a_type)):
        Account.objects.create(key=access_token,user=user,a_type=a_type)
    else:
        acc = Account.objects.get(user=user, a_type=a_type)
        acc.key = access_token
        acc.save()
    
    return redirect('/addBubbles')