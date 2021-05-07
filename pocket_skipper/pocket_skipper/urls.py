from django.views.generic.base import RedirectView
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()

from . import settings


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    
    url(r'^pocket$', 'theapp.views.landing', name='landing'),
    url(r'^skipper$', 'theapp.views.skipper', name='skipper'),
    
    url(r'^$', 'theapp.views.home', name='home'),
    

    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    
    (r'(?P<path>.*)$', 'django.views.static.serve',
                                {'document_root': r'C:/work/pocket_skipper/pocket_skipper/pocket_skipper/templates'}),
    
    (r'^fonts/(?P<path>.*)$', 'django.views.static.serve',
                                {'document_root': r'C:/work/pocket_skipper/pocket_skipper/pocket_skipper/templates/fonts'}),
    (r'^img/(?P<path>.*)$', 'django.views.static.serve',
                                {'document_root': r'C:/work/pocket_skipper/pocket_skipper/pocket_skipper/templates/img'}),
    
    url(r'^favicon\.ico$', RedirectView.as_view(url='/img/favicon.ico')),
)

urlpatterns += staticfiles_urlpatterns()
