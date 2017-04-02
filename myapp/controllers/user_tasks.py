from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import EmailMessage
from datetime import datetime


@shared_task
def send_mail(token, email):
    email = EmailMessage('RisoGelato 인증 메일입니다.', 'https://192.168.1.214/user/complete/?token='+token, to=[email])
    email.send()
