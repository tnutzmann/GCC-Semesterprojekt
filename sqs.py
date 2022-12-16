import boto3

session = boto3.session.Session(aws_access_key_id='',
                                aws_secret_access_key='',
                                aws_session_token=''
                                )
sqs = session.client('sqs', region_name='us-east-1')
r = sqs.send_message(
    QueueUrl='https://sqs.us-east-1.amazonaws.com/790933937313/xmas2022',
    MessageBody=('Versuch 2 - 16.12.2022 - 10:03'),
    MessageAttributes={'MatNr':
                          {'DataType': 'String',
                           'StringValue': '20224463'},
                      'StudentName':
                          {'DataType': 'String',
                           'StringValue': 'Tony Nutzmann'},
                      'Email-Adresse':
                          {'DataType': 'String',
                           'StringValue': 'nutzmann@th-brandenburg.de'},
                      'ReplyURL':
                          {'DataType': 'String',
                           'StringValue': 'https://sqs.us-east-1.amazonaws.com/567270253559/ESA-SQS'},
                      }
)

print(r)
