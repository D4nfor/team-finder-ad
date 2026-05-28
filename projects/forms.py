from django import forms

from team_finder.forms import GithubUrlValidationMixin

from .models import Project


class ProjectForm(GithubUrlValidationMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "GitHub",
            "status": "Статус",
        }
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}
