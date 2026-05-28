import json

from .models import Skill


def get_request_payload(request):
    if request.content_type == "application/json":
        try:
            return json.loads(request.body.decode() or "{}")
        except json.JSONDecodeError:
            return {}
    return request.POST


def get_or_create_skill(payload):
    skill_id = payload.get("skill_id")
    name = (payload.get("name") or "").strip()
    if skill_id:
        return Skill.objects.filter(pk=skill_id).first(), False
    if name:
        return Skill.objects.get_or_create(name=name)
    return None, False
