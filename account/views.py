from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template import loader
from django.urls import reverse
from datetime import datetime

from django.template.defaultfilters import date
from django.contrib.auth.decorators import login_required

def _initBookingDate(login):

    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day
    startDay = 27
    amount = 1600
    budgetName = 'Konto Name'
    msg = ''
    label = 'AC-Label'

    return {'dd': day,
            'mm': month,
            'yyyy': year,
            'start_amount': amount,
            'start_day': startDay,
            'bt_label': label,
            'bt_type': type,
            'Q_Type_ID': 'Q_Type[0].pk',
            'msg': msg,
            }



# Create your views here.
# Account
@login_required(login_url='/accounts/login/')
def index(request):

    data = _initBookingDate(request.user)

    year = data['yyyy']
    month = data['mm']
    day = data['dd']
    startDay = data['start_day']
    label = data['bt_label']
    value = data['start_amount']


    template = loader.get_template('account/index.html')
    context = {
        'bt_list': [],
        'bt_bez': label,
        'bk_data': value,
        'year': year,
        'month': month,
        'month_desc': date(datetime.now(), 'F'),
        'Q_Budget_Pos': [],
    }

    return HttpResponse(template.render(context, request))
