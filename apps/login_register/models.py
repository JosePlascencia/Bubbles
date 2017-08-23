# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import re


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z]{2,}$')
PASSWORD_REGEX = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,}$')

# Create your models here.
class UserManager(models.Manager):
    def validator(self,postData):
        errors = {}
        if not NAME_REGEX.match(postData["last_name"]):
            errors["first_name"] = "First name should be more than 2 characters and only letters"
        if not NAME_REGEX.match(postData["last_name"]):
            errors["last_name"] = "Last name should be more than 2 characters and only letters"
        if not EMAIL_REGEX.match(postData["email"]):
            errors["email"] = "Entered an invalid email" 
        if not PASSWORD_REGEX.match(postData["password"]):
            errors["password"] = "Password should be more than 8 characters, contain 1 Uppercase, 1 Number, 1 Special Character"
        if postData["password"] != postData["confirm"]:
            errors["confirm"] = "Passwords don't match"
        return errors;

class User(models.Model):
    username = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = UserManager()

class Type(models.Model):
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)

class Account(models.Model):
    key = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    user = models.ForeignKey(User, related_name='accounts', on_delete=models.CASCADE)
    a_type = models.ForeignKey(Type, related_name = 'accounts', on_delete=models.CASCADE)