from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse

# Create your views here.

@login_required(login_url=reverse('login'))
def index(request):
    return render(request, 'expenses/index.html')

def add_expenses(request):
    return render(request, 'expenses/add_expenses.html')