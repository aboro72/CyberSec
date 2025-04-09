from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Lead
import json

@csrf_exempt
def collect_location(request):
    if request.method == "POST":
        data = json.loads(request.body)
        Lead.objects.create(
            name=data.get("name"),
            email=data.get("email"),
            phone=data.get("phone"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            accuracy=data.get("accuracy"),
            user_agent=data.get("userAgent"),
            session_id=data.get("sessionId", "unknown")
        )
        return JsonResponse({"status": "success"})
