from flask import Flask, request, make_response, redirect, render_template, session, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

import os
import pandas as pd
import numpy as np
import joblib
import pickle


app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'SUPER SECRETO'
app.config['APP_FOLDER'] = 'model_files'

#todos = ['Comprar cafe', 'Enviar solicitud de compra', 'Entregar video a productor ']

class LoginForm(FlaskForm):  
    username = StringField('Su nombre', validators=[DataRequired()])   
    ScaledTimeAlive = StringField('ScaledTimeAlive', validators=[DataRequired()])
    RoundWinner = SelectField('RoundWinner', choices=[('SI', 'Si'), ('NO', 'No')], validators=[DataRequired()])
    TimeAlive = StringField('TimeAlive', validators=[DataRequired()])
    submit = SubmitField('Enviar')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', error=error)


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html', error=error)


@app.route('/')
def index():
    user_ip = request.remote_addr

    response = make_response(redirect('/hello'))
    session['user_ip'] = user_ip

    return response


@app.route('/hello', methods=['GET', 'POST'])
def hello():
    user_ip = session.get('user_ip')
    login_form = LoginForm()
    username = session.get('username')
    context = {
        'user_ip': user_ip,
        'login_form' : login_form,
        'username' : username
    }

    if login_form.validate_on_submit():
        username = login_form.username.data
        ScaledTimeAlive = login_form.ScaledTimeAlive.data
        RoundWinner = login_form.RoundWinner.data
        TimeAlive = login_form.TimeAlive.data

        session['username'] = username
        session['scaledtimealive'] = ScaledTimeAlive
        session['roundwinner'] = 1 if RoundWinner == 'SI' else 0
        session['timealive'] = TimeAlive

        flash('Datos recibidos con éxito!')
        #return redirect(url_for('index'))
        return redirect(url_for('prediction'))

    #return render_template('hello.html', **context)
    return render_template('hello.html', **context)

@app.route('/prediction')
def prediction():
    scaledtimealive = session['scaledtimealive']
    roundwinner = session['roundwinner']
    timealive = session['timealive']
    features_values = [scaledtimealive, roundwinner, timealive]
    path_predict = os.path.join(app.config['APP_FOLDER'], 
        'model.pkl')

    with open(path_predict,mode='rb') as f:  
        model = pickle.load(f)
    #data_predict = [scaledtimealive, roundwinner, timealive] # pd.DataFrame(np.array(features_values).reshape(1,-1))
    data_predict = pd.DataFrame(np.array(features_values).reshape(1,-1))
    data_predict.columns = ['ScaledTimeAlive', 'RoundWinner', 'TimeAlive']
    
    lpred = model.predict(np.array(data_predict).reshape(1,-1))[0]
    answer = ['No Sobrevive' if lpred==0 else 'Sobrevive']
    session['answer'] = answer
    return render_template('respuesta.html',
        answer = session['answer'], 
            feature_1 = scaledtimealive,
            feature_2 = roundwinner,
            feature_3 = timealive,
            label_round = ('SI ' if roundwinner == 1 else 'NO ') + 'gana la ronda',
            username = session['username'])    
