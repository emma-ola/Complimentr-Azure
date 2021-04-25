import os
import boto3
from twilio.rest import Client
from flask import (
    Flask,
    flash, 
    render_template, 
    redirect,
    request,
    url_for,
)

app = Flask(__name__)
app.secret_key = "ssssh don't tell anyone"

ssm = boto3.client(
    'ssm',
    region_name='us-west-2',
    aws_access_key_id=os.environ['ACCESS_KEY'],
    aws_secret_access_key=os.environ['SECRET_KEY']
)

ssm_response = ssm.get_parameters(
    Names=['/Complimentr/TWILIO_ACCOUNT_SID', '/Complimentr/TWILIO_AUTH_TOKEN', '/Complimentr/TWILIO_PHONE_NUMBER']
)

TWILIO_ACCOUNT_SID = ssm_response['Parameters'][0]['Value']
TWILIO_AUTH_TOKEN = ssm_response['Parameters'][1]['Value']
TWILIO_PHONE_NUMBER = ssm_response['Parameters'][2]['Value']

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def get_sent_messages():
    messages = client.messages.list(from_=TWILIO_PHONE_NUMBER)
    return messages


def send_message(to, body):
    client.messages.create(
        to=to,
        body=body,
        from_=TWILIO_PHONE_NUMBER
    )


@app.route("/", methods=["GET"])
def index():
    messages = get_sent_messages()
    return render_template("index.html", messages=messages)


@app.route("/add-compliment", methods=["POST"])
def add_compliment():
    sender = request.values.get('sender', 'Someone')
    receiver = request.values.get('receiver', 'Someone')
    compliment = request.values.get('compliment', 'wonderful')
    to = request.values.get('to')
    body = f'{sender} says: {receiver} is {compliment}. See more compliments at {request.url_root}'
    send_message(to, body)
    flash('Your message was successfully sent')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
