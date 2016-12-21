"""bcpp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from bcpp.views.search_bhs_subject_view import BHSSubjectSearchView
from bcpp.views.search_plot_view import SearchPlotView

urlpatterns = [
    url(r'^bhs_search',
        BHSSubjectSearchView.as_view(), name='bhs_subject_search'),
    url('plot/', include('plot.urls')),
    url('household/', include('household.urls')),
    url('member/', include('member.urls')),
    url('subject/', include('bcpp_subject.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^search/$', SearchPlotView.as_view(), name='search_url'),
    url(r'^household_search/$', SearchPlotView.as_view(), name='household_search_url'),
]
