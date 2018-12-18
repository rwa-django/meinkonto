from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template import loader
from django.urls import reverse
from datetime import datetime

from django.template.defaultfilters import date
from django.contrib.auth.decorators import login_required

from .models import Account, Account_Pos, Account_Type, Account_Base
import decimal

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
    if Q:
        status = 'Error:bereits vorhanden'
    elif len(name) < 2:
        status = 'Error:Name zu kurz'
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

    if day >= startDay:
        if day > 15:
            month += 1
        if month > 12:
            month = 1
            year += 1

    return {'dd': day,
            'mm': month if type == 'B' else 0,
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


def _getCurrentAccount(login, Q_Type_ID, actype, month, year):

    if actype == 'B':
        Q_Account = Account.objects.filter(login=login, account_type=Q_Type_ID, account_month=month, account_year=year)
    else:
        Q_Account = Account.objects.filter(login=login, account_type=Q_Type_ID, account_month=month)

    if Q_Account:
        ID_B = Q_Account[0].pk
        Q_Account_Pos = Account_Pos.objects.filter(account_id=ID_B)

        val = 0
        last_pos = 1
        for pos in Q_Account_Pos.order_by('pos'):
            val += decimal.Decimal(pos.booking_amount)

            last_pos = pos.pos
            print(val, pos.booking_amount)

        if actype == 'B':
            account_amount = Q_Account[0].account_amount - val
        else:
            account_amount = Q_Account[0].current_amount
    else:
        if Q_Type_ID:
            Q_Base = Account_Base.objects.filter(login=login,
                                                 account_type=Q_Type_ID,)
            account_amount = Q_Base[0].account_amount

            Q_Type = Account_Type.objects.filter(login=login,
                                                 aktiv=True)
            Q_Account = Account(login=login,
                                account_type=Q_Type[0],
                                account_month=month,
                                account_year=year,
                                account_amount=account_amount,
                                current_amount=account_amount,
                                account_info='Init. Monat {0}'.format(date(datetime.now(), 'F')), )
            Q_Account.save()
            last_pos = 0

            Q_Account = Account.objects.filter(login=login, account_type=Q_Type_ID, account_month=month, account_year=year)

    return {'Q_Account': Q_Account,
            'account_amount': account_amount,
            'last_pos': last_pos,
            }


# Account
@login_required(login_url='/accounts/login/')
def index(request):

    try:
        amount = int(request.POST['amount'])
        info = request.POST['info']
    except:
        amount = 0
        info = ''

    data = _initBookingDate(request.user)

    year = data['yyyy']
    month = data['mm']
    day = data['dd']
    startDay = data['start_day']
    actype = data['bt_type']
    label = data['bt_label']
    value = data['start_amount']

    bt_list = _getAccountTypes(request.user)

    # current budget
    current_budget = _getCurrentAccount(request.user, data['Q_Type_ID'], actype, month, year)

    Q_Account = current_budget['Q_Account']
    ak_amount = int(current_budget['account_amount'])
    last_pos = int(current_budget['last_pos'])

    Q_Account_Pos = []
    if amount != 0:
        val = amount
        # Type A Konto add input to Account
        if actype == 'A':
            val = amount * -1
        ak_amount = ak_amount - val


        print('--Create Account Pos %s M %s Y %s ak: %s am: %s' % (last_pos + 1, month, year, ak_amount, amount))

        ap = Account_Pos(account_id=Q_Account[0], pos=last_pos + 1, booking_amount=amount, booking_info=info)
        ap.save()

        a = Account.objects.filter(login=request.user,
                                   account_type=data['Q_Type_ID'],
                                   account_month=0,
                                   account_year=year).update(current_amount=int(ak_amount))


    if Q_Account:
        Q_Account_Pos = Account_Pos.objects.filter(account_id=Q_Account[0])


    template = loader.get_template('account/index.html')
    context = {
        'bt_list': bt_list,
        'bt_type': actype,
        'bt_bez': label,
        'bk_amount': ak_amount,
        'year': year,
        'month': month,
        'month_desc': date(datetime.now(), 'F'),
        'Q_Account_Pos': Q_Account_Pos,
        'MSG': data['MSG']
    }

    return HttpResponse(template.render(context, request))


def set_account_type(request, type_id):

    q = Account_Type.objects.filter(login=request.user).update(aktiv=False)
    q = Account_Type.objects.filter(login=request.user, id=type_id).update(aktiv=True)

    return redirect('/account')

