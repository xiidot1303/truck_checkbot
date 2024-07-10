from django.db import models
from django.utils import timezone
from asgiref.sync import sync_to_async

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
    is_complete = models.BooleanField(default=False)
    current_depot_index = models.PositiveIntegerField(default=0)

    @property
    @sync_to_async
    def get_next_depot(self):
        depot_relations = self.taskdepot_set.order_by('order')
        if self.current_depot_index < depot_relations.count():
            return depot_relations[self.current_depot_index].depot
        return None

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

class TaskEvent(models.Model):
    EVENT_TYPES = [
        ('arrive_to_factory', 'Водитель прибыл на завод'),
        ('in_factory', 'На заводе'),
        ('arrive_to_depot', 'Водитель прибыл на склад'),
        ('in_depot', 'В складе'),
    ]

    task = models.ForeignKey(Task, related_name='events', on_delete=models.CASCADE, verbose_name="Задание")
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, verbose_name="Тип")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="Время начала") 
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="Конечное время")
    depot = models.ForeignKey(Depot, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Склад")

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"