from django.views.generic import RedirectView
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    #url(r'^$', RedirectView.as_view(url='/quiz/')),

    url(r'^admin/', admin.site.urls),

    url(r'^', include('quiz.urls')),
]
