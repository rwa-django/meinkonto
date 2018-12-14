from django.urls import path

from . import views

app_name = 'account'
urlpatterns = [
    path('', views.index, name='index'),
    # path('<int:type_id>/', views.set_budget_type, name='type'),
    #
    # path('profile', views.Profile, name='profile'),
    # path('profile/<int:type_id>/', views.select_budget_type, name='selecttype'),
    #
    # path('budgettype', views.BudgetType, name='budgettype'),
    # path('addbudgettype', views.add_BudgetType, name='addbudgettype'),
    #
    # path('updbudgettype/<int:bt_id>/', views.BudgetTypeUpdate, name='updbudgettype'),
    #
    # path('mybudget', views.MyBudget, name='mybudget'),
    # path('mybudget/<int:type_id>/', views.choos_budget_type, name='choostype'),
]