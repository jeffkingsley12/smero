from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('people/', views.people, name='people'),
    path('people/new/', views.person_form, name='person-create'),
    path('people/<uuid:pk>/edit/', views.person_form, name='person-edit'),
    path('people/<uuid:pk>/delete/', views.person_delete, name='person-delete'),
    path('levels/', views.levels, name='levels'),
    path('academic-years/', views.academic_years, name='academic-years'),
    path('categories/', views.categories, name='categories'),
    path('expenses/', views.expenses, name='expenses'),
    path('revenues/', views.revenues, name='revenues'),
    path('payments/', views.payments, name='payments'),
]
