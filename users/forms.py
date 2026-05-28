import re

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

from team_finder.forms import GithubUrlValidationMixin

from .models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")
        labels = {"name": "Имя", "surname": "Фамилия", "email": "Email"}

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise forms.ValidationError("Неверный имейл или пароль")
            cleaned_data["user"] = user
        return cleaned_data


class ProfileForm(GithubUrlValidationMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "avatar": "Аватар",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "GitHub",
        }
        widgets = {"about": forms.Textarea(attrs={"rows": 4})}

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not phone:
            return phone
        if not re.fullmatch(r"(8|\+7)\d{10}", phone):
            raise forms.ValidationError("Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX")
        normalized = "+7" + phone[1:] if phone.startswith("8") else phone
        duplicates = User.objects.exclude(pk=self.instance.pk).filter(
            phone__in=[normalized, "8" + normalized[2:]]
        )
        if duplicates.exists():
            raise forms.ValidationError("Такой номер телефона уже используется")
        return normalized


class UserPasswordChangeForm(PasswordChangeForm):
    pass
