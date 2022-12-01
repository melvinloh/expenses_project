from django.shortcuts import render
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages

# Create your views here.

class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        if not validate_email(email):
            return JsonResponse({'email_error': 'invalid email.'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'email is already taken.'}, status=409)
        return JsonResponse({'email_valid': 'looks good!'})

class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'username should only contain alphanumeric characters.'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'username taken.'}, status=409)
        return JsonResponse({'username_valid': 'looks good!'})

class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):

        MIN_PASSWORD_LENGTH = 8
        error_count = 0

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Server side validation
        if User.objects.filter(email=email).exists():
            messages.error(request, 'email is already taken.')
            error_count += 1
        if not validate_email(str(email)):
            messages.error(request, 'invalid email.')
            error_count += 1

        if not str(username).isalnum():
            messages.error(request, 'username should only contain alphanumeric characters.')
            error_count += 1
        if User.objects.filter(username=username).exists():
            messages.error(request, 'username taken.')
            error_count += 1

        if len(password) < MIN_PASSWORD_LENGTH:
            messages.error(request, 'password must be minimum 8 characters long.')
            error_count += 1

        if error_count == 0:
            new_user = User.objects.create_user(username=username, email=email, password=password)
            new_user.save()
            messages.success(request, 'account successfully created.')
            context = { 'fieldValues' : None }

        else:
            context = { 'fieldValues' : request.POST }
        
        return render(request, 'authentication/register.html', context)

class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')
