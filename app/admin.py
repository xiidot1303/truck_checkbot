from django.contrib import admin
from app.models import *

class DepotAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]

class CarAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]

class TaskDepotInline(admin.TabularInline):
    model = TaskDepot
    extra = 1  # Number of extra forms to display
    ordering = ['order']  # Order by 'order' field

class TaskEventInline(admin.TabularInline):
    model = TaskEvent
    extra = 1

class TaskAdmin(admin.ModelAdmin):
    inlines = [TaskDepotInline, TaskEventInline]

admin.site.register(Depot, DepotAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskDepot)
admin.site.register(TaskEvent)