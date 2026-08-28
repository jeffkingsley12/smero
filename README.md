# Smero — multi-tenant school management

A Django/DRF API for running several schools out of one database. Every row
belongs to an `Account` (a school), and that account is the tenant key used by
[django-multitenant](https://github.com/citusdata/django-multitenant).

## Implemented today

- **Schools** (`users.Account`): name, type, domain, address.
- **Levels** (`users.Level`): the classes within a school, unique by name per school.
- **People** (`users.CommonUser`): one table holding directors, headteachers, class
  teachers, teachers, school workers and students. The role lives in `user_type`,
  and each role also has a proxy model (`Student`, `Teacher`, …) with its own
  manager, admin page and API endpoint.
- **Finance** (`finance`): academic years, categories, expenses, revenues,
  transactions, student payments and per-year reports.

Courses, attendance and assignments are *not* implemented.

## Tenancy model

Isolation is enforced in three places, so no single mistake exposes another
school's data:

1. `users.middleware.TenantMiddleware` binds the logged-in user's account to the
   thread and clears it after the response.
2. `users.views.TenantScopedViewSet` sets the tenant again (DRF authenticates
   after middleware runs, so a JWT request is still anonymous at that point) and
   filters every queryset by `account_id`.
3. `users.permissions.IsSameAccount` rejects any object from another account as
   a backstop, and the database constraints are all scoped per account.

`account` is never writable through the API — it is taken from the requesting
user — and `password`, `is_staff`, `is_superuser`, `groups` and
`user_permissions` are not exposed by any serializer.

### Citus

The models are laid out for Citus (every table carries the tenant column and
uses `TenantForeignKey`), but the tables are **not** distributed yet: Citus
requires the distribution column to be part of every primary key and unique
constraint, which Django cannot express without composite primary keys. Until
that is resolved the project runs on plain PostgreSQL and tenancy is enforced by
the application. The previous `0002_distribute_tables` migration was removed —
it built primary keys on columns that never existed.

## Requirements

- Python 3.10+
- PostgreSQL 13+

## Installation

1. Clone the repository and create a virtual environment.
2. `pip install -r requirements-dev.txt` (or `requirements.txt` without the lint tooling).
3. Copy `core/.env.example` to `core/.env` and fill it in. `DJANGO_SECRET_KEY` is
   required; the database connection, `DJANGO_DEBUG` and `DJANGO_ALLOWED_HOSTS`
   are read from there too. Never commit `core/.env`.
4. `python manage.py migrate`
5. `python manage.py createsuperuser` — superusers have no account and can see
   every school through the admin.
6. `python manage.py runserver`

All settings come from the environment via
[python-decouple](https://pypi.org/project/python-decouple/); `DJANGO_DEBUG`
defaults to `False`.

## API

Everything is under `/api/`, browsable at the root of that prefix:

| Path | Contents |
| --- | --- |
| `/api/accounts/` | the requesting user's school |
| `/api/levels/` | classes |
| `/api/users/` | everyone at the school, filterable by `user_type` |
| `/api/students/`, `/api/teachers/`, `/api/class-teachers/`, `/api/directors/`, `/api/headteachers/`, `/api/school-workers/` | one role each |
| `/api/finance/…` | academic years, categories, expenses, revenues, transactions, payments, reports |
| `/api/auth/token/` | JWT obtain / refresh / verify |

Reads are open to any authenticated member of the school; writes require a
director, headteacher, teacher or class teacher.

## Development

```sh
ruff check .                              # lint
python manage.py makemigrations --check   # model/migration drift
python manage.py test                     # tests, incl. cross-tenant isolation
```

CI runs the same three commands against PostgreSQL on every pull request.

## License

MIT.
