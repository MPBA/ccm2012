# -*- encoding: utf-8 -*-
__author__ = 'arbitrio@fbk.eu'

from django.conf.urls import patterns, url

from .views import UploadView, MyChunkedUploadView, MyChunkedUploadCompleteView


urlpatterns = patterns('engine.views',

    url(r'^$', UploadView.as_view(), name='upload'),
    url(r'^chunked_upload/?$', MyChunkedUploadView.as_view(), name='api_chunked_upload'),
    url(r'^chunked_upload_complete/?$', MyChunkedUploadCompleteView.as_view(), name='api_chunked_upload_complete'),
)