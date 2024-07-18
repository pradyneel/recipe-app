# from django.template import Context
# from django.template.loader import render_to_string
# from django.core.mail import EmailMessage
# from django.conf import settings

# def send_signup_email():

#     # context = {
#     #     'name': name,
#     #     'email': email,
#     # }

#     email_subject = 'Thank you for signing up'
#     email_body = "Bro you have failed"

#     email = EmailMessage(
#         email_subject, email_body,
#         'pradyneel2@gmail.com', ['pradyneel@gmail.com'],
#     )

#     return email.send(fail_silently=False)