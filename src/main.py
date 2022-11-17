#!/usr/bin/python3
from bottle import route, run, template


@route('/')
def home():
    return template('home.tpl', name='BottleTube Home', content='Bla')


@route('/home2')
def home():
    return template('base.tpl', title='BottleTube Home', content='Bla')


@route('/hello')
def index():
    return '<b>Hello world</b>!'


# Start server
run(host='localhost', port=8080)
