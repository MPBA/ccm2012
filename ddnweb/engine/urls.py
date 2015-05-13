# -*- encoding: utf-8 -*-
__author__ = 'arbitrio@fbk.eu'

from django.conf.urls import patterns, url

from .views import CreateDeaseaseNetwork, NetworkView


urlpatterns = patterns('engine.views',


    url(regex='^get_json_network/$', view=CreateDeaseaseNetwork.as_view(), name='get_json_network'),
    url(regex='^network_view/$', view=NetworkView.as_view(), name='network_view'),


)