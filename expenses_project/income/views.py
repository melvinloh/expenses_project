from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Income, IncomeStream
from userpreferences.models import UserPreference
from django.contrib import messages
from django.shortcuts import redirect

from .utils import get_user_currency_symbol, server_validation
from django.http import JsonResponse

from django.core.paginator import Paginator
import json
import datetime
from dateutil.relativedelta import relativedelta


# Create your views here.

@login_required(login_url='/authentication/login')
def index(request):

    # get user currency
    user_currency_symbol = get_user_currency_symbol(request.user)
    # get categories
    income_streams = IncomeStream.objects.all()

    if request.method == 'GET':

        order_by = request.GET.get('order_by', '-date')
        all_user_income = Income.objects.filter(user=request.user).order_by(order_by)
        
        paginator_obj = Paginator(all_user_income, 8)
        page_number = request.GET.get('page', 1)
        page_obj = paginator_obj.get_page(page_number)

        
        context = {'all_user_income' : all_user_income, 'user_currency_symbol': user_currency_symbol, 
            'income_streams' : income_streams, 'page_obj' : page_obj, }

        return render(request, 'income/index.html', context)

@login_required(login_url='/authentication/login')
def search_income(request):

    if request.method == 'POST':
        # stack filters together: https://docs.djangoproject.com/en/4.1/topics/db/queries/
        search_str = json.loads(request.body).get('search-form-input')

        all_user_income = Income.objects.filter(user=request.user)
        filtered_user_income = all_user_income.filter(description__icontains=search_str)
        data = filtered_user_income.values()

        return JsonResponse(list(data), safe=False)
        

    
@login_required(login_url='/authentication/login')
def add_income(request):

    # get categories
    income_streams = IncomeStream.objects.all()
    # get user currency
    user_currency_symbol = get_user_currency_symbol(request.user)

    if request.method == 'GET':

        context = {'income_streams' : income_streams, 'user_currency_symbol': user_currency_symbol, }

        return render(request, 'income/add_income.html', context)
    
    elif request.method == 'POST':

        amount = request.POST.get('amount')
        date = request.POST.get('date')
        description = request.POST.get('description')
        stream = request.POST.get('income-stream')

        description = str(description).strip()
        


        # server validation: amount is float, income_stream in income_stream, date is date
        dict_fields = server_validation(amount, date, stream, description)


        if len(dict_fields['error_messages']) != 0:

            for message in dict_fields['error_messages']:
                messages.error(request, message)

            context = {'income_streams' : income_streams, 'user_currency_symbol': user_currency_symbol, 'dict_fields' : dict_fields }
            return render(request, 'income/add_income.html', context)

        else:
            if not description or description == "":
                description = None

            income_object = Income.objects.create(user=request.user, amount=amount, date=date, income_stream=stream, description=description)
            income_object.save()

            messages.success(request, 'new income entry created successfully.')
            return redirect('income-index')

@login_required(login_url='/authentication/login')
def edit_income(request, id):
    
    income_obj = Income.objects.get(pk=id)

    if request.method == 'GET':
        amount = str(income_obj.amount)
        stream = str(income_obj.income_stream)
        description = str(income_obj.description)
        date = str(income_obj.date)
        
        return JsonResponse({'amount': amount, 'income_stream': stream, 'description': description, 'date': date, })

    elif request.method == 'POST':

        amount = request.POST.get('modal-amount')
        date = request.POST.get('modal-date')
        description = request.POST.get('modal-description')
        stream = request.POST.get('modal-income-stream')

        description = str(description).strip()


        # server validation: amount is float, income stream in income stream, date is date
        dict_fields = server_validation(amount, date, stream, description)

        if len(dict_fields['error_messages']) != 0:
            
            for message in dict_fields['error_messages']:
                messages.error(request, f"unable to update changes: {message}")
        
        else:

            income_obj.amount = amount
            income_obj.date = date
            income_obj.description = description
            income_obj.income_stream = stream
            income_obj.save()

            messages.success(request, 'income entry updated successfully.')
        
        return redirect('income-index')


@login_required(login_url='/authentication/login')
def delete_income(request, id):

    try:
        income_obj = Income.objects.get(pk=id)
        if income_obj.user == request.user:

            income_obj.delete()
            messages.success(request, 'income entry removed successfully.')
        else:
            messages.error(request, 'you are not authorised to remove this entry.')
    except:
        messages.error(request, 'unable to remove entry.')
    finally:
        return redirect('income-index')

# functions to create chart using Chart.JS (passing data as JSON object)

def income_category_summary(request, mths):
    today = datetime.date.today()
    previously = today - relativedelta(months=mths)

    income_x_months = Income.objects.filter(user=request.user, date__gte=previously, date__lte=today)
    
    all_categories_x_months = {}

    for income_obj in income_x_months:
        category = income_obj.income_stream

        if all_categories_x_months.get(category) is None:
            all_categories_x_months[category] = round(income_obj.amount, 2)
        else:
            all_categories_x_months[category] = round(income_obj.amount + all_categories_x_months.get(category), 2)

    return JsonResponse({'income_category_data' : all_categories_x_months }, safe=False)

def income_amount_summary(request, mths):
    cumulative_amount_by_month = {}

    today = datetime.date.today()
    this_mth = today.month
    this_yr = today.year
    end_dt = today + datetime.timedelta(days=1)
    
    for _ in range(mths):
        start_dt = datetime.datetime(this_yr, this_mth, 1)
        income_list_for_month_x = Income.objects.filter(user=request.user, date__gte=start_dt, date__lt=end_dt)
        
        income_amt_for_month_x = 0
        current_mth_string = start_dt.strftime('%B')

        for income_obj in income_list_for_month_x:
            income_amt_for_month_x += income_obj.amount

        # add to dictionary
        # note : maxmium months is 12, else dictionary will have values overrriden by same keys 
        # (e.g. Dec 2022 and Dec 2021) both have keys as "December"
        cumulative_amount_by_month[current_mth_string] = round(income_amt_for_month_x, 2)

        # if jan - 1mth (overflow to last year dec)
        if this_mth - 1 < 1:
            this_mth = 12
            this_mth = this_yr - 1
        else:
            this_mth = this_mth - 1
        
        end_dt = start_dt

    return JsonResponse({'income_amount_data' : cumulative_amount_by_month }, safe=False)


def income_statistics_view(request):
    context = {}

    today = datetime.date.today()

    def get_amt_and_count(income_list):
        count = len(income_list)
        amount = 0

        for income in income_list:
            amount += income.amount

        return {'count' : count, 'amount' : round(amount, 2) }

    this_month = datetime.datetime(today.year, today.month, 1)
    income_month = Income.objects.filter(user=request.user, date__gte=this_month, date__lte=today)
    context['month'] = get_amt_and_count(income_month)

    return render(request, 'income/statistics.html', context)
    
