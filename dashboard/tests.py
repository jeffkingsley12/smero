from django.test import TestCase
from django.urls import reverse

from finance.models import AcademicYear, FinanceCategory
from users.models import Account, CommonUser, Level, UserType

PASSWORD = 'l0ng-enough-passphrase'


class DashboardTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.school = Account.objects.create(name='Hill View', domain_url='hill.example.com')
        cls.other = Account.objects.create(name='Lakeside', domain_url='lake.example.com')
        cls.teacher = CommonUser.objects.create_user(
            email='teacher@hill.example.com',
            password=PASSWORD,
            account=cls.school,
            user_type=UserType.TEACHER,
        )
        cls.student = CommonUser.objects.create_user(
            email='student@hill.example.com',
            password=PASSWORD,
            account=cls.school,
            user_type=UserType.STUDENT,
        )
        cls.level = Level.objects.create(account=cls.school, name='P4', school_class='P4')
        cls.other_level = Level.objects.create(account=cls.other, name='P4', school_class='P4')
        cls.other_person = CommonUser.objects.create_user(
            email='rival@lake.example.com',
            password=PASSWORD,
            account=cls.other,
            user_type=UserType.STUDENT,
        )

    def login(self, user):
        self.client.force_login(user)


class AuthenticationTests(DashboardTestCase):
    def test_pages_require_login(self):
        for name in ['dashboard:home', 'dashboard:people', 'dashboard:levels']:
            response = self.client.get(reverse(name))
            self.assertRedirects(response, f'/accounts/login/?next={reverse(name)}')

    def test_login_page_renders(self):
        self.assertContains(self.client.get('/accounts/login/'), 'Sign in')


class PeoplePageTests(DashboardTestCase):
    def test_lists_only_this_school(self):
        self.login(self.teacher)
        response = self.client.get(reverse('dashboard:people'))
        self.assertContains(response, self.student.email)
        self.assertNotContains(response, self.other_person.email)

    def test_htmx_request_returns_only_the_rows(self):
        self.login(self.teacher)
        response = self.client.get(reverse('dashboard:people'), HTTP_HX_REQUEST='true')
        self.assertContains(response, 'people-rows')
        self.assertNotContains(response, '<nav>')

    def test_filters_by_role(self):
        self.login(self.teacher)
        response = self.client.get(
            reverse('dashboard:people'), {'user_type': UserType.STUDENT}, HTTP_HX_REQUEST='true',
        )
        self.assertContains(response, self.student.email)
        self.assertNotContains(response, self.teacher.email)

    def test_students_cannot_open_the_create_form(self):
        self.login(self.student)
        self.assertEqual(self.client.get(reverse('dashboard:person-create')).status_code, 403)

    def test_staff_can_create_a_person(self):
        self.login(self.teacher)
        response = self.client.post(
            reverse('dashboard:person-create'),
            {
                'first_name': 'Ada',
                'last_name': 'Nakato',
                'email': 'ada@hill.example.com',
                'user_type': UserType.STUDENT,
                'status': 'ACTIVE',
                'level': str(self.level.pk),
            },
        )
        self.assertRedirects(response, reverse('dashboard:people'))
        created = CommonUser.objects.get(email='ada@hill.example.com')
        self.assertEqual(created.account, self.school)

    def test_another_schools_level_is_not_selectable(self):
        self.login(self.teacher)
        response = self.client.post(
            reverse('dashboard:person-create'),
            {
                'first_name': 'Mallory',
                'email': 'mallory@hill.example.com',
                'user_type': UserType.STUDENT,
                'status': 'ACTIVE',
                'level': str(self.other_level.pk),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CommonUser.objects.filter(email='mallory@hill.example.com').exists())

    def test_cannot_edit_someone_from_another_school(self):
        self.login(self.teacher)
        url = reverse('dashboard:person-edit', args=[self.other_person.pk])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_delete_removes_the_row(self):
        self.login(self.teacher)
        url = reverse('dashboard:person-delete', args=[self.student.pk])
        response = self.client.delete(url, HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(CommonUser.objects.filter(pk=self.student.pk).exists())


class CollectionPageTests(DashboardTestCase):
    def test_levels_page_is_scoped(self):
        self.login(self.teacher)
        response = self.client.get(reverse('dashboard:levels'))
        self.assertEqual(list(response.context['rows']), [self.level])

    def test_create_returns_the_rows_partial(self):
        self.login(self.teacher)
        response = self.client.post(
            reverse('dashboard:levels'), {'name': 'P5', 'school_class': 'P5'},
        )
        self.assertContains(response, 'P5')
        self.assertNotContains(response, '<nav>')
        self.assertEqual(Level.objects.get(name='P5').account, self.school)

    def test_students_may_read_but_not_write(self):
        self.login(self.student)
        self.assertEqual(self.client.get(reverse('dashboard:levels')).status_code, 200)
        response = self.client.post(
            reverse('dashboard:levels'), {'name': 'P6', 'school_class': 'P6'},
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Level.objects.filter(name='P6').exists())

    def test_expense_form_only_offers_this_schools_categories(self):
        FinanceCategory.objects.create(account=self.other, name='Rival salaries')
        mine = FinanceCategory.objects.create(account=self.school, name='Salaries')
        AcademicYear.objects.create(account=self.school, name='2026')
        self.login(self.teacher)
        response = self.client.get(reverse('dashboard:expenses'))
        categories = response.context['form'].fields['category'].queryset
        self.assertEqual(list(categories), [mine])


class HomePageTests(DashboardTestCase):
    def test_counts_only_this_school(self):
        self.login(self.teacher)
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.context['student_count'], 1)
        self.assertEqual(response.context['level_count'], 1)
        self.assertContains(response, self.school.name)
