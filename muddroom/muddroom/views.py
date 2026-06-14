from django.shortcuts import render
from .models import Service
from django.contrib.auth.decorators import login_required

def hub(request):
    services = Service.objects.filter(is_active=True)
    return render(request, 'muddroom/hub.html', {'services': services})