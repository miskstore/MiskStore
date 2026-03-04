from django.db.models.signals import pre_save,post_save,pre_delete,post_delete
from django.core.mail import send_mail
import threading
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django_rest_passwordreset.signals import reset_password_token_created

class EmailThread(threading.Thread):
    def __init__(self, subject, message, from_email, recipient_list):
        self.subject = subject
        self.message = message
        self.from_email = from_email
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        try:
            send_mail(
                self.subject,
                self.message,
                self.from_email,
                self.recipient_list,
                fail_silently=False,
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send password reset email: {str(e)}")


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    reset_password_url = "https://novera-tau.vercel.app/reset-password?token={}".format(
        reset_password_token.key
    )
    
    email_message = "Click here to reset your password: {}".format(reset_password_url)
    
    # Send email in background thread
    EmailThread(
        subject="Password Reset for My Website",
        message=email_message,
        from_email="xtramarket9@gmail.com",
        recipient_list=[reset_password_token.user.email]
    ).start()

####################### Signals ########################

##### Commented cuz it takes so much time and slows the web #####


# @receiver(post_save,sender=User)
# def user_post_save_receiver(sender,instance,created,*args,**kwargs):
#     if created:
#         send_mail(
#     subject="Welcome!",
#     message=f"Hey {instance.username} Thank you for signing up in our e-commerce website",
#     from_email= settings.DEFAULT_FROM_EMAIL,
#     recipient_list=[instance.email],
#     fail_silently=True,
# )
#     else:
#         print("You account information has been updated")


# @receiver(post_save,sender=Order)
# def order_post_save_receiver(sender,instance,created,*args,**kwargs):
#     if created:
#         send_mail(
#     subject="Your Order",
#     message=f"Hello {instance.customer.username}, we wanted to inform you that your order has been placed successfully",
#     from_email=settings.DEFAULT_FROM_EMAIL,
#     recipient_list=[instance.customer.email],
#     fail_silently=True,
#     )
    
#     else:
#         if "status" in instance.get_dirty_fields():
#             if instance.status == 'shipped':
#                 message = f"Hello {instance.customer.username}, you order has been shipped and will be delivered soon.\nStay Tuned"
#             elif instance.status == 'delivered':
#                 message = f"Hello {instance.customer.username}, you order has been delivered to your place"
#             elif instance.status == 'cancelled':
#                 message = f"Hello {instance.customer.username}, you order has been been cancelled"
#             elif instance.status == 'pending':
#                 message = f"Hello {instance.customer.username}, you order is now pending"
#             elif instance.status == 'paid':
#                 message = f"Hello {instance.customer.username}, you order has been paid successfully"
#             else:
#                 return
        
#         else:
#             return 
        
#         send_mail(
#     subject="Your Order",
#     message=message,
#     from_email=settings.DEFAULT_FROM_EMAIL,
#     recipient_list=[instance.customer.email],
#     fail_silently=True,
# )
