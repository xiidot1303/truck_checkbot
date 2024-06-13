from django.db import models
from django.utils import timezone
from asgiref.sync import sync_to_async

class Depot(models.Model):
    code = models.IntegerField(null=True, blank=False)
    title = models.CharField(null=True, blank=True, max_length=255)
    branch = models.CharField(null=True, blank=True, max_length=255)
    tg_id = models.CharField(null=True, blank=True, max_length=16)
    bot_user = models.OneToOneField('bot.DepotManager', null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"{self.branch} | {self.title}"

class Car(models.Model):
    code = models.CharField(null=True, blank=False, max_length=64)
    title = models.CharField(null=True, blank=True, max_length=255)
    number = models.CharField(null=True, blank=True, max_length=64)
    tg_id = models.CharField(null=True, blank=True, max_length=16)
    bot_user = models.OneToOneField('bot.Driver', null=True, blank=True, on_delete=models.PROTECT)

class Task(models.Model):
    driver = models.ForeignKey('bot.Driver', on_delete=models.CASCADE)
    depots = models.ManyToManyField(Depot, through='TaskDepot')
    created_at = models.DateTimeField(auto_now_add=True)
    is_complete = models.BooleanField(default=False)
    current_depot_index = models.PositiveIntegerField(default=0)

    @property
    @sync_to_async
    def get_next_depot(self):
        depot_relations = self.taskdepot_set.order_by('order')
        if self.current_depot_index < depot_relations.count():
            return depot_relations[self.current_depot_index].depot
        return None

class TaskDepot(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    depot = models.ForeignKey(Depot, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ('task', 'depot')

class TaskEvent(models.Model):
    EVENT_TYPES = [
        ('arrive_to_factory', 'Arrive to factory'),
        ('in_factory', 'In Factory'),
        ('arrive_to_depot', 'Arrive to Depot'),
        ('in_depot', 'In Depot'),
    ]

    task = models.ForeignKey(Task, related_name='events', on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    start_time = models.DateTimeField(null=True, blank=True) 
    end_time = models.DateTimeField(null=True, blank=True)
    depot = models.ForeignKey(Depot, null=True, blank=True, on_delete=models.CASCADE)
