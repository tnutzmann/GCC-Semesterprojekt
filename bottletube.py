#!/usr/bin/python3

import time
import os
import uuid
import requests
import psycopg2
import json

from bottle import route,post, get, put, delete, run, template, request, response, default_app
from boto3 import resource, session

HOSTNAME = requests.get('http://169.254.169.254/latest/meta-data/public-hostname').text
PORT = 80
BUCKET_NAME = 'tonys-bottletube-bucket'  # Replace with your bucket name
SAVE_PATH = '/tmp/images/'
secret_name = "RDS-Secrets"

@route('/home')
@route('/')
def home():
    # SQL Query goes here later, now dummy data only
    items = []
    cursor.execute('SELECT * FROM image_uploads ORDER BY id')
    for record in cursor.fetchall():
        items.append({'id': record[0], 'filename': record[1], 'category': record[2]})
    return template('home.tpl', name='BoTube Home', items=items)

@route('/healthcheck')
def healthcheck():
    return('Here is '+ HOSTNAME +' and I feel lucky')

@route('/upload', method='GET')
def do_upload_get():
    return template('upload.tpl', name='Upload Image')


@route('/upload', method='POST')
def do_upload_post():
    category = request.forms.get('category')
    upload = request.files.get('file_upload')

    # Check for errors
    error_messages = []
    if not upload:
        error_messages.append('Please upload a file.')
    if not category:
        error_messages.append('Please enter a category.')

    try:
        name, ext = os.path.splitext(upload.filename)
        if ext not in ('.png', '.jpg', '.jpeg'):
            error_messages.append('File Type not allowed.')
    except:
        error_messages.append('Unknown error.')

    if error_messages:
        return template('upload.tpl', name='Upload Image', error_messages=error_messages)

    # Save to SAVE_PATH directory
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)
    save_filename = f'{name}_{time.strftime("%Y%m%d-%H%M%S")}{ext}'
    with open(f'{SAVE_PATH}{save_filename}', 'wb') as open_file:
        open_file.write(upload.file.read())

    if ext == '.png':
        content_type = 'image/png'
    else:
        content_type = 'image/jpeg'

    # Upload to S3
    data = open(SAVE_PATH + save_filename, 'rb')
    s3_resource.Bucket(BUCKET_NAME).put_object(Key=f'user_uploads/{save_filename}',
                                               Body=data,
                                               Metadata={'Content-Type': content_type},
                                               ACL='public-read')

    # Write to DB
    cursor.execute(f"INSERT INTO image_uploads (url, category) VALUES ('user_uploads/{save_filename}', '{category}');")
    connection.commit()
    # some code has to go here later

    # Return template
    return template('upload_success.tpl', name='Upload Image')

# ------------------------------------------

@post('/api/pictures')
def creation_handler():
    try:
        try:
            request_data = request.json()
        except:
            raise ValueError

        if request_data is None:
            raise ValueError

        try:
            category = request_data['category']
            upload = request_data['file_upload']

            
            name, ext = os.path.splitext(upload.filename)
            if ext not in ('.png', '.jpg', '.jpeg'):
                raise TypeError

            if not os.path.exists(SAVE_PATH):
                os.makedirs(SAVE_PATH)
            save_filename = f'{name}_{time.strftime("%Y%m%d-%H%M%S")}{ext}'
            with open(f'{SAVE_PATH}{save_filename}', 'wb') as open_file:
                open_file.write(upload.file.read())

            if ext == '.png':
                content_type = 'image/png'
            else:
                content_type = 'image/jpeg'

            # Upload to S3
            data = open(SAVE_PATH + save_filename, 'rb')
            s3_resource.Bucket(BUCKET_NAME).put_object(Key=f'user_uploads/{save_filename}',Body=data,Metadata={'Content-Type': content_type},ACL='public-read')
            # Write to DB
            cursor.execute(f"INSERT INTO image_uploads (url, category) VALUES ('user_uploads/{save_filename}', '{category}');")
            connection.commit()
            id = connection.insert_id()


        except (TypeError, KeyError):
            raise ValueError

    except ValueError:
        response.status = 400
        return

    response.headers['Content-Type'] = 'application/json'
    return json.dumps({'id':id, 'category':category, 'filename':f'user_uploads/{save_filename}'})

@get('/api/pictures')
def listing_handler():
    pictures = []
    cursor.execute('SELECT * FROM image_uploads ORDER BY id')
    for record in cursor.fetchall():
        pictures.append({'id': record[0], 'filename': record[1], 'category': record[2]})
    return json.dumps(pictures)

@put('/api/pictures/<id>')
def update_handler(name):
    '''Handles name updates'''
    pass

@delete('/api/pictures/<id>')
def delete_handler(name):
    '''Handles name deletions'''
    pass

# ------------------------------------------

if True:
    sm_session = session.Session()
    client = sm_session.client(service_name='secretsmanager', region_name='us-east-1')

    secrets = json.loads(client.get_secret_value(SecretId=secret_name).get('SecretString'))

    connection = psycopg2.connect(user=secrets['User'], host=secrets['Host'], password=secrets['Password'],
                                  database=secrets['DBName'])

    cursor = connection.cursor()
    cursor.execute("SET SCHEMA 'bottle_tube';")
    connection.commit()

    # Connect to S3
    s3_resource = resource('s3', region_name='us-east-1')

    os.chdir(os.path.dirname(__file__))
    application = default_app()
