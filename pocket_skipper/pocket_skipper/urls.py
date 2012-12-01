from django.conf.urls import patterns, include, url
from django.views.generic.simple import redirect_to

from dajaxice.core import dajaxice_autodiscover
dajaxice_autodiscover()

import settings


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    
    url(r'^pocket$', 'theapp.views.landing', name='landing'),
    url(r'^skipper$', 'theapp.views.skipper', name='skipper'),
    
    url(r'^$', 'theapp.views.home', name='home'),
    

    (r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
    
    (r'(?P<path>.*)$', 'django.views.static.serve',
                                {'document_root': r'C:/work/pocket_skipper/code/pocket_skipper/templates'}),
    # url(r'^pocket_skipper/', include('pocket_skipper.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
