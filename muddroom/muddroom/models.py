from django.conf import settings
from django.db import models
from django.utils import timezone

class Service(models.Model):

    name = models.CharField(max_length=200)
    url = models.URLField()
    description = models.CharField(max_length=200)
    icon = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class Device(models.Model):

    name = models.CharField(max_length=200)
    tailscale_ip = models.GenericIPAddressField()
    is_reachable = models.BooleanField(default=True)
    last_checked = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.name