from django.shortcuts import render
from .models import Service, Device
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone

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

def hub(request):
    services = Service.objects.filter(is_active=True)
    devices = Device.objects.all()

    hub = {
        'services': services,
        'devices': devices
    }
    return render(request, 'muddroom/hub.html', hub)