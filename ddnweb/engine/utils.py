# -*- coding: utf-8 -*-
__author__ = 'ernesto'
import pandas as pd
import numpy as np
from django.conf import settings
from random import randint
import json


class LoadDDN:

    def __init__(self):
        self.filepath_diagnosis_legend = '{0}/{1}'.format(settings.MEDIA_ROOT, 'diagnosis_legend.txt')
        self.filepath_allnet = '{0}/{1}'.format(settings.MEDIA_ROOT, 'HuDiNe_AllNet5.net')

    def patologie_dataframe(self, filepath_patologie):
        A = pd.read_table(filepath_patologie, sep=";", header=0, dtype=object, na_values='')
        A1 = A[A['CODICE_ISTAT'].astype(np.str) != "nan"].copy()
        A1.loc[:, 'CODICE_ISTAT'] = A1.loc[:,'CODICE_ISTAT'].str.strip()
        A2 = A1[~A1['CODICE_ISTAT'].str.contains('[a-zA-Z]+')].copy()
        tmpind = ~ A2['CODICE_ISTAT'].str.contains('.', regex=False)
        A2.ix[tmpind, 'CODICE_ISTAT'] = A2.ix[tmpind, 'CODICE_ISTAT'].copy() + '.000'
        A3 = A2[A2['CODICE_ISTAT'].str.contains('.', regex=False)]

        a = pd.Series(A3['CODICE_ISTAT'].unique())
        b = a.str.split('.')
        c = pd.DataFrame(b.to_dict().values(), columns=['M', 'm'])
        c['CODICE_ISTAT'] = a
        c1 = (c['M'].str.len() > 3) & (c['M'].str.startswith('0'))
        ce = c[(c['M'].str.len() > 3) & (~c['M'].str.startswith('0'))]
        ce2 = c[(c['M'].str.len() < 3)]
        c.ix[c1, 'M'] = c.ix[c1, 'M'].str[1:]
        c['M.m'] = c.ix[:, 'M'] + '.' + c.ix[:, 'm']
        A4 = A3.merge(c, on='CODICE_ISTAT', how='inner')
        A4 = A4.reindex()
        return A4

    def deasease_dataframe(self):
        B = pd.read_table(self.filepath_allnet, sep="\t", header=-1, dtype={0: object, 1: object, 2: float, 3: float,
                                                                            4: float, 5: float, 6: float, 7: float,
                                                                            8: float, 9:float}, na_values='')
        B.columns = ["id_d1", "id_d2", "prev_d1", "prev_d2", "co-occurrence", "RR", "RR_99l", "RR_99r", "phi", "t-test"]
        tmpind = ~B['id_d1'].str.contains('.', regex=False)
        B.ix[tmpind, 'id_d1'] = B.ix[tmpind, 'id_d1'].copy() + '.000'
        tmpind = ~B['id_d2'].str.contains('.', regex=False)
        B.ix[tmpind, 'id_d2'] = B.ix[tmpind, 'id_d2'].copy() + '.000'
        B1 = B[B['prev_d1'] > 5].copy()
        B2 = B1[B1['prev_d2'] > 5].copy()

        # ICD9 id format
        # All codes are 6 characters long
        # The decimal point comes between the 3rd and 4th characters
        # If the code starts with a V character the decimal point comes between the 2nd and 3rd characters
        Blegend = pd.read_table(self.filepath_diagnosis_legend, sep="\t", header=0, dtype=object, na_values='')
        Blegend_noV = Blegend[~Blegend.loc[:, 'DIAGNOSIS CODE'].str.contains('[a-zA-Z]+')]
        tmp = Blegend_noV['DIAGNOSIS CODE'].copy()
        Blegend_noV.loc[:, 'code'] = (tmp.str[0:3] + '.' + tmp.str[3:])
        tmpind = Blegend_noV['code'].str.len() == 4
        Blegend_noV.ix[tmpind, 'code'] = Blegend_noV.ix[tmpind, 'code'].copy() + '000'
        Blegend_noV = Blegend_noV.set_index('code', drop=False)
        ddn = B2
        disease_desc = Blegend_noV
        return ddn, disease_desc


def transform_json_for_sigmajs(nodes_json, edges_json, input_diseases):
    nodes_dict = []
    edges_dict = []
    y = 0
    for n in dict(nodes_json).itervalues():
        print n

        nodes_dict.append({"id": str(n['code']), "label": n['LONG DESCRIPTION'],
                           "x": 0 if str(n['code']) in input_diseases else randint(3, 30),
                           "y": y if str(n['code']) in input_diseases else randint(4, 30),
                           "size": 6 if str(n['code']) in input_diseases else 3,
                           "color": "#606060" if str(n['code']) in input_diseases else "#005c91"})
        y += 2

    i = 1
    for e in eval(json.loads(json.dumps(edges_json))):
        print e
        edges_dict.append({"size": e['phi']*100, "weights": e['phi'], "id": "e{0}".format(i), "source": str(e['id_d1']),
                           "target": str(e['id_d2']), "color": "#005c91" if e['intra'] == 1 else "#606060"})
        i += 1
    network = {"nodes": nodes_dict, "edges": edges_dict}
    return network
