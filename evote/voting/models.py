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

    def get_campaigns(self, id=None):
        all = Campaign.objects.filter(organization__in=self.organization.all(), archived=False)
        if id is not None:
            all = all.filter(id=id)
        return all

    def campaign_count(self):
        campaign_count = {'ACTIVE_camp': 0, 'FINISHED_camp':0, 'DRAFT_camp': 0}
        for c in self.get_campaigns():
            campaign_count[c.state+'_camp'] += 1
        return campaign_count


class Campaign(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True, default='')
    state = models.CharField(max_length=15, choices=CAMPAIGN_STATE_CHOICES, default='DRAFT')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    publish_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    private = models.BooleanField(default=False)
    target_group = JSONField(blank=True, null=True, default=None)
    organization = models.ForeignKey(Organization, related_name='campaigns')
    archived = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    def completion(self):
        def _get_min(td):
            return td.days * 24*60 + td.seconds/60

        percent = _get_min(datetime.utcnow().replace(tzinfo=pytz.utc) - self.publish_date)/(_get_min(self.end_date - self.publish_date) + 1) * 100
        if percent > 100:
            percent = 100
        elif percent <= 0:
            percent = 1

        return '{0:.1f}'.format(percent)


    def count_voters(self):
        c = User.objects.filter(answers__campaign__id=self.pk).count()
        return c


    def __str__(self):
        return self.name

class Question(models.Model):
    campaign = models.ForeignKey(Campaign, related_name='questions')
    text = models.TextField()
    options = JSONField()


class Answer(models.Model):
    user = models.ForeignKey(User, related_name='answers')
    campaign = models.ForeignKey(Campaign, related_name='answers')
    response = JSONField(default=dict())

    class Meta:
        unique_together = (("user", "campaign"),)


class CampaignResult(models.Model):
    campaign = models.ForeignKey(Campaign)
    result = JSONField()
    
