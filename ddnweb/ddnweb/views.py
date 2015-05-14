# -*- coding: utf-8 -*-
__author__ = 'arbitrio@fbk.eu'

from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView


class DashboardView(TemplateView):
    template_name = 'ddnweb/index.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        return context