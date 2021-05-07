from django.views.generic.base import RedirectView
from django.urls import include, path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static


from . import settings

from theapp import views


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    
    path('pocket', views.landing, name='landing'),
    path('skipper', views.skipper, name='skipper'),
    
    path('', views.home, name='home'),
    

    
    # (r'(?P<path>.*)$', 'django.views.static.serve',
    #                             {'document_root': r'C:/work/pocket_skipper/pocket_skipper/pocket_skipper/templates'}),
    #
    # (r'^fonts/(?P<path>.*)$', 'django.views.static.serve',
    #                             {'document_root': r'C:/work/pocket_skipper/pocket_skipper/pocket_skipper/templates/fonts'}),
    # (r'^img/(?P<path>.*)$', 'django.views.static.serve',
    #                             {'document_root': r'C:/work/pocket_skipper/pocket_skipper/pocket_skipper/templates/img'}),
    #
    # url(r'^favicon\.ico$', RedirectView.as_view(url='/img/favicon.ico')),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)