from django.urls import path

from . import views

app_name = 'account'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:type_id>/', views.set_account_type, name='settype'),

    path('profile', views.Profile, name='profile'),
    path('profile/<int:type_id>/', views.select_account_type, name='selecttype'),

    path('mybudget', views.MyBudget, name='mybudget'),
    path('mykonto', views.MyKonto, name='mykonto'),

    path('mybudget/<int:type_id>/', views.choos_account_type, name='choosetype'),

    path('accounttype', views.AccountType, name='accounttype'),
    path('addaccounttype', views.add_AccountType, name='addaccounttype'),
    path('updaccounttype/<int:bt_id>/', views.AccountTypeUpdate, name='updaccounttype'),
    #
]