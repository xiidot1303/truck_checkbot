from django.urls import path, re_path
from bot.views import botwebhook
from config import DRIVERBOT_API_TOKEN, DEPOT_MANAGERBOT_API_TOKEN

urlpatterns = [
    path(DRIVERBOT_API_TOKEN, botwebhook.DriverBotWebhookView.as_view()),
    path(DEPOT_MANAGERBOT_API_TOKEN, botwebhook.DepotManagerBotWebhookView.as_view())
]