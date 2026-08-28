from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Account, Level, Student, Teacher, UserType

User = get_user_model()


def make_account(name, domain):
    return Account.objects.create(name=name, domain_url=domain)


def make_teacher(account, email, **extra):
    return Teacher.objects.create_user(
        email=email, password='sup3r-s3cret-pw', account=account, **extra
    )


class UserModelTests(TestCase):
    def setUp(self):
        self.account = make_account('Alpha School', 'alpha.example.com')

    def test_password_is_hashed(self):
        user = make_teacher(self.account, 'teacher@alpha.example.com')
        self.assertNotEqual(user.password, 'sup3r-s3cret-pw')
        self.assertTrue(user.check_password('sup3r-s3cret-pw'))

    def test_role_proxy_stamps_user_type_and_filters_queryset(self):
        teacher = make_teacher(self.account, 'teacher@alpha.example.com')
        student = Student.objects.create_user(
            email='student@alpha.example.com', password='sup3r-s3cret-pw', account=self.account,
        )
        self.assertEqual(teacher.user_type, UserType.TEACHER)
        self.assertEqual(student.user_type, UserType.STUDENT)
        self.assertQuerySetEqual(Teacher.objects.all(), [teacher])
        self.assertQuerySetEqual(Student.objects.all(), [student])
        self.assertEqual(User.objects.count(), 2)

    def test_superuser_may_exist_without_an_account(self):
        admin = User.objects.create_superuser(email='root@example.com', password='sup3r-s3cret-pw')
        self.assertIsNone(admin.account_id)
        self.assertTrue(admin.is_staff and admin.is_superuser)


class TenantIsolationTests(APITestCase):
    """The whole point of the multi-tenant setup: no cross-school reads."""

    def setUp(self):
        self.alpha = make_account('Alpha School', 'alpha.example.com')
        self.beta = make_account('Beta School', 'beta.example.com')
        self.alpha_teacher = make_teacher(self.alpha, 'teacher@alpha.example.com')
        self.beta_student = Student.objects.create_user(
            email='student@beta.example.com', password='sup3r-s3cret-pw', account=self.beta,
        )
        self.beta_level = Level.objects.create(
            account=self.beta, name='P1', school_class='PRIMARY_ONE',
        )
        self.client.force_authenticate(self.alpha_teacher)

    def test_list_excludes_other_tenants(self):
        response = self.client.get(reverse('users:student-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])

    def test_detail_of_other_tenant_is_not_found(self):
        response = self.client.get(
            reverse('users:student-detail', args=[self.beta_student.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_account_list_only_contains_own_school(self):
        response = self.client.get(reverse('users:account-list'))
        self.assertEqual([row['name'] for row in response.data['results']], ['Alpha School'])

    def test_level_of_other_tenant_is_not_found(self):
        response = self.client.get(reverse('users:level-detail', args=[self.beta_level.pk]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_created_user_is_assigned_to_the_requesting_tenant(self):
        response = self.client.post(
            reverse('users:student-list'),
            {'email': 'new@alpha.example.com', 'password': 'sup3r-s3cret-pw'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        created = Student.objects.get(email='new@alpha.example.com')
        self.assertEqual(created.account_id, self.alpha.pk)


class UserApiSecurityTests(APITestCase):
    def setUp(self):
        self.account = make_account('Alpha School', 'alpha.example.com')
        self.teacher = make_teacher(self.account, 'teacher@alpha.example.com')
        self.client.force_authenticate(self.teacher)

    def test_password_hash_is_never_serialized(self):
        response = self.client.get(reverse('users:user-list'))
        self.assertNotIn('password', response.data['results'][0])

    def test_privilege_escalation_via_the_api_is_ignored(self):
        response = self.client.patch(
            reverse('users:user-detail', args=[self.teacher.pk]),
            {'is_superuser': True, 'is_staff': True},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.teacher.refresh_from_db()
        self.assertFalse(self.teacher.is_superuser)
        self.assertFalse(self.teacher.is_staff)

    def test_account_reassignment_via_the_api_is_ignored(self):
        other = make_account('Beta School', 'beta.example.com')
        self.client.patch(
            reverse('users:user-detail', args=[self.teacher.pk]), {'account': str(other.pk)},
        )
        self.teacher.refresh_from_db()
        self.assertEqual(self.teacher.account_id, self.account.pk)

    def test_anonymous_access_is_rejected(self):
        self.client.force_authenticate(None)
        response = self.client.get(reverse('users:user-list'))
        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_students_may_not_write(self):
        student = Student.objects.create_user(
            email='student@alpha.example.com', password='sup3r-s3cret-pw', account=self.account,
        )
        self.client.force_authenticate(student)
        response = self.client.post(
            reverse('users:student-list'),
            {'email': 'intruder@alpha.example.com', 'password': 'sup3r-s3cret-pw'},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_groups_are_superuser_only(self):
        response = self.client.get(reverse('users:group-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
