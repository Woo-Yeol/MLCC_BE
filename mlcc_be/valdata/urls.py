"""handwritefont_be URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import DataListView, BboxListView, MarginListView, DataRetrieveView,\
     BboxRetrieveView, MarginRetrieveView, ManualLogListView, \
    main, detail, self_train, set_schedule, set_thr, set_environment_variable, \
        curr_inference_model, set_inference_model, eval_self_train, sample_img


urlpatterns = [
    path('main', main),
    path('detail/<str:name>', detail),
    path('data', DataListView.as_view()),
    path('bbox', BboxListView.as_view()),
    path('margin', MarginListView.as_view()),
    path('log', ManualLogListView.as_view()),
    path('setting/mode', set_schedule),
    path('setting/thr', set_thr),
    path('data/<str:pk>', DataRetrieveView.as_view()),
    path('bbox/<str:pk>', BboxRetrieveView.as_view()),
    path('margin/<str:pk>', MarginRetrieveView.as_view()),
    path('setting', set_environment_variable),
    path('learning', self_train),
    path('learning/eval', eval_self_train),
    path('model', curr_inference_model),
    path('model/sampleimg', sample_img),
    path('model/<str:name>', set_inference_model),
    
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
