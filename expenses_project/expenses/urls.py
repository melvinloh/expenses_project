from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name="expenses-index"),
    path('add-expenses', views.add_expenses, name="add-expenses"),
    path('edit-expenses/<int:id>', views.edit_expenses, name="edit-expenses"),
    path('delete-expenses/<int:id>', views.delete_expenses, name="delete-expenses"),
    path('search-expenses', csrf_exempt(views.search_expenses), name="search-expenses"),
    path('expenses-category-summary', views.expenses_category_summary, name="expenses-category-summary"),
    path('expenses-statistics-view', views.expenses_statistics_view, name="expenses-statistics-view"),
]

