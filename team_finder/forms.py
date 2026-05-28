from urllib.parse import urlparse

from django import forms

from .constants import GITHUB_HOSTS


class GithubUrlValidationMixin:
    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "").strip()
        if not url:
            return url
        host = urlparse(url).netloc.lower()
        if host not in GITHUB_HOSTS:
            raise forms.ValidationError("Ссылка должна вести на GitHub")
        return url
