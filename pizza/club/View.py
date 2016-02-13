from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.views.generic import View

from django.contrib import auth

from django.db.models import Avg

# Template libs
from django.shortcuts import render

import datetime

import string
import inspect
import types

from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

import os
import json

from club.models import *

class BaseView(View):
    command = ''

    kResultParam            = 'result'
    kMessageParam           = 'message'
    kUsernameParam          = 'login'

    # Set in the Django URL mappings (urls.py)
    command = ''

    commandHandlers = {}

    def getVerifiedHandler(self):
        func = self.commandHandlers[self.command]
        if func is None:
            raise Exception('No handler for command %s' % self.command)

        spec = inspect.getargspec(func)
        # Not too strict, but enough to make sure we are fairly close to the
        # required signature.
        if len(spec.args) < 2 or len(spec.args) > 2 or spec.args[0] != 'self':
            raise Exception('Handler %s does not satisfy signature requirements' % func.__name__)

        return func

    def _handleCommand(self):
        res = None
        serverSuccess = True
        packResult = None
        try:
            unpackData = json.loads(self.request.body)
            # We've verified that we got a legit handler, else we'll throw an
            # exception
            res = self.getVerifiedHandler()(unpackData)
            if type(res) is types.TupleType:
                # not sure what kind of error
                packResult = {self.kResultParam:res[0],
                              self.kMessageParam:res[1]}
            else:
                packResult = res
        except Exception as e:
            print('Exception: %s' % e)

        return JsonResponse(packResult, safe=True)

    def get(self, request):
        return self._handleCommand()

    def post(self, request):
        return self._handleCommand()

class StartView(BaseView):

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return self._setCookie()

    def _setCookie(self):
        return HttpResponseRedirect('/static/html/index.html')

class UserView(BaseView):

    kCreateCommand          = 'create'
    kLoginCommand           = 'login'
    kInfoCommand            = 'info'

    kPasswordParam          = 'passwd'
    kEmailParam             = 'email'

    def dispatch(self, *args, **kwargs):
        # We need to access self, so we use dispatch to set the 
        # commandHadlers property
        self.commandHandlers.update({ self.kCreateCommand: self._create,
                                      self.kLoginCommand: self._login,
                                      self.kInfoCommand: self._info,
                                  })
        return super(UserView, self).dispatch(*args, **kwargs)

    def _getCreds(self, content):
        username = content.get(self.kUsernameParam, None)
        password = content.get(self.kPasswordParam, None)
        email = content.get(self.kEmailParam, None)

        return username, password, email

    def _info(self, content):
        username = 'Anonymous'
        if self.request.user.is_authenticated():
            username = self.request.user.username

        return {self.kUsernameParam:username}

    def _create(self, content):
        username, password, email = self._getCreds(content)
        if not username or not password or not email:
            return False, 'Missing username, password or email'

        userExists = True
        try:
            user = User.objects.get(username=username)
        except:
            userExists = False

        if userExists:
            return False, 'User already exists'

        user = User.objects.create_user(username, email, password)

        if user is None:
            return False, 'Unable to create user'

        return { self.kResultParam:True }

    def _login(self, content):
        username, password, email = self._getCreds(content)
        if not username or not password:
            return False, 'Missing username or password'

        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(self.request, user)
        else:
            return False, 'Invalid username or password'

        return {self.kResultParam:True}

# Base class for the page views.
class ClubView(BaseView):

    kDetailCommand         = 'detail'
    kListCommand            = 'list'
    kEventCommand           = 'event'
    kVoteCommand            = 'vote'

    kIdParam             = 'id'
    kVisitIdParam        = 'visit_id'
    kNameParam           = 'name'
    kNeighborhoodParam   = 'neighborhood'
    kStyleParam          = 'specialty'
    kUrlParam            = 'url'
    kDateParam           = 'date'
    kNotesParam          = 'notes'
    kUserParam           = 'user'
    kCrustParam          = 'crust'
    kSauceParam          = 'sauce'
    kServiceParam        = 'service'
    kCreativityParam     = 'creativity'
    kOverallParam        = 'overall'
    kCommentParam        = 'comment'

    kPizzeriaListParam   = 'pizzeria_list'
    kPizzeriaParam       = 'pizzeria'
    kVisitListParam      = 'visit_list'
    kVoteParam           = 'vote'
    kVoteListParam       = 'vote_list'

    def dispatch(self, *args, **kwargs):
        # We need to access self, so we use dispatch to set the 
        # commandHadlers property
        self.commandHandlers.update({ self.kDetailCommand: self._detail,
                                      self.kListCommand: self._list,
                                      self.kEventCommand: self._event,
                                      self.kVoteCommand: self._vote
                                  })
        return super(ClubView, self).dispatch(*args, **kwargs)

    def _pizzaToDict(self, pizzeria):
        return {self.kNameParam: pizzeria.name,
                self.kIdParam: pizzeria.id,
                self.kNeighborhoodParam: pizzeria.neighborhood.name,
                self.kStyleParam: pizzeria.specialty.style,
                self.kIdParam: pizzeria.id,
                self.kUrlParam: pizzeria.url}

    def _list(self, content):
        # List of restaurants
        pizzerias = Pizzeria.objects.all()
        result = {}

        shops = []
        for p in pizzerias:
            shops.append(self._pizzaToDict(p))
        result[self.kPizzeriaListParam] = shops
        return result

    def _detail(self, content):
        # Restaurant summary
        shopId = content.get(self.kIdParam, None)

        if shopId is None:
            return False, 'id must be provided for detail'

        pizzeria = Pizzeria.objects.get(pk=shopId)
        visits = Visit.objects.filter(pizzeria = shopId)

        vs = []
        for visit in visits:
            v = {}
            v[self.kIdParam] = visit.id
            v[self.kDateParam] = visit.visitDate
            v[self.kNotesParam] = visit.diningNotes

            votes = Vote.objects.filter(visit = visit.id)
            # If we don't have any votes yet, we don't have anything to show.
            # Sending back None seems like it might mislead the client to think
            # that there's something there.
            if len(votes) > 0:
                v[self.kCrustParam] = votes.aggregate(Avg('crust'))['crust__avg']
                v[self.kSauceParam] = votes.aggregate(Avg('sauce'))['sauce__avg']
                v[self.kServiceParam] = votes.aggregate(Avg('service'))['service__avg']
                v[self.kCreativityParam] = votes.aggregate(Avg('creativity'))['creativity__avg']
                v[self.kOverallParam] = votes.aggregate(Avg('overall'))['overall__avg']
            else:
                print('no votes')
            vs.append(v)

        results = {}
        results[self.kPizzeriaParam] = self._pizzaToDict(pizzeria)
        results[self.kVisitListParam] = vs

        return results

    def _event(self, content):
        # Detail about a particular visit
        visitId = content.get(self.kIdParam,None)
        if visitId is None:
            return False, 'event ID required for event listing'

        votes = Vote.objects.filter(visit = visitId)
        userVote = None
        vs = []
        for vote in votes:
            v = {self.kUsernameParam: vote.voter.username,
                 self.kCrustParam: vote.crust,
                 self.kSauceParam: vote.sauce,
                 self.kServiceParam: vote.service,
                 self.kCreativityParam: vote.creativity,
                 self.kOverallParam: vote.overall,
                 self.kCommentParam: vote.comment,
             }
            vs.append(v)
            
            if vote.voter == self.request.user:
                userVote = v

        result = {}
        result[self.kVoteListParam] = vs
        result[self.kVoteParam] = userVote

        return result

    def _dbVote(self, visit, user, vote):
        print('_dbVote')
        newCrust = vote.get(self.kCrustParam, None)
        newSauce = vote.get(self.kSauceParam, None)
        newService = vote.get(self.kServiceParam, None)
        newCreativity = vote.get(self.kCreativityParam, None)
        newOverall = vote.get(self.kOverallParam, None)
        newComment = vote.get(self.kCommentParam, None)
        if not newCrust or not newSauce or not newService or \
           not newCreativity or not newOverall or not newComment:
            print('%s %s %s %s %s %s' % (newCrust, newSauce, newService, newCreativity, newOverall, newComment))
            return False, 'missing required params for vote'

        vote = None
        try:
            vote = Vote.objects.filter(visit = visit.id).get(voter = user)
        except:
            vote = Vote(visit = visit, voter = user)

        vote.crust = newCrust
        vote.sauce = newSauce
        vote.service = newService
        vote.creativity = newCreativity
        vote.overall = newOverall
        vote.comment = newComment

        print('saving vote!')
        return vote.save() is None

    def _vote(self, content):
        print('vote')
        # the only required key, so if we don't have it, return.
        visitId = content.get(self.kIdParam, None)
        if visitId is None:
            return False, 'visit id required'

        voteContent = content.get(self.kVoteParam, None)
        if voteContent is None:
            return False, 'no vote information'

        visit = Visit.objects.get(pk = visitId)
        print('fetched visit: %s' % visit)
        success = False
        if self.request.user.is_authenticated():
            print('user: %s' % self.request.user)
            # update if necessary
            print('content: %s ' % voteContent)
            success = self._dbVote(visit, self.request.user, voteContent)
        else:
            return False, 'User is not authenticated.  Can\'t vote'

        if success:
            # Return the same data we get from the _event callback, since it's
            # been updated.  Saves us a call
            return self._event(content)
        else:
            return False, 'Error saving vote'
