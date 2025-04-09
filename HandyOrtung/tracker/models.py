from django.db import models

class Lead(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    accuracy = models.FloatField(blank=True, null=True)
    user_agent = models.TextField()
    session_id = models.CharField(max_length=128)
    timestamp = models.DateTimeField(auto_now_add=True)
