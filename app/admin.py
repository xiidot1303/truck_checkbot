from django.contrib import admin
from app.models import *

class DepotAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]

class CarAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]

admin.site.register(Depot, DepotAdmin)
admin.site.register(Car, CarAdmin)