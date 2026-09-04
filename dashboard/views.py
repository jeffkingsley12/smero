"""Server-rendered, htmx-driven UI.

Every view is tenant-scoped the same way the API is: the queryset is filtered
by the requesting user's `account_id` and creates take the account from the
session user, never from the payload. htmx requests get the table partial back
instead of the whole page, so a create, edit or delete swaps one fragment.
"""
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from finance.models import AcademicYear, Expense, FinanceCategory, Payment, Revenue
from users.models import CommonUser, Level, UserType
from users.permissions import STAFF_USER_TYPES

from .forms import (
    AcademicYearForm,
    ExpenseForm,
    FinanceCategoryForm,
    LevelForm,
    PaymentForm,
    PersonForm,
    RevenueForm,
)


def _account(request):
    account = request.user.account
    if account is None:
        raise Http404('This account is not attached to a school.')
    return account


def _may_write(user):
    return user.is_superuser or user.user_type in STAFF_USER_TYPES


def _forbidden():
    return HttpResponse('Only school staff may change records.', status=403)


@login_required
def home(request):
    account = _account(request)
    people = CommonUser.objects.filter(account=account)
    context = {
        'account': account,
        'student_count': people.filter(user_type=UserType.STUDENT).count(),
        'teacher_count': people.filter(user_type__in=STAFF_USER_TYPES).count(),
        'level_count': Level.objects.filter(account=account).count(),
        'revenue_total': Revenue.objects.filter(account=account).aggregate(
            total=Sum('amount'),
        )['total'],
        'expense_total': Expense.objects.filter(account=account).aggregate(
            total=Sum('amount'),
        )['total'],
        'recent_payments': Payment.objects.filter(account=account).select_related('student')[:5],
    }
    return render(request, 'dashboard/home.html', context)


def _people_queryset(request):
    people = CommonUser.objects.filter(account=_account(request)).select_related('level')
    user_type = request.GET.get('user_type', '')
    if user_type:
        people = people.filter(user_type=user_type)
    search = request.GET.get('q', '').strip()
    if search:
        people = people.filter(first_name__icontains=search) | people.filter(
            last_name__icontains=search,
        ) | people.filter(email__icontains=search)
    return people


@login_required
def people(request):
    context = {
        'people': _people_queryset(request),
        'user_types': UserType.choices,
        'selected_type': request.GET.get('user_type', ''),
        'q': request.GET.get('q', ''),
        'may_write': _may_write(request.user),
    }
    if request.headers.get('HX-Request'):
        return render(request, 'dashboard/partials/people_rows.html', context)
    return render(request, 'dashboard/people.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def person_form(request, pk=None):
    if not _may_write(request.user):
        return _forbidden()
    account = _account(request)
    person = get_object_or_404(CommonUser, pk=pk, account=account) if pk else None
    form = PersonForm(request.POST or None, instance=person, account=account)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('dashboard:people')
    return render(
        request,
        'dashboard/person_form.html',
        {'form': form, 'person': person, 'title': 'Edit person' if person else 'Add person'},
    )


@login_required
@require_http_methods(['DELETE', 'POST'])
def person_delete(request, pk):
    if not _may_write(request.user):
        return _forbidden()
    person = get_object_or_404(CommonUser, pk=pk, account=_account(request))
    if person.pk == request.user.pk:
        return HttpResponse('You cannot delete your own account.', status=400)
    person.delete()
    if request.headers.get('HX-Request'):
        return HttpResponse(status=204)
    return redirect('dashboard:people')


def collection_view(model, form_class, name, url_name, select_related=()):
    """Builds a list page with an inline create form, both tenant-scoped.

    The collections differ only in model, form and columns, so they share one
    implementation: GET renders the page, POST creates the row and returns just
    the table body, which htmx swaps in place.
    """
    template = f'dashboard/{name}.html'
    partial = f'dashboard/partials/{name}_rows.html'

    @login_required
    @require_http_methods(['GET', 'POST'])
    def view(request):
        account = _account(request)
        rows = model.objects.filter(account=account).select_related(*select_related)
        form = form_class(request.POST or None, account=account)
        if request.method == 'POST':
            if not _may_write(request.user):
                return _forbidden()
            if form.is_valid():
                form.save()
                return render(request, partial, {'rows': rows, 'may_write': True})
        return render(
            request,
            template,
            {
                'rows': rows,
                'form': form,
                'post_url': reverse(f'dashboard:{url_name}'),
                'may_write': _may_write(request.user),
            },
        )

    return view


levels = collection_view(Level, LevelForm, 'levels', 'levels')
academic_years = collection_view(
    AcademicYear, AcademicYearForm, 'academic_years', 'academic-years',
)
categories = collection_view(FinanceCategory, FinanceCategoryForm, 'categories', 'categories')
expenses = collection_view(
    Expense, ExpenseForm, 'expenses', 'expenses', ('category', 'academic_year'),
)
revenues = collection_view(
    Revenue, RevenueForm, 'revenues', 'revenues', ('category', 'academic_year'),
)
payments = collection_view(
    Payment, PaymentForm, 'payments', 'payments', ('student', 'academic_year'),
)
