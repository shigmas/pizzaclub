from django.conf.urls import patterns, url, include

# It's a pretty straight forward mapping, and we don't want to have import
# every class separately.
from club.View import ClubView
from club.View import UserView
from club.View import StartView

urlpatterns = patterns('',
                       url(r'^$', StartView.as_view(command='start')),
                       url(r'^api/info/$', UserView.as_view(command='info')),
                       url(r'^api/login/$', UserView.as_view(command='login')),
                       url(r'^api/create/$', UserView.as_view(command='create')),
                       url(r'^api/detail/$', ClubView.as_view(command='detail')),
                       url(r'^api/list/$', ClubView.as_view(command='list')),
                       url(r'^api/event/$', ClubView.as_view(command='event')),
                       url(r'^api/vote/$', ClubView.as_view(command='vote')),
                       # We don't use the standard auth urls because we don't
                       # Setup a few overrides from the standard auth urls
#                       url(r'^logout/$', 'django.contrib.auth.views.logout'),
                       url('^', include('django.contrib.auth.urls'))
)
