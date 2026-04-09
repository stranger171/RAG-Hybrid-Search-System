from django.urls import path
from .views import chat, reset_session, memory_status

urlpatterns = [
    path('chat/', chat),
    path('reset-session/', reset_session),
    path('memory-status/', memory_status),
]