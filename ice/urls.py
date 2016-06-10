
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.sources, name='index'),
    url(r'^sources$', views.sources, name='sources'),
    url(r'^mean$', views.mean, name='mean'),
    url(r'^normal$', views.normal, name='normal'),
    url(r'^correlation$', views.correlation, name='correlation')
]