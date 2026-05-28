from http import HTTPStatus

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from team_finder.constants import SKILLS_SUGGESTIONS_LIMIT
from team_finder.services import get_page_obj, get_query_prefix

from .forms import LoginForm, ProfileForm, RegisterForm, UserPasswordChangeForm
from .models import Skill, User
from .services import get_or_create_skill, get_request_payload

JSON_ERROR_NOT_FOUND = "Object not found"
JSON_ERROR_FORBIDDEN = "Forbidden"


def register_view(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("users:login")
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        login(request, form.cleaned_data["user"])
        return redirect("projects:list")
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def user_detail(request, pk):
    profile_user = get_object_or_404(
        User.objects.prefetch_related("skills", "owned_projects"), pk=pk
    )
    return render(request, "users/user-details.html", {"user": profile_user})


@login_required
def edit_profile(request):
    form = ProfileForm(
        request.POST or None, request.FILES or None, instance=request.user
    )
    if form.is_valid():
        form.save()
        return redirect("users:detail", pk=request.user.pk)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    form = UserPasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("users:detail", pk=request.user.pk)
    return render(request, "users/change_password.html", {"form": form})


def users_list(request):
    participants = User.objects.prefetch_related("skills").order_by("-id")
    active_skill = request.GET.get("skill")
    if active_skill:
        participants = participants.filter(skills__name=active_skill)
    page_obj = get_page_obj(request, participants.distinct())
    all_skills = Skill.objects.order_by("name").values_list("name", flat=True)
    query_prefix = get_query_prefix(request)
    return render(
        request,
        "users/participants.html",
        {
            "participants": participants,
            "page_obj": page_obj,
            "all_skills": all_skills,
            "active_skill": active_skill,
            "query_prefix": query_prefix,
        },
    )


@require_GET
def skills_search(request):
    query = request.GET.get("q", "").strip()
    skills = (
        Skill.objects.filter(name__istartswith=query).order_by("name")[
            :SKILLS_SUGGESTIONS_LIMIT
        ]
        if query
        else Skill.objects.none()
    )
    return JsonResponse(list(skills.values("id", "name")), safe=False)


@login_required
@require_POST
def add_skill(request, pk):
    profile_user = User.objects.filter(pk=pk).first()
    if profile_user is None:
        return JsonResponse(
            {"error": JSON_ERROR_NOT_FOUND}, status=HTTPStatus.NOT_FOUND
        )
    if profile_user.pk != request.user.pk:
        return JsonResponse(
            {"error": JSON_ERROR_FORBIDDEN}, status=HTTPStatus.FORBIDDEN
        )
    payload = get_request_payload(request)
    skill, created = get_or_create_skill(payload)
    if skill is None:
        if payload.get("skill_id"):
            return JsonResponse(
                {"error": JSON_ERROR_NOT_FOUND}, status=HTTPStatus.NOT_FOUND
            )
        return JsonResponse(
            {"error": "skill_id or name is required"}, status=HTTPStatus.BAD_REQUEST
        )
    before = profile_user.skills.filter(pk=skill.pk).exists()
    profile_user.skills.add(skill)
    return JsonResponse(
        {
            "id": skill.id,
            "name": skill.name,
            "skill_id": skill.id,
            "created": created,
            "added": not before,
        }
    )


@login_required
@require_POST
def remove_skill(request, pk, skill_id):
    profile_user = User.objects.filter(pk=pk).first()
    if profile_user is None:
        return JsonResponse(
            {"error": JSON_ERROR_NOT_FOUND}, status=HTTPStatus.NOT_FOUND
        )
    if profile_user.pk != request.user.pk:
        return JsonResponse(
            {"error": JSON_ERROR_FORBIDDEN}, status=HTTPStatus.FORBIDDEN
        )
    skill = Skill.objects.filter(pk=skill_id).first()
    if skill is None:
        return JsonResponse(
            {"error": JSON_ERROR_NOT_FOUND}, status=HTTPStatus.NOT_FOUND
        )
    if not profile_user.skills.filter(pk=skill.pk).exists():
        return JsonResponse(
            {"error": "skill is not attached"}, status=HTTPStatus.NOT_FOUND
        )
    profile_user.skills.remove(skill)
    return JsonResponse({"status": "ok"})
