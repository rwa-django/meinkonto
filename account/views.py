from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template import loader
from django.urls import reverse
from datetime import datetime

from django.template.defaultfilters import date
from django.contrib.auth.decorators import login_required

from .models import Account, Account_Pos, Account_Type, Account_Base

MSG = ''

def _initAccountType(login):

    global MSG
    budgetName = 'Konto Name'

    Q_Type = Account_Type.objects.filter(login=login)
    if Q_Type:
        Account_Type.objects.filter(login=login).update(aktiv=True)
    else:
        MSG = _creatAccountType(login, budgetName, 'B')
        Q_Type = Account_Type.objects.filter(login=login)

    return Q_Type


def _creatAccountType(login, name, type):

    last = Account_Type.objects.all().filter(login=login).last()
    if last:
        aktiv = False
        pos = last.pos + 1
    else:
        aktiv = True
        pos = 1
    Q = Account_Type.objects.filter(login=login, label=name)

    status = ''
    if Q or len(name) < 2:
        status = 'Error:bereits vorhanden'
    else:
        AT = Account_Type(login=login,label=name,type=type,pos=pos,aktiv=aktiv)
        AT.save()

    return status

def _initBookingDate(login):

    global MSG

    startDay = 27   # monatlicher Starttag
    amount = 1600   # Startbetrag bim initialisieren

    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day

    Q_Type = Account_Type.objects.filter(login=login,
                                         aktiv=True)
    if not Q_Type:
        Q_Type = _initAccountType(login=login)

    label = Q_Type[0].type + '-' + Q_Type[0].label
    type =  Q_Type[0].type


    Q_Base = Account_Base.objects.filter(login=login,
                                         account_type=Q_Type[0],)
    if Q_Base:
        startDay = Q_Base[0].account_start_day
        amount = Q_Base[0].account_amount
    else:
        Q_Base = Account_Base(login=login,
                              account_type=Q_Type[0],
                              account_start_day=startDay,
                              account_amount=amount,
                              account_info='Init. Monat mit {0}'.format(amount),)
        Q_Base.save()


    return {'dd': day,
            'mm': month,
            'yyyy': year,
            'start_amount': amount,
            'start_day': startDay,
            'bt_label': label,
            'bt_type': type,
            'Q_Type_ID': Q_Type[0].pk,
            'MSG': MSG,
            }


def _getAccountTypes(login):

    return Account_Type.objects.values_list('id', 'label', 'aktiv', 'type', named=True).filter(login=login)


# Account
@login_required(login_url='/accounts/login/')
def index(request):

    data = _initBookingDate(request.user)

    year = data['yyyy']
    month = data['mm']
    day = data['dd']
    startDay = data['start_day']
    actype = data['bt_type']
    label = data['bt_label']
    value = data['start_amount']

    bt_list = _getAccountTypes(request.user)

    print(bt_list)


    template = loader.get_template('account/index.html')
    context = {
        'bt_list': bt_list,
        'bt_type': actype,
        'bt_bez': label,
        'bk_amount': value,
        'year': year,
        'month': month,
        'month_desc': date(datetime.now(), 'F'),
        'Q_Budget_Pos': [],
        'MSG': data['MSG']
    }

    return HttpResponse(template.render(context, request))


def set_account_type(request, type_id):

    q = Account_Type.objects.filter(login=request.user).update(aktiv=False)
    q = Account_Type.objects.filter(login=request.user, id=type_id).update(aktiv=True)

    return redirect('/account')

