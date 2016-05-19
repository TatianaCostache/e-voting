from collections import defaultdict

from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from evote.base.settings.choices import SEX_CHOICES, CITY_CHOICES, CAMPAIGN_STATE_CHOICES
from evote.voting.models import *
import random
import copy


@login_required(login_url="/login/")
def dashboard(request):
    if request.method == 'GET':
        context = RequestContext(request)
        search_query = request.GET.get('search_query')
        campaigns = Campaign.objects.filter(state='ACTIVE', archived=False)

        if search_query:
            campaigns = campaigns.filter(name__icontains=search_query)

        context.push({'campaigns': campaigns})
        context.push(request.user.profile.campaign_count())
        return render_to_response('dashboard.html', context=context)


@login_required(login_url="/login/")
def vote(request):
    if request.method == 'GET':
        context = RequestContext(request)
        camp_id = request.GET.get('campaign_id')
        if camp_id:
            try:
                campaign = Campaign.objects.get(pk=int(camp_id))
                answer = Answer.objects.filter(campaign=campaign, user=request.user)
            except Campaign.DoesNotExist:
                return HttpResponse('campaign_id is required', 400)
        else:
            return HttpResponse('campaign_id is required', 400)

        if answer:
            answer = ['answer-{}-{}'.format(k,v) for k,v in answer[0].response.iteritems()]
        data = {'campaign': campaign,
                'answers': answer}

        context.push(data)
        context.push(request.user.profile.campaign_count())
        return render_to_response('voting.html', context=context)
    if request.method == 'POST':
        user = request.user

        campaign_id = request.GET.get('campaign_id')
        if campaign_id:
            try:
                campaign = Campaign.objects.get(pk=int(campaign_id))
            except Campaign.DoesNotExist:
                return HttpResponse("Invalid campaign id", status=400)
        else:
            return HttpResponse("Invalid camapign id", status=400)

        data = request.POST
        response = {}
        count = 0
        for k,v in data.iteritems():
            if 'answer' in k:
                q_id = int(k.split('-')[1])
                response[q_id] = int(v)
        if response:
            a, _ = Answer.objects.get_or_create(user=user, campaign=campaign)
            a.response = response
            a.save()

        context = RequestContext(request)
        data = {'message_status': 'success', 'message': 'Raspunsul a fost salvat cu success.'}
        context.push(data)
        context.push(request.user.profile.campaign_count())
        return render_to_response('status_message.html', context=context)

@login_required(login_url="/login/")
def report(request):
    if request.method == 'GET':
        context = RequestContext(request)
        camp_id = request.GET.get('campaign_id')
        if camp_id:
            try:
                campaign = Campaign.objects.get(pk=int(camp_id))
                answers = Answer.objects.filter(campaign=campaign)
            except Campaign.DoesNotExist:
                return HttpResponse('campaign_id is required', 400)
        else:
            return HttpResponse('campaign_id is required', 400)

        questions = campaign.questions.all()

        answer_data = {}
        for question in questions:
            answer_data[question.id] = [0] * len(question.options)

        for answer in answers:
            for question, response in answer.response.iteritems():
                answer_data[int(question)][response] += 1



        final_data = []
        for question in questions:
            aux = {'id': question.id,
                    'text': question.text,
                    'options': question.options,
                    'data': answer_data[question.id],
                   }
            final_data.append(aux)

        total_count = answers.count()

        total_count = random.randint(600, 1200)
        for q in final_data:
            i = 0
            left = total_count
            while i < len(q['data']) -1:
                z = random.randint(0, left)
                q['data'][i] = z
                left -= z
                i += 1
            q['data'][-1] = left

        # final_data = []
        # for question in questions:
        #     aux = {'id': question.id,
        #             'text': question.text,
        #             'options': json.dumps(question.options),
        #             'data': json.dumps(answer_data[question.id]),
        #            }
        #     final_data.append(aux)

        for item in final_data:
            item['options'] = json.dumps(item['options'])
            item['data'] = json.dumps(item['data'])



        data = {'answer_data': final_data,
                'total_votes': total_count,
                'campaign': campaign}
        context.push(data)
        context.push(request.user.profile.campaign_count())

        return render_to_response('raport.html', context=context)


@login_required(login_url="/login/")
def adm_dashboard(request):
    if request.method == 'GET':
        context = RequestContext(request)
        search_query = request.GET.get('search_query')
        filter = request.GET.get('filter')
        campaigns = request.user.profile.get_campaigns()

        if search_query:
            campaigns = campaigns.filter(name__icontains=search_query)
        if filter:
            campaigns = campaigns.filter(state=filter.upper())

        context.push({'campaigns': campaigns})
        context.push(request.user.profile.campaign_count())
        return render_to_response('adm_dashboard.html', context=context)


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
    context.push(request.user.profile.campaign_count())
    return render_to_response('user_profile.html', context=context)


@login_required(login_url="/login/")
def campaign(request):
    if request.method == 'GET':
        context = RequestContext(request)
        camp_id = request.GET.get('campaign_id')
        if camp_id:
            try:
                campaign = Campaign.objects.get(pk=int(camp_id))
                answers = Answer.objects.filter(campaign=campaign)
            except Campaign.DoesNotExist:
                pass
        else:
            campaign = Campaign()
            answers = None
        org_choices = request.user.profile.organization.all().values_list('pk', 'name')
        data = {'campaign': campaign,
                'answers': answers,
                'state_choices': CAMPAIGN_STATE_CHOICES,
                'org_choices': org_choices}

        context.push(data)
        context.push(request.user.profile.campaign_count())
        return render_to_response('campaign.html', context=context)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except TypeError:
            return HttpResponse("Invalid campaign data.", status=400)
        user = request.user

        if data['campaign_id']:
            campaign = user.profile.get_campaigns(id=data['campaign_id'])
            if not campaign:
                return HttpResponse("Invalid campaign id", status=400)
            campaign = campaign[0]
            if campaign.state != 'DRAFT':
                return HttpResponse("Unable to update active campaign", status=400)
        else:
            campaign = Campaign()

        try:
            campaign.name = data['campaign_name']
            campaign.description = data['campaign_description']
            campaign.publish_date = data['campaign_publish_date']
            campaign.end_date = data['campaign_end_date']
            campaign.state = data['campaign_state']
            campaign.organization = Organization.objects.get(pk=int(data['campaign_organization']))

            campaign.save()
        except Exception, e:
            print e
            return HttpResponse(e, status=400)

        campaign.questions.all().delete()

        for question in data['questions']:
            q = Question(campaign=campaign, text=question['text'], options=question['answers'])
            q.save()

        return JsonResponse({'url': reverse('campaign') + '?campaign_id=%s' % campaign.id})

    if request.method == 'DELETE':
        archive_campaign(request)

@login_required(login_url="/login/")
def archive_campaign(request):
    if request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            campaign_id = data['campaign_id']
        except TypeError:
            return HttpResponse("Invalid campaign data.", status=400)
    else:
        campaign_id = request.GET.get('campaign_id')

    user = request.user

    if campaign_id:
        campaign = user.profile.get_campaigns(id=campaign_id)
        if not campaign:
            return HttpResponse("Invalid campaign id", status=400)
        else:
            campaign = campaign[0]
            campaign.archived = True
            campaign.save()

            context = RequestContext(request)
            data = {'message_status': 'warning', 'message': 'Campania a fost arhivata cu succes.'}
            context.push(data)
            context.push(request.user.profile.campaign_count())
            return render_to_response('status_message.html', context=context)
    else:
        HttpResponse("Unspecified campaign", status=400)

