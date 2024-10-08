from django.db import models
from django.utils import timezone
from asgiref.sync import sync_to_async
from datetime import datetime, timedelta

class Depot(models.Model):
    code = models.IntegerField(null=True, blank=False)
    title = models.CharField(null=True, blank=True, max_length=255, verbose_name="Название")
    branch = models.CharField(null=True, blank=True, max_length=255, verbose_name="Регион")
    tg_id = models.CharField(null=True, blank=True, max_length=16)
    bot_user = models.OneToOneField('bot.DepotManager', null=True, blank=True, on_delete=models.PROTECT)
    lat = models.CharField(null=True, blank=True, max_length=32)
    lon = models.CharField(null=True, blank=True, max_length=32)

    def __str__(self) -> str:
        return f"{self.branch} | {self.title}"

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады"

class Car(models.Model):
    code = models.CharField(null=True, blank=False, max_length=64)
    title = models.CharField(null=True, blank=True, max_length=255)
    number = models.CharField(null=True, blank=True, max_length=64)
    tg_id = models.CharField(null=True, blank=True, max_length=16)

    def __str__(self) -> str:
        return f"{self.title} {self.number}"

class Task(models.Model):
    driver = models.ForeignKey('bot.Driver', on_delete=models.CASCADE, verbose_name="Водитель")
    car = models.ForeignKey('app.Car', null=True, on_delete=models.PROTECT, verbose_name="Машина")
    depots = models.ManyToManyField(Depot, through='TaskDepot')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
    is_complete = models.BooleanField(default=False, verbose_name="Завершено?")
    current_depot_index = models.PositiveIntegerField(default=0)

    @property
    @sync_to_async
    def get_next_depot(self):
        depot_relations = self.taskdepot_set.order_by('order')
        if self.current_depot_index < depot_relations.count():
            return depot_relations[self.current_depot_index].depot
        return None

    @property
    @sync_to_async
    def get_car(self):
        return f"{self.car}"

    @property
    @sync_to_async
    def get_driver(self):
        return f"{self.driver}"

    class Meta:
        verbose_name = "Задание"
        verbose_name_plural = "Задания"


class TaskDepot(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    depot = models.ForeignKey(Depot, on_delete=models.CASCADE, verbose_name="Склад")
    order = models.PositiveIntegerField(verbose_name="Порядок")

    class Meta:
        unique_together = ('task', 'depot')
        verbose_name = "Склад заданий"
        verbose_name_plural = "Склады заданий"

EVENT_TYPES = [
    ('arrive_to_factory', 'Водитель прибыл на завод'),
    ('in_factory', 'На заводе'),
    ('arrive_to_depot', 'Водитель прибыл на склад'),
    ('in_depot', 'В складе'),
]

class TaskEvent(models.Model):
    task = models.ForeignKey(Task, related_name='events', on_delete=models.CASCADE, verbose_name="Задание")
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, verbose_name="Тип")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="Время начала") 
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="Конечное время")
    depot = models.ForeignKey(Depot, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Склад")
    duration_norm = models.IntegerField(null=True, blank=True, verbose_name="Норма")
    schedule_time = models.TimeField(null=True, blank=True, verbose_name="Время по графику")

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"

    @property
    async def spend_time(self):
        obj = self
        if obj.end_time and obj.start_time:
            delta = obj.end_time - obj.start_time
            minute = round(delta.seconds / 60, 2)
            return minute
        else:
            return ""

    @property
    async def difference_with_norm(self):
        spend_time = await self.spend_time if await self.spend_time else 0
        duration_norm = self.duration_norm if self.duration_norm else 0
        difference = spend_time - duration_norm
        return difference

    @property
    async def difference_with_schedule(self):
        if self.end_time and self.schedule_time:
            end_time = self.end_time.time()
            end_datetime = datetime.combine(datetime.today(), end_time)
            schedule_datetime = datetime.combine(datetime.today(), self.schedule_time)
            difference = schedule_datetime - end_datetime
            difference: timedelta
            return round(difference.total_seconds() / 3600, 2)
        return 0
        
    @property
    @sync_to_async
    def get_depot(self):
        if self.depot:
            return self.depot
        else:
            return self.task.depots.filter().order_by('taskdepot__order').first()

class EvenDurationNorm(models.Model):
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, verbose_name="Тип")
    depot = models.ForeignKey(Depot, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Склад")
    duration = models.IntegerField(verbose_name="Длительность (Минут)")

    class Meta:
        unique_together = ("event_type", "depot")
        verbose_name = "Норма для события задачи"
        verbose_name_plural = "Норма для события задачи"

class TaskSchedule(models.Model):
    WEEKDAY_CHOICES = [
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье')
    ]
    depot = models.ForeignKey(Depot, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Склад")
    arrive_to_factory_time = models.TimeField(null=True, blank=False, verbose_name='Время прибытия водителя на завод')
    in_factory_time = models.TimeField(null=True, blank=False, verbose_name = 'Время окончания загрузки')
    arrive_to_depot_time = models.TimeField(null=True, blank=False, verbose_name='Время прибытия на склад')
    in_depot_time = models.TimeField(null=True, blank=False, verbose_name = 'Время окончания разгрузки')
    weekday = models.IntegerField(null=True, blank=False, choices=WEEKDAY_CHOICES, verbose_name='Будний день')

    class Meta:
        verbose_name = 'График водителей'
        verbose_name_plural = 'Графики водителей'
        unique_together = ("depot", "weekday")