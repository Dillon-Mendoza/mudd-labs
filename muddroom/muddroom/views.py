from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def hub(request):
    return render(request, 'muddroom/hub.html')