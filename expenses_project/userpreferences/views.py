from django.shortcuts import render
from django.conf import settings
import os
import json
from .models import UserPreference
from django.contrib import messages
from django.shortcuts import redirect
import django.core.exceptions

# Create your views here.

def index(request):

    try:
        user_preferences_object = UserPreference.objects.get(user=request.user)
    except UserPreference.DoesNotExist:
        user_preferences_object = UserPreference.objects.create(user=request.user)

    if request.method == 'GET':

        user_currency = user_preferences_object.get_user_preference()

        json_file_path = os.path.join(settings.BASE_DIR, 'currencies.json')
        currencies_list = []

        with open(json_file_path, 'r') as json_file:
            json_object = json_file.read()
            currencies = json.loads(json_object)

            for key, value in currencies.items():
                currency = { 'symbol' : key, 'name' : value }
                currencies_list.append(currency)
            

        return render(request, 'userpreferences/index.html', {'currencies' : currencies_list, 'user_currency' : user_currency})

    else:
        selected_currency = request.POST.get('currency')
        user_preferences_object.currency = selected_currency
        user_preferences_object.save()

        messages.success(request, 'changes saved.')
        return redirect('user-preferences')
    