from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
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
    categories = Category.objects.all()

    if request.method == 'GET':

        order_by = request.GET.get('order_by', '-date')
        all_user_expenses = Expense.objects.filter(user=request.user).order_by(order_by)
        
        paginator_obj = Paginator(all_user_expenses, 8)
        page_number = request.GET.get('page', 1)
        page_obj = paginator_obj.get_page(page_number)

        
        context = {'all_user_expenses' : all_user_expenses, 'user_currency_symbol': user_currency_symbol, 
            'categories' : categories, 'page_obj' : page_obj }

        return render(request, 'expenses/index.html', context)

@login_required(login_url='/authentication/login')
def search_expenses(request):

    if request.method == 'POST':
        # stack filters together: https://docs.djangoproject.com/en/4.1/topics/db/queries/
        search_str = json.loads(request.body).get('search-form-input')

        all_user_expenses = Expense.objects.filter(user=request.user)
        filtered_user_expenses = all_user_expenses.filter(description__icontains=search_str)
        data = filtered_user_expenses.values()

        return JsonResponse(list(data), safe=False)
        

    
@login_required(login_url='/authentication/login')
def add_expenses(request):

    # get categories
    categories = Category.objects.all()
    # get user currency
    user_currency_symbol = get_user_currency_symbol(request.user)

    if request.method == 'GET':

        context = {'categories' : categories, 'user_currency_symbol': user_currency_symbol, }

        return render(request, 'expenses/add_expenses.html', context)
    
    elif request.method == 'POST':

        amount = request.POST.get('amount')
        date = request.POST.get('date')
        description = request.POST.get('description')
        category = request.POST.get('category')

        description = str(description).strip()
        


        # server validation: amount is float, category in category, date is date
        dict_fields = server_validation(amount, date, category, description)


        if len(dict_fields['error_messages']) != 0:

            for message in dict_fields['error_messages']:
                messages.error(request, message)

            context = {'categories' : categories, 'user_currency_symbol': user_currency_symbol, 'dict_fields' : dict_fields }
            return render(request, 'expenses/add_expenses.html', context)

        else:
            if not description or description == "":
                description = None

            expense_object = Expense.objects.create(user=request.user, amount=amount, date=date, category=category, description=description)
            expense_object.save()

            messages.success(request, 'new expense created successfully.')
            return redirect('expenses-index')

@login_required(login_url='/authentication/login')
def edit_expenses(request, id):
    
    expense_obj = Expense.objects.get(pk=id)

    if request.method == 'GET':
        amount = str(expense_obj.amount)
        category = str(expense_obj.category)
        description = str(expense_obj.description)
        date = str(expense_obj.date)
        
        return JsonResponse({'amount': amount, 'category': category, 'description': description, 'date': date, })

    elif request.method == 'POST':

        amount = request.POST.get('modal-amount')
        date = request.POST.get('modal-date')
        description = request.POST.get('modal-description')
        category = request.POST.get('modal-category')

        description = str(description).strip()


        # server validation: amount is float, category in category, date is date
        dict_fields = server_validation(amount, date, category, description)

        if len(dict_fields['error_messages']) != 0:
            
            for message in dict_fields['error_messages']:
                messages.error(request, f"unable to update changes: {message}")
        
        else:

            expense_obj.amount = amount
            expense_obj.date = date
            expense_obj.description = description
            expense_obj.category = category
            expense_obj.save()

            messages.success(request, 'expense updated successfully.')
        
        return redirect('expenses-index')


@login_required(login_url='/authentication/login')
def delete_expenses(request, id):

    try:
        expense_obj = Expense.objects.get(pk=id)
        if expense_obj.user == request.user:

            expense_obj.delete()
            messages.success(request, 'expense removed successfully.')
        else:
            messages.error(request, 'you are not authorised to remove this entry.')
    except:
        messages.error(request, 'unable to remove entry.')
    finally:
        return redirect('expenses-index')
    
    
# functions to create chart using Chart.JS (passing data as JSON object)

def expenses_category_summary(request, mths):
    today = datetime.date.today()
    previously = today - relativedelta(months=mths)

    expenses_x_months = Expense.objects.filter(user=request.user, date__gte=previously, date__lte=today)
    
    all_categories_x_months = {}

    for expense_obj in expenses_x_months:
        category = expense_obj.category

        if all_categories_x_months.get(category) is None:
            all_categories_x_months[category] = round(expense_obj.amount, 2)
        else:
            all_categories_x_months[category] = round(expense_obj.amount + all_categories_x_months.get(category), 2)

    return JsonResponse({'expenses_category_data' : all_categories_x_months }, safe=False)

def expenses_amount_summary(request, mths):
    cumulative_amount_by_month = {}

    today = datetime.date.today()
    this_mth = today.month
    this_yr = today.year
    end_dt = today + datetime.timedelta(days=1)
    
    for _ in range(mths):
        start_dt = datetime.datetime(this_yr, this_mth, 1)
        expenses_list_for_month_x = Expense.objects.filter(user=request.user, date__gte=start_dt, date__lt=end_dt)
        
        expense_amt_for_month_x = 0
        current_mth_string = start_dt.strftime('%B')

        for expense_obj in expenses_list_for_month_x:
            expense_amt_for_month_x += expense_obj.amount

        # add to dictionary
        # note : maxmium months is 12, else dictionary will have values overrriden by same keys 
        # (e.g. Dec 2022 and Dec 2021) both have keys as "December"
        cumulative_amount_by_month[current_mth_string] = round(expense_amt_for_month_x, 2)

        # if jan - 1mth (overflow to last year dec)
        if this_mth - 1 < 1:
            this_mth = 12
            this_mth = this_yr - 1
        else:
            this_mth = this_mth - 1
        
        end_dt = start_dt

    return JsonResponse({'expenses_amount_data' : cumulative_amount_by_month }, safe=False)


def expenses_statistics_view(request):
    context = {}

    def get_amt_and_count(expenses_list):
        count = len(expenses_list)
        amount = 0

        for expense in expenses_list:
            amount += expense.amount

        return {'count' : count, 'amount' : round(amount, 2) }

    today = datetime.date.today()
    expenses_today = Expense.objects.filter(user=request.user, date=today)
    context['today'] = get_amt_and_count(expenses_today)

    this_month = datetime.datetime(today.year, today.month, 1)
    expenses_month = Expense.objects.filter(user=request.user, date__gte=this_month, date__lte=today)
    context['month'] = get_amt_and_count(expenses_month)

    # Monday is 0, Tuesday is 1, etc in today.weekday()
    this_week = today - datetime.timedelta(days=today.weekday()) 
    expenses_week = Expense.objects.filter(user=request.user, date__gte=this_week, date__lte=today)
    context['week'] = get_amt_and_count(expenses_week)

    return render(request, 'expenses/statistics.html', context)