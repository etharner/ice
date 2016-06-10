from django.conf.urls import include, url

urlpatterns = [
    url(r'^', include('ice.urls')),
]
