#!/usr/bin/python3

import time
import os
import uuid

import requests

from bottle import route, run, template, request
from boto3 import resource

BUCKET_NAME = 'bottletube'  # Replace with your bucket name
SAVE_PATH = '/tmp/images/'


@route('/home')
@route('/')
def home():
    # SQL Query goes here later, now dummy data only
    items = ({'filename': 'user_uploads/camel.jpg',
              'category': 'Animals'
              },
             {'filename': 'user_uploads/cat.jpg',
              'category': 'Animals'
              },
             )
    return template('home.tpl', name='BoTube Home', items=items)


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
    # some code has to go here later

    # Return template
    return template('upload_success.tpl', name='Upload Image')


if __name__ == '__main__':
    # Connect to DB
    # some code has to go here

    # Connect to S3
    s3_resource = resource('s3', region_name='us-east-1')

    # Needs to be customized
    # run(host='your_public_dns_name',
    run(host='ec2-3-227-1-45.compute-1.amazonaws.com',
        port=80)
