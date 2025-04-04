from django.db import models
from django.core.validators import FileExtensionValidator

class Bot_user(models.Model):
    user_id = models.BigIntegerField(null=True)
    name = models.CharField(null=True, blank=True, max_length=256, default='', verbose_name='Имя')
    username = models.CharField(null=True, blank=True, max_length=256, verbose_name='username')
    firstname = models.CharField(null=True, blank=True, max_length=256, verbose_name='Никнейм')
    phone = models.CharField(null=True, blank=True, max_length=16, default='', verbose_name='Телефон')
    lang = models.CharField(null=True, blank=True, max_length=4, verbose_name='')
    date = models.DateTimeField(db_index=True, null=True, auto_now_add=True, blank=True, verbose_name='Дата регистрации')

    def __str__(self) -> str:
        try:
            return self.name + ' ' + str(self.phone)
        except:
            return super().__str__()

    class Meta:
        verbose_name = "Пользователь бота"
        verbose_name_plural = "Пользователи бота"
    
class Message(models.Model):
    bot_users = models.ManyToManyField('bot.Bot_user', blank=True, related_name='bot_users_list', verbose_name='Пользователи бота')
    text = models.TextField(null=True, blank=False, max_length=1024, verbose_name='Текст')
    photo = models.FileField(null=True, blank=True, upload_to="message/photo/", verbose_name='Фото',
        validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png','bmp','gif'])]
    )
    video = models.FileField(
        null=True, blank=True, upload_to="message/video/", verbose_name='Видео',
        validators=[FileExtensionValidator(allowed_extensions=['MOV','avi','mp4','webm','mkv'])]
        )
    file = models.FileField(null=True, blank=True, upload_to="message/file/", verbose_name='Файл')
    is_sent = models.BooleanField(default=False)
    date = models.DateTimeField(db_index=True, null=True, auto_now_add=True, blank=True, verbose_name='Дата')

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

class Driver(models.Model):
    user_id = models.BigIntegerField(null=True)
    name = models.CharField(null=True, blank=True, max_length=256, default='', verbose_name='Имя')
    username = models.CharField(null=True, blank=True, max_length=256, verbose_name='username')
    firstname = models.CharField(null=True, blank=True, max_length=256, verbose_name='Никнейм')
    LANG_CHOICES = [
        ("uz", "O'zbekcha"),
        ("ru", "Русский")
    ]
    lang = models.CharField(null=True, blank=True, max_length=4, verbose_name='Язык', choices=LANG_CHOICES, default='uz')
    date = models.DateTimeField(db_index=True, null=True, auto_now_add=True, blank=True, verbose_name='Дата регистрации')
    lat = models.CharField(null=True, blank=True, max_length=32)
    lon = models.CharField(null=True, blank=True, max_length=32)

    def __str__(self) -> str:
        try:
            return self.name
        except:
            return super().__str__()

    class Meta:
        verbose_name = "Водитель"
        verbose_name_plural = "Водители"

class DepotManager(models.Model):
    user_id = models.BigIntegerField(null=True)
    name = models.CharField(null=True, blank=True, max_length=256, default='', verbose_name='Имя')
    username = models.CharField(null=True, blank=True, max_length=256, verbose_name='username')
    firstname = models.CharField(null=True, blank=True, max_length=256, verbose_name='Никнейм')
    lang = models.CharField(null=True, blank=True, max_length=4, verbose_name='')
    date = models.DateTimeField(db_index=True, null=True, auto_now_add=True, blank=True, verbose_name='Дата регистрации')

    def __str__(self) -> str:
        try:
            return self.name + '|' + str(self.depot.title)
        except:
            return super().__str__()

    class Meta:
        verbose_name = "Менеджер склада"
        verbose_name_plural = "Менеджеры склада"

class Factory(models.Model):
    tg_id = models.BigIntegerField(null=True, blank=True)
    lat = models.CharField(null=True, blank=True, max_length=32)
    lon = models.CharField(null=True, blank=True, max_length=32)


    class Meta:
        verbose_name = "Заведующий складом"
        verbose_name_plural = "Заведующие складом"

class ReportGroup(models.Model):
    tg_id = models.BigIntegerField(null=True, blank=False, verbose_name="Отчет завершения")
    tg_id_2 = models.BigIntegerField(null=True, blank=False, verbose_name="Ежедневные отчеты")
    class Meta:
        verbose_name = "Группа для отчета"
        verbose_name_plural = "Группы для отчета"
