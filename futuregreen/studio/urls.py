# studio/urls.py

from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic import ListView, DetailView, TemplateView, DateDetailView, MonthArchiveView
from futuregreen.studio.models import NewsItem

urlpatterns = patterns('',
    url(r'^$', 'futuregreen.studio.views.index', name = 'studio'),
    url(r'^news/$', ListView.as_view(model=NewsItem, context_object_name = "news_list"), name = 'newsitem_list'),
    url(r'^news/(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
        DateDetailView.as_view(model=NewsItem, context_object_name = "news",
                               date_field="date_published", template_name = "studio/newsitem_detail.html"),
        name = 'newsitem_detail'),
    url(r'^news/(?P<year>\d{4})/(?P<month>\w{3})/$',
        MonthArchiveView.as_view(model=NewsItem,
                                 context_object_name = "news_list",
                                 date_field="date_published"),
        name='news_archive_month'
    ),
    (r'^people/', include('futuregreen.people.urls')),
)