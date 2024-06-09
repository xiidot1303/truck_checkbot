from django.db import models

class Depot(models.Model):
    code = models.IntegerField(null=True, blank=False)
    title = models.CharField(null=True, blank=True, max_length=255)
    branch = models.CharField(null=True, blank=True, max_length=255)
    tg_id = models.CharField(null=True, blank=True, max_length=16)

class Car(models.Model):
    code = models.CharField(null=True, blank=False, max_length=64)
    title = models.CharField(null=True, blank=True, max_length=255)
    number = models.CharField(null=True, blank=True, max_length=64)
    tg_id = models.CharField(null=True, blank=True, max_length=16)