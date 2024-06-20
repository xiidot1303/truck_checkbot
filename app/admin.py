from django.contrib import admin
from app.models import *

class DepotAdmin(admin.ModelAdmin):
    list_display = ["title", "branch", "tg_id", "lat", "lon"]
    list_editable = ["title", "branch", "tg_id", "lat", "lon"]
    list_display_links = None

class CarAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]

class TaskDepotInline(admin.TabularInline):
    model = TaskDepot
    extra = 1  # Number of extra forms to display
    ordering = ['order']  # Order by 'order' field

class TaskEventInline(admin.TabularInline):
    model = TaskEvent
    extra = 0
    readonly_fields = ['event_type', 'start_time', 'end_time', 'spend_time', 'depot']

    def spend_time(self, obj):
        if obj.end_time and obj.start_time:
            delta = obj.end_time - obj.start_time
            minute = round(delta.seconds / 60, 2)
            return minute
        else:
            return ""

    spend_time.short_description = "Пройденное время (Минуты)"

class TaskAdmin(admin.ModelAdmin):
    list_display = ['driver', 'created_at']
    list_filter = ['driver']
    search_fields = ['driver']
    inlines = [TaskDepotInline, TaskEventInline]

    fieldsets = (
        ('', {
            'fields': ['driver'],
        }),
    )

admin.site.register(Depot, DepotAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(Task, TaskAdmin)
# admin.site.register(TaskDepot)
# admin.site.register(TaskEvent)