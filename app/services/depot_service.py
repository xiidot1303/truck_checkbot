from app.services import *
from asgiref.sync import sync_to_async
from app.models import Depot
from django.db import transaction

def filter_depots_by_codes(codes):
    depots = Depot.objects.filter(code__in = codes)
    return depots

def depot_transactional_update_or_create(depots_to_create, depots_to_update):
    with transaction.atomic():
        if depots_to_create:
            Depot.objects.bulk_create(depots_to_create)
        if depots_to_update:
            Depot.objects.bulk_update(depots_to_update, ['title', 'branch', 'tg_id'])
