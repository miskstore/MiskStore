from django.db.models.signals import pre_save,post_save,pre_delete,post_delete
from django.core.mail import send_mail
import threading
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django_rest_passwordreset.signals import reset_password_token_created
import os
from .models import Order
from .utils import send_telegram_notification

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
    reset_password_url = "https://copymisk-ccax.vercel.app/ar/reset-password?token={}".format(
        reset_password_token.key
    )
    
    email_message = "اضغط هنا لإعادة تعيين كلمة المرور الخاصة بك: {}".format(reset_password_url)
    
    # Send email in background thread
    EmailThread(
        subject="اعاده تعيين كلمة مرور موقع مسك",
        message=email_message,
        from_email=os.environ.get('EMAIL_HOST_USER'),
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

# @receiver(post_save, sender=Order)
# def notify_admin_on_new_order(sender, instance, created, **kwargs):
#     if created: 
#         total = instance.total_price
        
#         try:
#             payment = instance.payment.method
#         except Exception:
#             payment = "N/A"
            
#         # customer_info = instance.customer.full_name or instance.customer.email if hasattr(instance, 'customer') and instance.customer else 'Guest'
#         # customer_number = instance.customer.phone_number if hasattr(instance, 'customer') and instance.customer else 'N/A'
#         # customer_address = instance.customer.address if hasattr(instance, 'customer') and instance.customer else 'N/A'
#         order_full_name =    instance.full_name
#         order_phone_number = instance.phone_number
#         order_full_address = instance.full_address
#         order_notes = instance.order_notes
#         order_id = instance.id
        
#         message = (
#             f"🚨 <b>NEW ORDER RECEIVED!</b> 🚨\n\n"
#             f"🛒 <b>Order ID(رقم الطلب):</b> #{order_id}\n"
#             f"👤 <b>Customer(العميل):</b> {order_full_name}\n"
#             f"👤 <b>Customer Number(رقم العميل):</b> {order_phone_number}\n"
#             f"👤 <b>Customer Address(عنوان العميل):</b> {order_full_address}\n"
#             f"👤 <b>Order Notes(ملاحظات الطلب):</b> {order_notes}\n"
#             f"💵 <b>Total(المبلغ):</b> {total} EGP\n"
#             # f"💳 <b>Payment(طريقة الدفع):</b> {payment}\n\n"
#         )
        
#         send_telegram_notification(message)
