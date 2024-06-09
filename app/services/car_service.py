from app.services import *
from asgiref.sync import sync_to_async
from app.models import Car
from django.db import transaction

def filter_cars_by_codes(codes):
    cars = Car.objects.filter(code__in=codes)
    return cars

def car_transactional_update_or_create(cars_to_create, cars_to_update):
    with transaction.atomic():
        if cars_to_create:
            Car.objects.bulk_create(cars_to_create)
        if cars_to_update:
            # Car.objects.bulk_update(cars_to_update, ['title', 'number', 'tg_id'])
            Car.objects.bulk_update(cars_to_update, ['title', 'number'])
