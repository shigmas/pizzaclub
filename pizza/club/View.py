from django.http import HttpRequest, StreamingHttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.views.generic import View

from django.contrib import auth

from django.db.models import Avg

# Template libs
from django.shortcuts import render

import datetime

import string

import os
import json

from club.models import *

class BaseView(View):
    command = ''

    kDetailsCommand         = 'details'
    kEventCommand           = 'event'
    kVoteCommand            = 'be_vote'

    kListCommand            = 'list'
    kLoginCommand           = 'login'
    kCreateCommand          = 'create'

    kIdParam                = 'id'
    ContentType = 'application/json'

    def _getParams(self):
        postParams = self.request.POST
        getParams = self.request.GET

        if len(postParams) > 0:
            return postParams
        else:
            return getParams

    def get(self, request):
        return self._handleCommand(self.command)

    def post(self, request):
        return self._handleCommand(self.command)

class UserView(BaseView):
    def _handleCommand(self, command):
        if command == self.kLoginCommand:
            return self._login()
        elif command == self.kCreateCommand:
            return self._create()
        else:
            return self._login()

    def _getUserCreds(self, params):
        if not params.has_key('username') or not params.has_key('password'):
            return None, None, None

        username = params['username']
        password = params['password']

        if params.has_key('email'):
            return username, password, params['email']
        else:
            return username, password, None

    def _create(self):
        createTemplate = 'club/create.html'
        context = {}
        username, password, email = self._getUserCreds(self._getParams())

        if not username or not password or not email:
            context['error_message'] = 'Missing username, password or email'
            return render(self.request, createTemplate, context)

        userExists = True
        try:
            user = User.objects.get(username=username)
        except:
            userExists = False

        if userExists:
            context['error_message'] = 'User already exists'
            return render(self.request, createTemplate, context)

        user = User.objects.create_user(username, email, password)

        return HttpResponseRedirect('/club/')

    def _login(self):
        loginTemplate = 'club/login.html'
        context = {}
        username, password, email = self._getUserCreds(self._getParams())

        if not username or not password:
            context['error_message'] = 'Missing username or password'
            return render(self.request, loginTemplate, context)

        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(self.request, user)
        else:
            context['error_message'] = 'Invalid username or password'
            return render(self.request, loginTemplate, context)

        return HttpResponseRedirect('/club/')

# Base class for the page views.
class ClubView(BaseView):

    def _handleCommand(self, command):
        if command == self.kDetailsCommand:
            return self._details()
        elif command == self.kListCommand:
            return self._list()
        elif command == self.kEventCommand:
            return self._event()
        elif command == self.kVoteCommand:
            return self._vote()
        else:
            print('fallback')
            return self._index()

    def _index(self):
        return render(self.request, 'club/index.html',{})

    def _list(self):
        context = {}
        pizzerias = Pizzeria.objects.all()
        shops = []
        for p in pizzerias:
            shop = {}
            shop['name'] = p.name
            shop['id'] = p.id
            shop['url'] = p.url
            shops.append(shop)

        context['pizzeria_list'] = shops
        return render(self.request, 'club/list.html',context)

    def _details(self):
        params = self._getParams()
        context = {}

        if params.has_key(self.kIdParam):
            shopId = params[self.kIdParam];
            pizzeria = Pizzeria.objects.get(pk=shopId)
            visits = Visit.objects.filter(pizzeria = shopId)

            vs = []
            for visit in visits:
                v = {}
                v['id'] = visit.id
                v['date'] = visit.visitDate
                v['notes'] = visit.diningNotes
                v['crust'] = Vote.objects.filter(visit = visit.id).aggregate(Avg('crust'))['crust__avg']
                v['sauce'] = Vote.objects.filter(visit = visit.id).aggregate(Avg('sauce'))['sauce__avg']
                v['service'] = Vote.objects.filter(visit = visit.id).aggregate(Avg('service'))['service__avg']
                v['creativity'] = Vote.objects.filter(visit = visit.id).aggregate(Avg('creativity'))['creativity__avg']
                v['overall'] = Vote.objects.filter(visit = visit.id).aggregate(Avg('overall'))['overall__avg']

                vs.append(v)

            context['pizzeria'] = pizzeria
            context['visit_list'] = vs

        return render(self.request, 'club/details.html',context)

    def _event(self):
        params = self._getParams()
        eventId = params[self.kIdParam];
        context = {}

        context['event_id'] = eventId
        return render(self.request, 'club/event.html',context)

    def _dbVote(self, visit, user, vote):
        print('_dbVote')
        if not vote.has_key('crust'):
            print('missing required params for vote')
            return
        newCrust = vote['crust']
        newSauce = vote['sauce']
        newService = vote['service']
        newCreativity = vote['creativity']
        newOverall = vote['overall']
        print('creating or updating vote')

        voteExists = True
        vote = None
        try:
            vote = Vote.objects.filter(visit = visit.id).get(voter = user)
        except:
            voteExists = False

        if vote is None:
            vote = Vote(visit = visit, voter = user)

        vote.crust = newCrust
        vote.sauce = newSauce
        vote.service = newService
        vote.creativity = newCreativity
        vote.overall = newOverall

        vote.save()
        return

    def _vote(self):
        acceptType = self.request.META.get('HTTP_ACCEPT')
        content = json.loads(self.request.body)

        response = {}
        # the only required key, so if we don't have it, return.
        if not content.has_key('event_id'):
            print('_vote return empty response')
            return StreamingHttpResponse(json.dumps(response),
                                         content_type=self.ContentType)

        eventId = content['event_id']
        event = Visit.objects.get(pk = eventId)
        if self.request.user.is_authenticated() and \
           content.has_key('vote'):
            print('authed and vote key present %s',content['vote'])
            # update if necessary
            self._dbVote(event, self.request.user, content['vote'])

        votes = Vote.objects.filter(visit = int(eventId))
        vs = []
        print('event Id: %s, %d votes' % (eventId, len(votes)))
        for vote in votes:
            v = {}
            v['name'] = vote.voter.username
            v['crust'] = vote.crust
            v['sauce'] = vote.sauce
            v['service'] = vote.service
            v['creativity'] = vote.creativity
            v['overall'] = vote.overall
            vs.append(v)

            if vote.voter == self.request.user:
                print("adding user's vote")
                response['id_crust'] = vote.crust
                response['id_sauce'] = vote.sauce
                response['id_service'] = vote.service
                response['id_creativity'] = vote.creativity
                response['id_overall'] = vote.overall
        response['event_id'] = eventId
        response['vote_list'] = vs

        return StreamingHttpResponse(json.dumps(response),
                                     content_type=self.ContentType)

