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
    path('v1/mark_as_read', views.mark_as_read, name='mark_as_read'),

    path('', views.home, name='home'),
    # url(r'^favicon\.ico$', RedirectView.as_view(url='/img/favicon.ico')),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)