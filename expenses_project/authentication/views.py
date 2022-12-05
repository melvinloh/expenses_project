from django.shortcuts import render
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect

from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from .utils import AppTokenGenerator
import re
from django.contrib.auth import authenticate, login, logout

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

class PasswordValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        password = str(data.get('password'))

        # regex pattern
        string_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9]).+$"
        regex_pattern = re.compile(string_pattern)

        if len(password) < 8 or len(password) > 15:
            return JsonResponse({'password_error': 'password must have a length of 8 to 15 characters.'}, status=400)

        if len(regex_pattern.findall(password)) == 0:
            return JsonResponse({'password_error': 'password must contain at least one uppercase letter, lowercase letter and one numeric digit.'}, status=400)

        return JsonResponse({'password_valid': 'looks good!'})


class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):

        MIN_PASSWORD_LENGTH = 8
        MAX_PASSWORD_LENGTH = 15
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

        if len(password) < MIN_PASSWORD_LENGTH or len(password) > MAX_PASSWORD_LENGTH:
            messages.error(request, 'password must have a length of 8 to 15 characters.')
            error_count += 1

        # regex pattern
        string_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9]).+$"
        regex_pattern = re.compile(string_pattern)
        if len(regex_pattern.findall(str(password))) == 0:
            messages.error(request, 'password must contain at least one uppercase letter, lowercase letter and one numeric digit.')
            error_count += 1
        
        if error_count == 0:
            # Validation completed. Update Database.
            new_user = User.objects.create_user(username=username, email=email, password=password)
            new_user.is_active = False

            # URI path to UserActivationView class.
            # Users click on link in email inbox to activate account.
            current_site = get_current_site(request)
            current_site_domain = current_site.domain

            # user primary key is a unique user id
            uidb64_encoded = urlsafe_base64_encode(force_bytes(new_user.pk)) 
            token_generator = AppTokenGenerator()
            

            verification_link = reverse('activate-user', kwargs={'uidb64' : uidb64_encoded, 'token' : token_generator.make_token(new_user)})
            full_url_link = str('http://'+current_site_domain+verification_link)

            message_body = f"Welcome {new_user.username}!\n\nThanks for signing up with Example Expenses!\n\nYou must follow this link to activate your account: {full_url_link}"

            # Email Message
            activation_email = EmailMessage(
                'Confirm Your E-mail Address', 
                message_body,
                'lohzy@outlook.com',
                [str(email)], 
                reply_to=['helpdesk@exampleexpenses.com'],
            )

            # To debug if email send is unsuccessful
            try:
                activation_email.send(fail_silently=False)
                messages.success(request, 'account successfully created.')
                new_user.save()
            except:
                messages.warning(request, 'failed to send email. account activation unsuccessful.')
                new_user.delete()
            finally:
                context = { 'fieldValues' : None }

        else:
            context = { 'fieldValues' : request.POST }
            return render(request, 'authentication/register.html', context)
        
        return render(request, 'authentication/register.html', context)


class UserActivationView(View):
    def get(self, request, uidb64, token):

        try:

            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            token_generator = AppTokenGenerator()

            if token_generator.check_token(user, token) and not user.is_active:
                user.is_active = True
                user.save()
                messages.success(request, 'account activated successfully.')
        
        except Exception as e:
            pass
        finally:
            return redirect('login')

class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):

        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'please ensure that all fields are filled.')
        else:
            # read about authentication methods at https://docs.djangoproject.com/en/4.1/topics/auth/default/
            user = authenticate(username=username, password=password)
            user_isValid = user is not None

            if user_isValid and user.is_active:
                login(request, user)
                messages.success(request, f"Welcome, {user.get_username()}! You are successfully logged in.")
                return redirect('expenses-index')

            elif user_isValid and not user.is_active:
                messages.error(request, 'please activate your account via the link in the email sent.')
            else:
                messages.error(request, 'invalid username and/or password.')
        
        return redirect('login')

class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.success(request, f"You have logged out successfully.")
        return redirect('login')
