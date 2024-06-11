from django.db import models

class Depot(models.Model):
    code = models.IntegerField(null=True, blank=False)
    title = models.CharField(null=True, blank=True, max_length=255)
    branch = models.CharField(null=True, blank=True, max_length=255)
    tg_id = models.CharField(null=True, blank=True, max_length=16)
    bot_user = models.OneToOneField('bot.DepotManager', null=True, blank=True, on_delete=models.PROTECT)

class Car(models.Model):
    code = models.CharField(null=True, blank=False, max_length=64)
    title = models.CharField(null=True, blank=True, max_length=255)
    number = models.CharField(null=True, blank=True, max_length=64)
    tg_id = models.CharField(null=True, blank=True, max_length=16)
    bot_user = models.OneToOneField('bot.Driver', null=True, blank=True, on_delete=models.PROTECT)