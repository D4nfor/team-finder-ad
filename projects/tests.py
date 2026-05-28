from django.test import TestCase
from django.urls import reverse

from projects.models import Project
from users.models import Skill, User


class ProjectViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="maria@yandex.ru",
            password="password",
            name="Maria",
            surname="Backend",
            phone="+79990000001",
        )
        self.project = Project.objects.create(name="Demo", description="Description", owner=self.user)
        self.project.participants.add(self.user)

    def test_project_list_and_detail_are_public(self):
        self.assertEqual(self.client.get(reverse("projects:list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("projects:detail", args=[self.project.pk])).status_code, 200)

    def test_authenticated_user_can_toggle_participation(self):
        other = User.objects.create_user(
            email="ivan@example.com",
            password="password",
            name="Ivan",
            surname="Frontend",
            phone="+79990000002",
        )
        self.client.force_login(other)
        response = self.client.post(reverse("projects:toggle_participate", args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["participant"])
        self.assertTrue(self.project.participants.filter(pk=other.pk).exists())


class UserSkillViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="maria@yandex.ru",
            password="password",
            name="Maria",
            surname="Backend",
            phone="+79990000001",
        )

    def test_profile_owner_can_add_skill_and_filter_users(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("users:add_skill", args=[self.user.pk]),
            data='{"name": "Django"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["added"])
        response = self.client.get(reverse("users:list"), {"skill": "Django"})
        self.assertContains(response, "Maria")

    def test_skill_search_returns_prefix_matches(self):
        Skill.objects.create(name="Django")
        response = self.client.get(reverse("users:skills_search"), {"q": "Dj"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["name"], "Django")
