from io import BytesIO

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse
from PIL import ImageFont

from team_finder.constants import (
    ABOUT_MAX_LENGTH,
    AVATAR_COLORS,
    AVATAR_CONTENT_RATIO,
    AVATAR_FONT_RATIO,
    AVATAR_FORMAT,
    AVATAR_MODE,
    AVATAR_SIZE,
    AVATAR_TEXT_FILL,
    DEFAULT_AVATAR_LETTER,
    MIN_FONT_SIZE,
    PHONE_MAX_LENGTH,
    SKILL_NAME_MAX_LENGTH,
    USER_NAME_MAX_LENGTH,
)


class Skill(models.Model):
    name = models.CharField(max_length=SKILL_NAME_MAX_LENGTH, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"{reverse('users:list')}?skill={self.name}"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


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
            self.avatar.save(self._avatar_filename(), self._build_avatar(), save=False)
        super().save(*args, **kwargs)

    def _avatar_filename(self):
        base = self.email.split("@", 1)[0] if self.email else "user"
        return f"{base}_avatar.png"

    def _build_avatar(self):
        from PIL import Image, ImageDraw

        color = AVATAR_COLORS[sum(ord(ch) for ch in self.email or self.name) % len(AVATAR_COLORS)]
        image = Image.new(AVATAR_MODE, (AVATAR_SIZE, AVATAR_SIZE), color)
        draw = ImageDraw.Draw(image)
        letter = (self.name[:1] or self.email[:1] or DEFAULT_AVATAR_LETTER).upper()
        font_size = _fit_font_size(draw, letter, AVATAR_SIZE)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except OSError:
            font = ImageFont.load_default()
        box = draw.textbbox((0, 0), letter, font=font)
        x = (AVATAR_SIZE - (box[2] - box[0])) / 2 - box[0]
        y = (AVATAR_SIZE - (box[3] - box[1])) / 2 - box[1]
        draw.text((x, y), letter, fill=AVATAR_TEXT_FILL, font=font)
        buffer = BytesIO()
        image.save(buffer, format=AVATAR_FORMAT)
        return ContentFile(buffer.getvalue())


def _fit_font_size(draw, letter, canvas_size):
    font_size = int(canvas_size * AVATAR_FONT_RATIO)
    while font_size > MIN_FONT_SIZE:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except OSError:
            return font_size
        box = draw.textbbox((0, 0), letter, font=font)
        if (
            (box[2] - box[0]) <= canvas_size * AVATAR_CONTENT_RATIO
            and (box[3] - box[1]) <= canvas_size * AVATAR_CONTENT_RATIO
        ):
            return font_size
        font_size -= 1
    return font_size
