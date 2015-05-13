# -*- coding: utf-8 -*-
__author__ = 'ernesto'
import pandas as pd
import json
from utils import transform_json_for_sigmajs
from django.views.generic.base import View, TemplateView
from utils import LoadDDN
from braces.views import JSONResponseMixin, AjaxResponseMixin
from django.core.urlresolvers import reverse_lazy


class CreateDeaseaseNetwork(JSONResponseMixin, AjaxResponseMixin, View):

    def get_data(self):
        input_diseases = ['496.000', '490.000']

        nma = 15

        '''
        Input:
        - ddn, pd.DataFrame, disease network
        - disease_desc, pd.DataFrame, disease description
        - input_diseases, list, input diseases

        Output:
        - neigh_diseases, dict, potential diseases
        '''
        ddnsource = LoadDDN()
        disease_desc = ddnsource.deasease_dataframe()[1]
        ddn = ddnsource.deasease_dataframe()[0]
        # init structures (neigh_diseases, input_d)
        input_d = pd.DataFrame({'id' : input_diseases})

        # retrieve input disease description (input_d_desc)
        input_d_desc = disease_desc.ix[input_d['id']]

        # retrieve first degree neighborhood (ddn_sub)
        ddn_sub1 = input_d.merge(ddn, left_on='id', right_on='id_d1', how='left')
        ddn_sub2 = input_d.merge(ddn, left_on='id', right_on='id_d2', how='left')
        tmp = ddn_sub2.loc[:,'id_d2'].copy()
        ddn_sub2.loc[:,'id_d2'] = ddn_sub2.loc[:,'id_d1'].copy()
        ddn_sub2.loc[:,'id_d1'] = tmp.copy()
        tmp = ddn_sub2.loc[:,'prev_d2'].copy()
        ddn_sub2.loc[:,'prev_d2'] = ddn_sub2.loc[:,'prev_d1'].copy()
        ddn_sub2.loc[:,'prev_d1'] = tmp.copy()
        ddn_sub = pd.concat([ddn_sub1, ddn_sub2])
        ddn_sub.reset_index(inplace=True)

        # selects high co-morbidity disease network by phi
        phinet_1 = ddn_sub.sort('phi', ascending=False).iloc[0:nma].copy()
        phinet_1_nodes = pd.DataFrame(phinet_1.loc[:,'id_d2'])
        # retrieve co-morbidity disease description
        phinet_1_nodes_desc = disease_desc.ix[phinet_1_nodes['id_d2']]

        # find interactions between high co-morbidity diseases
        temp1 = phinet_1_nodes.merge(ddn, left_on='id_d2', right_on='id_d2', how='inner')
        phinet_1_intra = phinet_1_nodes.merge(temp1, left_on='id_d2', right_on='id_d1', how='inner')
        # phinet = phinet.merge(ddn_sub, left_on='id_d2', right_on='id_d2', how='left')
        phinet_1_intra.reset_index(inplace=True)

        phinet_1_nodes_final = pd.concat([input_d_desc, phinet_1_nodes_desc])
        phinet_1_nodes_final['code'] = phinet_1_nodes_final.index
        phinet_1_nodes_final_json = json.loads(phinet_1_nodes_final.to_json(orient='index')) ##

        # network
        phinet_1.drop(['index', 'id'], axis=1, inplace=True)
        phinet_1_intra.drop(['id_d2_x'], axis=1, inplace=True)
        phinet_1_intra = phinet_1_intra.reindex_axis(['id_d1', 'id_d2_y'] + list(phinet_1_intra.columns[3:]), axis=1)
        phinet_1_intra.rename(columns={'id_d2_y': 'id_d2'}, inplace=True)
        phinet_1_intra['intra'] = 1
        phinet_1['intra'] = 0
        phinet_1_final = pd.concat([phinet_1, phinet_1_intra])
        phinet_1_final = phinet_1_final.reset_index(drop=True)
        phinet_1_final_json = phinet_1_final.to_json(orient='index') ##
        json_net_final = '[{0}]'.format(phinet_1_final_json.replace('"0":', '')[1:-1])

        network = transform_json_for_sigmajs(phinet_1_nodes_final_json, json_net_final, input_diseases)

        return network

    def get(self, request, *args, **kwargs):
        return self.get_ajax(request, *args, **kwargs)

    def get_ajax(self, request, *args, **kwargs):
        return self.render_json_response(self.get_data())


class NetworkView(TemplateView):
    template_name = 'engine/network.html'
    success_url = reverse_lazy('network-view')

    def get_context_data(self, **kwargs):
        context = super(NetworkView, self).get_context_data(**kwargs)
        return context
