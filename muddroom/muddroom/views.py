from django.shortcuts import render
from .models import Service, Device
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.auth.decorators import login_required

@csrf_exempt
@require_POST
def webhook_receiver(request):
    try:
        n8n_parse = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    for parsed in n8n_parse:
        device_status = parsed.get('status')
        device_name = parsed.get('device')
        device_ip = parsed.get('ip')

        try:
            device = Device.objects.get(name=device_name)
            if device_status == "CONFIRMED":
                device.is_reachable = True
            else:
                device.is_reachable = False
        except Device.DoesNotExist:
            continue
        device.last_checked = timezone.now()
        device.save()

    return JsonResponse({'status': 'ok'})

@csrf_exempt
@require_POST
def service_webhook(request):
    try:
        service_n8n = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    for parsed in service_n8n:
        service_name = parsed.get('name')
        service_active = parsed.get('status')
        service_last_checked = parsed.get('last_checked')

        try:
            service = Service.objects.get(name=service_name)
            if service_active == "CONFIRMED":
                service.port_reachable = True
            else:
                service.port_reachable = False
        except Service.DoesNotExist:
            continue
        service.last_checked = timezone.now()
        service.save()
    
    return JsonResponse({'status': 'ok'})

@login_required
def hub(request):
    services = Service.objects.filter(is_active=True, port_reachable=True)
    devices = Device.objects.all()

    hub = {
        'services': services,
        'devices': devices
    }
    return render(request, 'muddroom/hub.html', hub)