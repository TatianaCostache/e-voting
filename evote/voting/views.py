from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from evote.base.settings.choices import SEX_CHOICES, CITY_CHOICES, CAMPAIGN_STATE_CHOICES
from evote.voting.models import *
import random
import copy


@login_required(login_url="/login/")
def dashboard(request):
    context = RequestContext(request)
    campaigns = list(Campaign.objects.all())
    campaign_count = {'ACTIVE_camp': 0, 'FINISHED_camp':0, 'DRAFT_camp': 0}
    for c in campaigns:
        campaign_count[c.state+'_camp'] += 1
    context.push({'campaigns': campaigns})
    context.push(campaign_count)
    return render_to_response('dashboard.html', context=context)


def logout(request):
    logout(request)

@login_required(login_url="/login/")
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.last_name = request.POST['last_name']
        user.first_name = request.POST['first_name']
        user.email = request.POST['email']
        profile = user.profile
        profile.age = request.POST['age']
        profile.sex = request.POST['sex']
        profile.city = request.POST['city']

        profile.save()
        user.save()
    context = RequestContext(request)
    context.push({'request': request,
                  'sex_choices': SEX_CHOICES,
                  'city_choices': CITY_CHOICES})
    return render_to_response('user_profile.html', context=context)

@login_required(login_url="/login/")
def campaign(request):
    context = RequestContext(request)
    camp_id = request.GET.get('campaign_id')
    campaign = None
    answers = None
    if camp_id:
        try:
            campaign = Campaign.objects.get(pk=int(camp_id))
            answers = Answer.objects.filter(campaign=campaign)
        except Campaign.DoesNotExist:
            pass
    org_choices = request.user.profile.organization.all().values_list('pk', 'name')
    data = {'campaign': campaign,
            'answers': answers,
            'state_choices': CAMPAIGN_STATE_CHOICES,
            'org_choices': org_choices}

    context.push(data)
    return render_to_response('campaign.html', context=context)
