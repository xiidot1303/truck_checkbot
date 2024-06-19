from app.services.one_c_service import get_cars_list, get_depots_list
from app.services.car_service import *
from app.services.depot_service import *
from django.db import transaction

def update_cars():
    data = get_cars_list()
    codes = [item['code'] for item in data]
    existing_cars = filter_cars_by_codes(codes)
    existing_cars_dict = {car.code: car for car in existing_cars}

    cars_to_create = []
    cars_to_update = []

    for item in data:
        code = item['code']
        if code in existing_cars_dict:
            car = existing_cars_dict[code]
            car.title = item['title']
            car.number = item['number']
            # car.tg_id = item['tg_id']
            cars_to_update.append(car)
        else:
            cars_to_create.append(Car(**item))

    # update db
    car_transactional_update_or_create(cars_to_create, cars_to_update)

def update_depots():
    data = get_depots_list()
    codes = [item['code'] for item in data]
    existing_depots = filter_depots_by_codes(codes)
    existing_depots_dict = {depot.code: depot for depot in existing_depots}

    depots_to_create = []
    depots_to_update = []

    for item in data:
        code = item['code']
        if code in existing_depots_dict:
            depot = existing_depots_dict[code]
            depot.title = item['title']
            depot.branch = item['branch']
            depot.tg_id = item['tg_id']
            depot.lat = item['lat']
            depot.lon = item['lon']
            depots_to_update.append(depot)
        else:
            depots_to_create.append(Depot(**item))

    # update db
    depot_transactional_update_or_create(depots_to_create, depots_to_update)