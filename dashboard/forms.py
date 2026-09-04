"""Forms for the server-rendered UI.

Every form takes the requesting user's `account` and narrows its relation
choices to that school, so a crafted POST cannot attach a row to another
tenant's level, category or student.
"""
from django import forms

from finance.models import AcademicYear, Expense, FinanceCategory, Payment, Revenue
from users.models import CommonUser, Level, UserType

PERSON_FIELDS = [
    'first_name',
    'last_name',
    'email',
    'phone_number',
    'gender',
    'date_of_birth',
    'registration_number',
    'status',
]


class AccountScopedForm(forms.ModelForm):
    """Limits every related field to rows owned by `account`."""

    def __init__(self, *args, account=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.account = account
        # Stamped here rather than in save() so that model validation, which
        # runs during is_valid(), already sees the owning school.
        self.instance.account = account
        for field in self.fields.values():
            if isinstance(field, forms.ModelChoiceField):
                field.queryset = field.queryset.filter(account=account)


class PersonForm(AccountScopedForm):
    class Meta:
        model = CommonUser
        fields = [
            *PERSON_FIELDS,
            'user_type',
            'level',
            'class_teacher',
            'student_role',
            'job_title',
        ]
        widgets = {'date_of_birth': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['level'].queryset = Level.objects.filter(account=self.account)
        self.fields['class_teacher'].queryset = CommonUser.objects.filter(
            account=self.account, user_type=UserType.CLASSTEACHER,
        ).exclude(pk=self.instance.pk)

    def clean_registration_number(self):
        number = self.cleaned_data['registration_number']
        if not number:
            return number
        clash = CommonUser.objects.filter(
            account=self.account, registration_number=number,
        ).exclude(pk=self.instance.pk)
        if clash.exists():
            raise forms.ValidationError('That registration number is already used at this school.')
        return number


class LevelForm(AccountScopedForm):
    class Meta:
        model = Level
        fields = ['name', 'school_class']


class AcademicYearForm(AccountScopedForm):
    class Meta:
        model = AcademicYear
        fields = ['name', 'starts_on', 'ends_on']
        widgets = {
            'starts_on': forms.DateInput(attrs={'type': 'date'}),
            'ends_on': forms.DateInput(attrs={'type': 'date'}),
        }


class FinanceCategoryForm(AccountScopedForm):
    class Meta:
        model = FinanceCategory
        fields = ['name', 'description']


class ExpenseForm(AccountScopedForm):
    class Meta:
        model = Expense
        fields = ['description', 'amount', 'currency', 'category', 'academic_year']


class RevenueForm(AccountScopedForm):
    class Meta:
        model = Revenue
        fields = ['source', 'amount', 'currency', 'category', 'academic_year']


class PaymentForm(AccountScopedForm):
    class Meta:
        model = Payment
        fields = ['student', 'amount', 'currency', 'academic_year', 'paid_on']
        widgets = {'paid_on': forms.DateInput(attrs={'type': 'date'})}
