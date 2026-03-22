from celery import Celery
from app.mail import mail, create_messsage
from asgiref.sync import async_to_sync

c_app = Celery("app")

c_app.config_from_object('app.config')

@c_app.task()
def send_email(recipients:list[str], subject:str, body:str):
        message = create_messsage(recipients=recipients, subject=subject, body=body)
        
        async_to_sync(mail.send_message)(message)
        print("Send Email")