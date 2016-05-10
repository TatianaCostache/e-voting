from __future__ import unicode_literals

from datetime import datetime

import json
from django.db import models
from django.db.models import Count
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField

import pytz

from evote.base.settings.choices import SEX_CHOICES, CITY_CHOICES, CAMPAIGN_STATE_CHOICES


class Organization(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    organization = models.ManyToManyField(Organization, related_name='users', blank=True)
    age = models.IntegerField()
    sex = models.CharField(max_length=10, choices=SEX_CHOICES)
    city = models.CharField(max_length=30, choices=CITY_CHOICES)

    def __str__(self):
        return self.user.username


class Campaign(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=15, choices=CAMPAIGN_STATE_CHOICES)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    publish_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    private = models.BooleanField(default=False)
    target_group = JSONField(blank=True, null=True, default=None)
    organization = models.ForeignKey(Organization, related_name='campaigns')

    def completion(self):
        def _get_min(td):
            return td.days * 24*60 + td.seconds/60 * 1.0

        percent = _get_min(datetime.utcnow().replace(tzinfo=pytz.utc) - self.publish_date)/_get_min(self.end_date - self.publish_date) * 100
        return '{0:.1f}'.format(3)


    def count_voters(self):
        c = User.objects.filter(answers__campaign__id=self.pk).distinct().count()
        return c


    def __str__(self):
        return self.name

class Question(models.Model):
    campaign = models.ForeignKey(Campaign, related_name='questions')
    text = models.TextField()
    options = JSONField()

    def get_options(self):
        return json.loads(self.options)


class Answer(models.Model):
    user = models.ForeignKey(User, related_name='answers')
    campaign = models.ForeignKey(Campaign, related_name='answers')
    question = models.ForeignKey(Question, related_name='answers')
    response = JSONField()


class CampaignResult(models.Model):
    campaign = models.ForeignKey(Campaign)
    result = JSONField()
    
