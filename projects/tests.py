from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from projects.models import Project
from users.models import Skill, User

ADD_SKILL_JSON = '{"name": "Django"}'
BACKEND_SURNAME = "Backend"
DEMO_DESCRIPTION = "Description"
DEMO_PROJECT_NAME = "Demo"
DJANGO_QUERY = "Dj"
DJANGO_SKILL = "Django"
FRONTEND_SURNAME = "Frontend"
IVAN_EMAIL = "ivan@example.com"
IVAN_NAME = "Ivan"
IVAN_PHONE = "+79990000002"
MARIA_EMAIL = "maria@yandex.ru"
MARIA_NAME = "Maria"
MARIA_PHONE = "+79990000001"
PASSWORD = "password"
UNKNOWN_PK = 999999

PROJECT_DETAIL_URL = "projects:detail"
PROJECT_LIST_URL = "projects:list"
TOGGLE_PARTICIPATE_URL = "projects:toggle_participate"
USERS_ADD_SKILL_URL = "users:add_skill"
USERS_LIST_URL = "users:list"
USERS_REMOVE_SKILL_URL = "users:remove_skill"
USERS_SKILLS_SEARCH_URL = "users:skills_search"

CONTENT_TYPE_JSON = "application/json"
FILTER_PARAM_SKILL = "skill"
HEADER_CONTENT_TYPE = "Content-Type"
SEARCH_PARAM_QUERY = "q"
JSON_KEY_ADDED = "added"
JSON_KEY_ERROR = "error"
JSON_KEY_NAME = "name"
JSON_KEY_PARTICIPANT = "participant"


class ProjectViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=MARIA_EMAIL,
            password=PASSWORD,
            name=MARIA_NAME,
            surname=BACKEND_SURNAME,
            phone=MARIA_PHONE,
        )
        self.project = Project.objects.create(
            name=DEMO_PROJECT_NAME,
            description=DEMO_DESCRIPTION,
            owner=self.user,
        )
        self.project.participants.add(self.user)

    def test_project_list_and_detail_are_public(self):
        self.assertEqual(
            self.client.get(reverse(PROJECT_LIST_URL)).status_code,
            HTTPStatus.OK,
        )
        self.assertEqual(
            self.client.get(
                reverse(PROJECT_DETAIL_URL, args=[self.project.pk])
            ).status_code,
            HTTPStatus.OK,
        )

    def test_authenticated_user_can_toggle_participation(self):
        other = User.objects.create_user(
            email=IVAN_EMAIL,
            password=PASSWORD,
            name=IVAN_NAME,
            surname=FRONTEND_SURNAME,
            phone=IVAN_PHONE,
        )
        self.client.force_login(other)
        response = self.client.post(
            reverse(TOGGLE_PARTICIPATE_URL, args=[self.project.pk])
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.json()[JSON_KEY_PARTICIPANT])
        self.assertTrue(self.project.participants.filter(pk=other.pk).exists())

    def test_toggle_participation_returns_json_for_unknown_project(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse(TOGGLE_PARTICIPATE_URL, args=[UNKNOWN_PK]))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response.headers[HEADER_CONTENT_TYPE], CONTENT_TYPE_JSON)
        self.assertIn(JSON_KEY_ERROR, response.json())


class UserSkillViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=MARIA_EMAIL,
            password=PASSWORD,
            name=MARIA_NAME,
            surname=BACKEND_SURNAME,
            phone=MARIA_PHONE,
        )

    def test_profile_owner_can_add_skill_and_filter_users(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse(USERS_ADD_SKILL_URL, args=[self.user.pk]),
            data=ADD_SKILL_JSON,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.json()[JSON_KEY_ADDED])
        response = self.client.get(
            reverse(USERS_LIST_URL), {FILTER_PARAM_SKILL: DJANGO_SKILL}
        )
        self.assertContains(response, MARIA_NAME)

    def test_skill_search_returns_prefix_matches(self):
        Skill.objects.create(name=DJANGO_SKILL)
        response = self.client.get(
            reverse(USERS_SKILLS_SEARCH_URL), {SEARCH_PARAM_QUERY: DJANGO_QUERY}
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json()[0][JSON_KEY_NAME], DJANGO_SKILL)

    def test_remove_skill_returns_json_for_unknown_skill(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse(USERS_REMOVE_SKILL_URL, args=[self.user.pk, UNKNOWN_PK])
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response.headers[HEADER_CONTENT_TYPE], CONTENT_TYPE_JSON)
        self.assertIn(JSON_KEY_ERROR, response.json())
