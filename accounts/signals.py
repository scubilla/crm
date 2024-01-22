from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from .models import Customer

def customer_profile(sender, instance, created, **kwargs):
    if created:
        group = Group.objects.get(name='customer')
        # el usuario sera la instancia
        instance.groups.add(group)
        # agregamos en campo user al Customer segun el modelo y la relacion One to One
        Customer.objects.create(
            user=instance,
            name=instance.username,
            )
        print('Profile Created')

post_save.connect(customer_profile,sender=User)
