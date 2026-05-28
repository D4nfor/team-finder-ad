from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.urls import reverse

from team_finder.constants import (
    ABOUT_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    SKILL_NAME_MAX_LENGTH,
    USER_NAME_MAX_LENGTH,
)
from users.managers import UserManager
from users.utils import build_avatar


class Skill(models.Model):
    name = models.CharField(max_length=SKILL_NAME_MAX_LENGTH, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"{reverse('users:list')}?skill={self.name}"


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    phone = models.CharField(max_length=PHONE_MAX_LENGTH, blank=True)
    github_url = models.URLField(blank=True)
    about = models.TextField(max_length=ABOUT_MAX_LENGTH, blank=True)
    skills = models.ManyToManyField(Skill, blank=True, related_name="users")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("name", "surname")

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return f"{self.name} {self.surname}".strip() or self.email

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar.save(
                self._avatar_filename(), build_avatar(self.name, self.email), save=False
            )
        super().save(*args, **kwargs)

    def _avatar_filename(self):
        base = self.email.split("@", 1)[0] if self.email else "user"
        return f"{base}_avatar.png"
