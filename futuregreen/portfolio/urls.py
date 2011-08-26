# portfolio/urls.py

from django.conf import settings
from django.conf.urls.defaults import *

from futuregreen.portfolio.views import *

urlpatterns = patterns('',
   url(r'^projects/$', ProjectListView.as_view(), name='projects_project_list'),
   url(r'^projects/completed/$', ProjectCompletedListView.as_view(), name='projects_project_completed'),
   url(r'^projects/current/$', ProjectCurrentListView.as_view(), name = 'projects_project_current'),
   url(r'^projects/scale/ascending/$', ProjectSizeAscListView.as_view(), name = 'projects_project_area_asc'),
   url(r'^projects/scale/desending/$', ProjectSizeDescListView.as_view(), name = 'projects_project_area_desc'),
   url(r'^project/(?P<slug>[-\w]+)/$', ProjectDetailView.as_view(), name = 'projects_project_detail'),
)