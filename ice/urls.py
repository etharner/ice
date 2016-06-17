from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.sources, name='index'),
    url(r'^sources$', views.sources, name='sources'),
    url(r'^mean$', views.mean, name='mean'),
    url(r'^normal$', views.normal, name='normal'),
    url(r'^correlation$', views.correlation, name='correlation'),
    url(r'^ice/data/(bering|chukchi|japan|okhotsk)_(source|mean|normal).csv$', views.get_data_src, name='get_data_src'),
    url(r'^ice/correlation/img/.*$', views.get_corr_img, name='get_corr_img'),
    url(r'^ice/correlation/data/.*$', views.get_corr_src, name='get_corr_src'),
    url(r'^ice/correlation/zip/.*$', views.get_corr_zip, name='get_corr_zip'),
    url(r'^forecast$', views.forecast, name='forecast'),
    url(r'^ice/forecast/.*$', views.get_forecast, name='get_forecast'),
    url(r'^report$', views.report, name='report'),
    url(r'^ice/report/.*$', views.get_pdf_tex, name='get_pdf_tex')
]
