from django.contrib import admin
from app.models import *
from rangefilter.filters import DateRangeFilter

class DepotAdmin(admin.ModelAdmin):
    list_display = ["title", "branch", "tg_id", "lat", "lon"]
    list_editable = ["title", "branch", "tg_id", "lat", "lon"]
    search_fields = ['title']
    list_filter = ['branch']
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
    fields = ['event_type', 'start_time', 'end_time', 'spend_time', 'schedule_datetime', 'depot']
    readonly_fields = ['event_type', 'start_time', 'end_time', 'spend_time', 'schedule_datetime', 'depot']

    def spend_time(self, obj):
        if obj.end_time and obj.start_time:
            delta = obj.end_time - obj.start_time
            minute = round(delta.seconds / 60, 2)
            return minute
        else:
            return ""

    spend_time.short_description = "Пройденное время (Минуты)"

class TaskAdmin(admin.ModelAdmin):
    change_list_template = 'admin/task/task_change_list.html'
    list_display = ['driver', 'depot', 'car', 'created_at', 'is_complete']
    list_filter = ['driver', 'car', ('created_at', DateRangeFilter)]
    # search_fields = ['driver', 'car']
    inlines = [TaskDepotInline, TaskEventInline]

    def depot(self, obj):
        t = ""
        for depot in obj.depots.all():
            t += f"{depot.title}, "
        return t
    depot.short_description = "Адрес"
    fieldsets = (
        ('', {
            'fields': ['driver', 'car'],
        }),
    )

    def changelist_view(self, request, extra_context=None):
        # Add the URL parameters to the context
        if extra_context is None:
            extra_context = {}
        extra_context['created_at__range__gte'] = request.GET.get('created_at__range__gte', None)
        extra_context['created_at__range__lte'] = request.GET.get('created_at__range__lte', None)
        return super().changelist_view(request, extra_context=extra_context)

class EvenDurationNormAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]

class TaskScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'depot', 'arrive_to_factory_time', 'in_factory_time', 
        'arrive_to_depot_time', 'in_depot_time', 'weekday'
        ]
    list_filter = ['depot', 'weekday']

    fieldsets = (
        (None, {
            'fields': (
                ('depot'),
                ('arrive_to_factory_time', 'arrive_to_factory_time_add_day'), 
                ('in_factory_time', 'in_factory_time_add_day'),
                ('arrive_to_depot_time', 'arrive_to_depot_time_add_day'),
                ('in_depot_time', 'in_depot_time_add_day'),
                ('weekday'),
                )
        }),
    )

admin.site.register(Depot, DepotAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(EvenDurationNorm, EvenDurationNormAdmin)
admin.site.register(TaskSchedule, TaskScheduleAdmin)

# admin.site.register(TaskDepot)
# admin.site.register(TaskEvent)