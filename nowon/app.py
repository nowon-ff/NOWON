import os
from flask import Flask, url_for, render_template, session, redirect
from authlib.integrations.flask_client import OAuth

import pandas as pd
import random
from datetime import date

from Config_Inicial import config_var_flask
config_var_flask()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY_FLASK')

# configuração do oauth

# /**/*/*/* CONSTRUIR CLASSE DO USUARIO /***//**/*/*/*/*/

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='1045049658322-qf2ifhcotdnatco1tqs2aosfkbmk3sab.apps.googleusercontent.com',
    client_secret='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',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://www.googleapis.com/auth/analytics.readonly',
    client_kwargs={'scope' : 'openid profile email'},
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs"
)
#    client_id='1045049658322-qf2ifhcotdnatco1tqs2aosfkbmk3sab.apps.googleusercontent.com',
#    client_secret='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',
#    access_token_url='https://accounts.google.com/o/oauth2/token',
#    access_token_params=None,
#    authorize_url='https://accounts.google.com/o/oauth2/auth',
#    authorize_params=None,
#    api_base_url='https://www.googleapis.com/oauth2/v1/',
#    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
#    client_kwargs={'scope':'https://www.googleapis.com/auth/analytics.readonly'},
#    client_kwargs={'scope' : 'openid profile email'},
#    jwks_uri="https://www.googleapis.com/oauth2/v3/certs"


@app.route("/")
def index():
    user = dict(session)
    # user = dict(session)
    if user:
        return render_template("perfil.html",user=user)
    return render_template('home.html',user=user)

@app.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo',token=token)
    user_info = resp.json()
    print("XXXXXXXXXXXXXXX")
    print(user_info)
    # do something with the token and profile
    session['email'] = user_info['email']
    session['nome'] = user_info['name']
    session['profile-photo'] = user_info['picture']

    return redirect('/')

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')
    

@app.route("/analise_diaria")
def analise_diaria():
    df = pd.read_csv('../nowon/data/google_ads.csv')
    conta_selecionada = random.choice(df['nome_conta'])

    df_filtrado = df[df['nome_conta']==conta_selecionada]
    
    dia = random.choice(range(2,7))
    data_atual = f'{date.today().year}-{date.today().month}-{str(0)+str(dia)}'
    data_antiga = f'{date.today().year}-{date.today().month}-{str(0)+str(dia-1)}'

    df_atual = df_filtrado[df_filtrado['Date']==data_atual]
    df_antigo = df_filtrado[df_filtrado['Date']==data_antiga]

    obj_atual = df_atual[['impressoes','cliques','interacoes','conversoes','investido']].sum()
    obj_antigo = df_antigo[['impressoes','cliques','interacoes','conversoes','investido']].sum()

    # CTR
    ctr_atual = obj_atual.cliques / obj_atual.impressoes
    ctr_antigo = obj_antigo.cliques / obj_antigo.impressoes
    
    if ctr_atual > ctr_antigo:
        ctr_diff = '{:.2f}'.format((ctr_atual - ctr_antigo) * 100)
        condicao_ctr = 'Aumentou (⏫)'
    elif ctr_antigo > ctr_atual:
        ctr_diff = '{:.2f}'.format((ctr_antigo - ctr_atual) * 100)
        condicao_ctr = 'Diminuiu (⏬)'
    else:
        ctr_diff = 0
        condicao_ctr = "Manteve"

    # CLIQUES
    atual_primeiro_cliques = df_atual.groupby(by='nome_campanha').sum().sort_values(by='cliques',ascending=False).iloc[0] 
    nome_campanha = atual_primeiro_cliques.name
    atual_clique = atual_primeiro_cliques.cliques


    antigo_campanha_cliques = df_antigo[df_antigo['nome_campanha'] == nome_campanha].iloc[0]
    antigo_clique = antigo_campanha_cliques.cliques

    if atual_clique > antigo_clique:
        cliques_diff = '{:.2f}'.format(((atual_clique / antigo_clique)-1)*100)
        condicao_clique = 'teve um aumento (⏫)'
    elif antigo_clique > atual_clique:
        cliques_diff = '{:.2f}'.format(((atual_clique / antigo_clique)-1)*100)
        condicao_clique = 'teve uma diminuição (⏬)'
    else:
        cliques_diff = 0
        condicao_clique = "manteve a porcentagem"

    # CONVERSOES
    atual_conv = atual_primeiro_cliques.conversoes  
    antigo_conv = antigo_campanha_cliques.conversoes

    if atual_conv > antigo_conv:
        conv_diff_por = '{:.2f}'.format(((atual_conv / antigo_conv)-1)*100)
        conv_diff_qtde = '{:.0f}'.format(atual_conv - antigo_conv)
        condicao_conv = 'tiveram um aumento (⏫)'
    elif antigo_conv > atual_conv:
        conv_diff_por = '{:.2f}'.format(((atual_conv / antigo_conv)-1)*100)
        conv_diff_qtde = '- {:.0f}'.format(antigo_conv - atual_conv)
        condicao_conv = 'tiveram uma diminuição (⏬)'
    else:
        conv_diff_qtde = 0
        conv_diff_por = 0
        condicao_conv = "manteve"

    # IMPRESSOES
    atual_imp = atual_primeiro_cliques.impressoes  
    antigo_imp = antigo_campanha_cliques.impressoes

    if atual_imp > antigo_imp:
        imp_diff_por = '{:.2f}'.format(((atual_imp / antigo_imp)-1)*100)
        imp_diff_qtde = '{:.0f}'.format(atual_imp - antigo_imp)
        condicao_imp = 'tiveram um aumento (⏫)'
    elif antigo_imp > atual_imp:
        imp_diff_por = '{:.2f}'.format(((atual_imp / antigo_imp)-1)*100)
        imp_diff_qtde = '- {:.0f}'.format(antigo_imp - atual_imp)
        condicao_imp = 'tiveram uma diminuição (⏬)'
    else:
        imp_diff_por = 0
        imp_diff_qtde = 0
        condicao_imp = "manteve"

    json_resp = {
        'conta_selecionada' : conta_selecionada,
        'data_atual' : data_atual,
        'data_antiga' : data_antiga,
        'ctr' : {
            'ctr_antigo' : ctr_antigo,
            'ctr_atual' : ctr_atual,
            'ctr_diff' : ctr_diff,
            'condicao_ctr' : condicao_ctr
        },
        'cliques' : {
            'nome_campanha' : nome_campanha,
            'condicao_cliques' : condicao_clique,
            'cliques_diff' : cliques_diff
        },
        'conv' : {
            'nome_campanha' : nome_campanha,
            'condicao_conv' : condicao_conv,
            'conv_diff_por' : conv_diff_por,
            'conv_diff_qtde' : conv_diff_qtde
        },
        'imp' : {
            'condicao_imp' : condicao_imp,
            'imp_diff_por' : imp_diff_por,
            'imp_diff_qtde' : imp_diff_qtde
        }
        
    }
    user = dict(session)
    return render_template('analise_diaria.html',user=user,
                                                 json_resp=json_resp)


app.run(debug=True)