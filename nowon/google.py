import pandas as pd

import os
from ga4 import GA4RealTimeReport

from Config_Inicial import config_var_google
config_var_google()



ID_PROPRIEDADE = '318095805'
os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

lista_dimensao = ['country', 'deviceCategory']
lista_metricas = ['activeUsers']

ga4_realtime = GA4RealTimeReport(ID_PROPRIEDADE)
response = ga4_realtime.query_report(
    lista_dimensao, lista_metricas, 10, True
)

cols = response['headers']
data = response['rows']

df = pd.DataFrame(data=data,columns=cols)

print(df)