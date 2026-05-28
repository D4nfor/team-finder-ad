from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from team_finder.services import get_page_obj

from .forms import ProjectForm
from .models import Project


def project_list(request):
    projects = Project.objects.select_related("owner").prefetch_related("participants").order_by("-created_at")
    page_obj = get_page_obj(request, projects)
    return render(request, "projects/project_list.html", {"projects": projects, "page_obj": page_obj, "query_prefix": ""})


def project_detail(request, pk):
    project = get_object_or_404(Project.objects.select_related("owner").prefetch_related("participants"), pk=pk)
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect("projects:detail", pk=project.pk)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.pk and not request.user.is_staff:
        return HttpResponseForbidden()
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        project = form.save()
        return redirect("projects:detail", pk=project.pk)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
@require_POST
def complete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.pk and not request.user.is_staff:
        return HttpResponseForbidden()
    if project.status == Project.STATUS_OPEN:
        project.status = Project.STATUS_CLOSED
        project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": project.status})


@login_required
@require_POST
def toggle_participate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id == request.user.pk:
        return JsonResponse({"status": "ok", "participant": True})
    if participant := project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)
    return JsonResponse({"status": "ok", "participant": not participant})
