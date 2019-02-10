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

    label = Q_Type[0].label
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

    print('-', actype, month, year)

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

            print('----', val, pos.pos, pos.booking_amount)

            last_pos = pos.pos

        if actype == 'B':
            account_amount = Q_Account[0].account_amount - val
        else:
            account_amount = Q_Account[0].current_amount + val
        print(actype, '--', account_amount)
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


def set_account_type(request, type_id):

    q = Account_Type.objects.filter(login=request.user).update(aktiv=False)
    q = Account_Type.objects.filter(login=request.user, id=type_id).update(aktiv=True)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def choos_account_type(request, type_id):
    q = Account_Type.objects.filter(login=request.user).update(aktiv=False)
    q = Account_Type.objects.filter(login=request.user, id=type_id).update(aktiv=True)

    Q_Type = Account_Type.objects.filter(login=request.user, id=type_id, aktiv=True)
    print('=====Type', Q_Type[0].type)

    if Q_Type[0].type == 'B':
        return HttpResponseRedirect(reverse('account:mybudget'))
    else:
        return HttpResponseRedirect(reverse('account:mykonto'))




###############################
# Account
###############################
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

def _getInitAccount(login):

    data = _initBookingDate(login)

    year = data['yyyy']
    month = data['mm']
    day = data['dd']
    acttype = data['bt_type']

    Q_Type = Account_Type.objects.filter(login=login, aktiv=True)

    return {'dd': day,
            'mm': month,
            'yyyy': year,
            'bt_type': acttype,
            'Q_Type_ID': Q_Type[0].pk,
            }


def upd_account_pos(request, pos):

    msg = ''
    login = request.user
    data = _getInitAccount(login)

    year = data['yyyy']
    month = data['mm']
    acttype = data['bt_type']
    Q_Type_ID = data['Q_Type_ID']

    try:
        amount = int(request.POST['amount'])
        info = request.POST['info']
    except:
        amount = 0
        info = ''


    if acttype == 'B':
        Q_Account = Account.objects.filter(login=login, account_type=Q_Type_ID, account_month=month, account_year=year)
    else:
        Q_Account = Account.objects.filter(login=login, account_type=Q_Type_ID, account_month=month)

    if amount != 0:
        val = amount
        # Type A Konto add input to Account
        if acttype == 'A':
            val = amount * -1
        ap = Account_Pos.objects.filter(account_id=Q_Account[0], pos=pos).update(booking_amount=val, booking_info=info)

        msg = 'Ihr Daten wurden gespeichert'

    Q_Pos = Account_Pos.objects.filter(account_id=Q_Account[0], pos=pos)

    context = {'POS': Q_Pos,
               'MSG': msg,}

    template = loader.get_template('account/account-upd-pos.html')
    return HttpResponse(template.render(context, request))

def del_account_pos(request, pos):

    login = request.user
    data = _getInitAccount(login)

    year = data['yyyy']
    month = data['mm']
    acttype = data['bt_type']
    Q_Type_ID = data['Q_Type_ID']


    if acttype == 'B':
        Q_Account = Account.objects.filter(login=login, account_type=Q_Type_ID, account_month=month, account_year=year)
    else:
        Q_Account = Account.objects.filter(login=login, account_type=Q_Type_ID, account_month=month)

    Q_Pos = Account_Pos.objects.filter(account_id=Q_Account[0], pos=pos)
    Q_Pos.delete()

    msg = 'Position gelöscht'

    print('--DEL POS:', Q_Pos)

    return redirect('/account')

###############################
# Profile
###############################
@login_required(login_url='/accounts/login/')
def Profile(request):

    data = _initBookingDate(request.user)

    current_budget = _getCurrentAccount(request.user, data['Q_Type_ID'], data['bt_type'], data['mm'], data['yyyy'])
    ak_amount = int(current_budget['account_amount'])

    bt_list = _getAccountTypes(request.user)

    template = loader.get_template('account/profile.html')
    context = {
        'bt_list': bt_list,
        'bt_type': data['bt_type'],
        'bt_bez': data['bt_label'],
        'bb_day': data['start_day'],
        'bk_amount': ak_amount,
    }

    return HttpResponse(template.render(context, request))

def select_account_type(request, type_id):

    q = Account_Type.objects.filter(login=request.user).update(aktiv=False)
    q = Account_Type.objects.filter(login=request.user, id=type_id).update(aktiv=True)

    return HttpResponseRedirect(reverse('account:profile'))

###############################
# MyBudget
###############################
@login_required(login_url='/accounts/login/')
def MyBudget(request):

    msg = ''
    try:
        amount = int(request.POST['amount'])
        day = int(request.POST['day'])
    except:
        amount = 0
        day = 0

    try:
        upd = request.POST['ckb_update']
    except:
        upd = '0'

    data = _initBookingDate(request.user)
    Q_Type_ID = data['Q_Type_ID']
    start_day = int(data['start_day'])
    start_amount = int(data['start_amount'])

    if amount > 0 and day > 0:

        Q_Base = Account_Base.objects.filter(login=request.user,
                                             account_type=Q_Type_ID, ).update(account_start_day=day, account_amount=amount)

        if upd == '1':
            Q_Budget = Account.objects.filter(login=request.user,
                                              account_type=Q_Type_ID,
                                              account_month=data['mm'],
                                              account_year=data['yyyy']).update(account_amount=amount)
        start_day = day
        start_amount = amount
        msg = 'Ihr Daten wurden gespeichert'

    bt_list = _getAccountTypes(request.user)

    template = loader.get_template('account/mybudget.html')
    context = {
        'bt_list': bt_list,
        'bt_bez': data['bt_label'],
        'bt_type': data['bt_type'],
        'bb_day': start_day,
        'bk_amount': start_amount,
        'month_desc': date(datetime.now(), 'F'),
        'msg': msg,
    }

    return HttpResponse(template.render(context, request))



###############################
# MyKonto
###############################
@login_required(login_url='/accounts/login/')
def MyKonto(request):

    msg = ''
    account_amount = 0
    current_amount = 0

    try:
        amount = int(request.POST['amount'])
    except:
        amount = 0

    data = _initBookingDate(request.user)

    Q_Type = Account_Type.objects.filter(login=request.user,
                                         aktiv=True)
    if not Q_Type:
        Q_Type = _initAccountType(login=request.user)

    Q_Account = Account.objects.filter(login=request.user,
                                       account_type=Q_Type[0],)


    if amount > 0 :
        qa = Account.objects.filter(login=request.user,
                                           account_type=Q_Type[0], ).update(current_amount=amount, account_amount=amount, account_info='Kontostand angepasst')

        qb = Account_Base.objects.filter(login=request.user,
                                             account_type=Q_Type[0], ).update(account_amount=amount, account_info='Kontostand angepasst')

        msg = 'Ihr Daten wurden gespeichert'

    if Q_Account:
        account_amount = int(Q_Account[0].account_amount)
        current_amount = Q_Account[0].current_amount

    bt_list = _getAccountTypes(request.user)

    template = loader.get_template('account/mykonto.html')
    context = {
        'bt_list': bt_list,
        'bt_bez': data['bt_label'],
        'bt_type': data['bt_type'],
        'ak_amount': account_amount,
        'ak_current': current_amount,
        'msg': msg,
    }

    return HttpResponse(template.render(context, request))

###############################
# MyKontoType
###############################
@login_required(login_url='/accounts/login/')
def AccountType(request):

    type_list = Account_Type.objects.filter(login=request.user)

    template = loader.get_template('account/account-type.html')
    context = {'type_list': type_list,}

    return HttpResponse(template.render(context, request))

def add_AccountType(request):
    name = request.POST['name']
    type = request.POST['type_update']

    msg = creat_account_type(request.user, name, type)

    return HttpResponseRedirect(reverse('account:accounttype'))


def creat_account_type(login, name, type):

    last = Account_Type.objects.all().filter(login=login).last()
    if last:
        aktiv = False
        pos = last.pos + 1
    else:
        aktiv = True
        pos = 1

    q = Account_Type.objects.filter(login=login, label=name)

    status = ''
    if q or len(name) < 2:
        status = 'Error:bereits vorhanden'
    else:
        b = Account_Type(login=login,label=name,type=type,pos=pos,aktiv=aktiv)
        b.save()

    return status

def AccountTypeUpdate(request, bt_id):
    bt_label = ''
    bt_type = 'B'

    Q_Type = Account_Type.objects.filter(id=bt_id)
    if Q_Type:
        bt_label = Q_Type[0].label
        bt_type = Q_Type[0].type

    try:
        label = request.POST['label']
    except:
        label = ''

    status = ''
    if label != '' and label != bt_label:

        q = Account_Type.objects.filter(login=request.user, label=label)
        if q or len(label) < 2:
            status = 'Budget Name >>'  + label + '<< bereits vorhanden'
        else:
            Q_Type = Account_Type.objects.filter(id=bt_id).update(label=label)
            bt_label = label
            status = 'geändert'

    template = loader.get_template('account/account-type-update.html')
    context = {'bt_id': bt_id,
               'bt_label': bt_label,
               'bt_type': bt_type,
               'msg': status,}

    return HttpResponse(template.render(context, request))


###############################
# Statistics
###############################
def Statistics(request):
    monthNames = ['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember'];
    monthShortNames = ['Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dez'];

    login = request.user
    data = _initBookingDate(login)
    bt_list = _getAccountTypes(request.user)

    year = data['yyyy']
    month = data['mm']
    day = data['dd']
    acttype = data['bt_type']
    label = data['bt_label']

    valueslist = ''
    monthlist = ''
    Q_Account = Account.objects.filter(login=login, account_type=data['Q_Type_ID'])
    for pos in Q_Account.order_by('account_year','account_month'):
        print('-', pos.current_amount, pos.account_year, pos.account_month)
        valueslist += str(pos.current_amount) + ','
        monthlist = monthlist + ',' + str(pos.account_month)

    valueslist = valueslist.strip(',')
    valueslist = valueslist.split(',')
    print('-m-', monthlist, '---valueslist:', valueslist, '--[0]:', valueslist[0], len(valueslist) )

    labels = ''
    values = ''
    if len(valueslist) < 2:
        valueslist += '0,'

    for x in range(0, len(valueslist)):
        if month + x > 12:
            pos = month - 13 + x
        else:
            pos = month - 1 + x
        labels += monthShortNames[pos] + ','

        values += valueslist[x] + ','

    labels = labels.strip(',')
    values = values.strip(',')
    print('===Val:', values)
    print('---Lab:', labels, month)

    template = loader.get_template('account/statistics.html')
    context= {'myData': values,
              'myLabel': labels,

        'bt_list': bt_list,
        'bt_type': acttype,
        'bt_bez': label,
        'month_desc': date(datetime.now(), 'F'),
        'MSG': data['MSG']
    }

    return HttpResponse(template.render(context, request))
