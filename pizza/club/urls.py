from django.conf.urls import patterns, url, include

# It's a pretty straight forward mapping, and we don't want to have import
# every class separately.
from club.View import ClubView
from club.View import UserView

urlpatterns = patterns('',
                       url(r'^$', ClubView.as_view()),
                       url(r'^views/list/$', ClubView.as_view(command='list')),
                       url(r'^views/details/$', ClubView.as_view(command='details')),
                       url(r'^views/event/$', ClubView.as_view(command='event')),
                       url(r'^login/$', UserView.as_view(command='login')),
                       url(r'^create/$', UserView.as_view(command='create')),
                       # 'backend' call.
                       url(r'^views/vote/$', ClubView.as_view(command='be_vote')),
                       # We don't use the standard auth urls because we don't
                       # Setup a few overrides from the standard auth urls
#                       url(r'^logout/$', 'django.contrib.auth.views.logout'),
                       url('^', include('django.contrib.auth.urls'))
)
