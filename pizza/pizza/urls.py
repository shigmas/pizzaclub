from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'pizza.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^club/', include('club.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
