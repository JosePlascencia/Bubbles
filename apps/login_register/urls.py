from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^register$', views.register),
    url(r'^login$', views.login),
    url(r'^addBubbles$', views.addBubbles),
    url(r'^wall$', views.wall),
    url(r'^logout$', views.logout),
    url(r'^link/twitter$', views.link_twitter),
    url(r'^link/instagram$', views.link_instagram),
    url(r'^verification/twitter$', views.verification_twitter),
    url(r'^verification/instagram$', views.verification_instagram),
]