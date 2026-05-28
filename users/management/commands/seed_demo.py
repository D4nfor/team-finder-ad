from django.core.management.base import BaseCommand

from projects.models import Project
from users.models import Skill, User


class Command(BaseCommand):
    help = "Create demo users, skills, and projects for manual review."

    def handle(self, *args, **options):
        rows = [
            ("maria@yandex.ru", "Maria", "Backend", "+79990000001", ["Django", "PostgreSQL"]),
            ("ivan@example.com", "Ivan", "Frontend", "+79990000002", ["JavaScript", "React"]),
            ("olga@example.com", "Olga", "Designer", "+79990000003", ["Figma", "UX"]),
        ]
        for email, name, surname, phone, skill_names in rows:
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={"name": name, "surname": surname, "phone": phone, "about": "TeamFinder demo account"},
            )
            user.set_password("password")
            user.save()
            for skill_name in skill_names:
                skill, _ = Skill.objects.get_or_create(name=skill_name)
                user.skills.add(skill)
            project, _ = Project.objects.get_or_create(
                name=f"{name}'s pet project",
                owner=user,
                defaults={
                    "description": "Demo project for TeamFinder review.",
                    "github_url": "https://github.com/D4nfor/team-finder-ad",
                    "status": Project.STATUS_OPEN,
                },
            )
            project.participants.add(user)
        self.stdout.write(self.style.SUCCESS("Demo data created. Password for all demo users: password"))
