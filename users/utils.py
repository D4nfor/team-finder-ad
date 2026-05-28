import re
from io import BytesIO

from django import forms
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from team_finder.constants import (
    AVATAR_COLORS,
    AVATAR_CONTENT_RATIO,
    AVATAR_FONT_RATIO,
    AVATAR_FORMAT,
    AVATAR_MODE,
    AVATAR_SIZE,
    AVATAR_TEXT_FILL,
    DEFAULT_AVATAR_LETTER,
    MIN_FONT_SIZE,
)


def clean_phone(phone, user_model, instance_pk=None):
    phone = phone.strip()
    if not phone:
        return phone
    if not re.fullmatch(r"(8|\+7)\d{10}", phone):
        raise forms.ValidationError(
            "Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
        )
    normalized = "+7" + phone[1:] if phone.startswith("8") else phone
    duplicates = user_model.objects.exclude(pk=instance_pk).filter(
        phone__in=[normalized, "8" + normalized[2:]]
    )
    if duplicates.exists():
        raise forms.ValidationError("Такой номер телефона уже используется")
    return normalized


def build_avatar(name, email):
    color = AVATAR_COLORS[sum(ord(ch) for ch in email or name) % len(AVATAR_COLORS)]
    image = Image.new(AVATAR_MODE, (AVATAR_SIZE, AVATAR_SIZE), color)
    draw = ImageDraw.Draw(image)
    letter = (name[:1] or email[:1] or DEFAULT_AVATAR_LETTER).upper()
    font_size = fit_font_size(draw, letter, AVATAR_SIZE)
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


def fit_font_size(draw, letter, canvas_size):
    font_size = int(canvas_size * AVATAR_FONT_RATIO)
    while font_size > MIN_FONT_SIZE:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except OSError:
            return font_size
        box = draw.textbbox((0, 0), letter, font=font)
        if (box[2] - box[0]) <= canvas_size * AVATAR_CONTENT_RATIO and (
            box[3] - box[1]
        ) <= canvas_size * AVATAR_CONTENT_RATIO:
            return font_size
        font_size -= 1
    return font_size
