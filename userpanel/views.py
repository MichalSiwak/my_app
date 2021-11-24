from django.contrib.auth.hashers import check_password
from django.contrib.messages import get_messages

from userpanel.forms import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.views import View
from django.db import transaction
from django.shortcuts import render, redirect
from verify_email.email_handler import send_verification_email


class TestView(View):
    @staticmethod
    def get(request):
        form = RegisterForm()
        return render(request, 'test.html', {'form': form})

    @staticmethod
    def post(request):
        form = RegisterForm(request.POST)

        if form.errors:
            messages.error(request, next(iter(form.errors.values())))
            return redirect('/register')

        if not form.is_valid():
            return redirect('/register')

        messages.info(request, 'Rejestracja przebiegła pomyślnie.')
        return redirect('login')


class IndexView(View):
    def get(self, request):
        if request.user.is_authenticated:
            user_name = request.user
            return render(request, 'index.html', {'user_name': user_name, 'is_active': request.user.is_authenticated})
        else:
            return render(request, 'index.html')


# ----------------------users view--------------------------------


class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        register = True
        return render(request, 'register.html', {'form': form, 'register': register})

    @transaction.atomic
    def post(self, request):
        form = RegisterForm(request.POST)

        if form.errors:
            messages.error(request, form.errors)
            # messages.error(request, next(iter(form.errors.values())))
            return redirect('/register')

        if not form.is_valid():
            return redirect('/register')

        form.save()
        send_verification_email(request, form)
        messages.info(request, 'Rejestracja przebiegła prawidłowo. Sprawdź skrzynkę mailową. '
                               'Otrzymałeś link aktywacyjny.')
        return redirect('login')


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        user = request.user
        return render(request, 'login.html', {'form': form, 'user': user, 'login': login})

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            user = authenticate(**form.cleaned_data)

            if user is not None:
                login(request, user)
                return redirect('home')

            else:
                messages.info(request, 'Błędny login lub hasło')
                return render(request, 'login.html', {'form': form})
        else:
            messages.info(request, 'Nastąpił błąd. Skontaktuj sie z nami!!!')
            return redirect('home')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')


# _____________________________


class UserView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        form = User.objects.get(id=user.id)
        is_active = user.is_active
        return render(request, 'user.html', {'form': form, 'is_active': is_active})


class EditProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        is_active = user.is_active
        form = EditProfileForm(initial={"username": user.username,
                                        "first_name": user.first_name,
                                        "last_name": user.last_name,
                                        "email": user.email})

        return render(request, 'edit_profile.html', {'is_active': is_active, 'form': form})

    def post(self, request):
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        user = request.user

        if request.FILES:
            myfile = request.FILES['profile_picture']
            fs = FileSystemStorage()
            profile_picture = f"{user.username}_pp.jpg"
            fs.delete(profile_picture)
            filename = fs.save(profile_picture, myfile)
            fs.url(filename)
            User.objects.filter(id=user.id).update(username=username,
                                                   profile_picture=profile_picture,
                                                   first_name=first_name,
                                                   last_name=last_name, email=email)

        elif User.objects.filter(username=username) and username != user.username:
            form = EditProfileForm(initial={"username": user.username,
                                            "first_name": user.first_name,
                                            "last_name": user.last_name,
                                            "email": user.email})
            is_active = user.is_active
            messages.info(request, 'Login zajęty. Wybierz inny.')
            return render(request, 'edit_profile.html', {'is_active': is_active, 'form': form})

        else:
            User.objects.filter(id=user.id).update(username=username,
                                                   first_name=first_name,
                                                   last_name=last_name, email=email)
        return redirect('edit_profile')


class EditPasswordView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        is_active = user.is_active
        form = EditPasswordForm(request.user, request.POST)
        return render(request, 'edit_password.html', {"form": form, "user": user, "is_active": is_active})

    def post(self, request):
        form = EditPasswordForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)

            messages.success(request, 'Hasło zmienione poprawnie!')
            return redirect('edit_password')

        else:
            messages.info(request, form.error_messages.values())
            return redirect('edit_password')


class MailChangeView(LoginRequiredMixin, View):
    def get(self, request):
        form = ChangeEmailForm()
        user = request.user
        is_active = user.is_active
        return render(request, 'change_mail.html', {'form': form, 'is_active': is_active})

    def post(self, request):
        form = ChangeEmailForm(request.user, request.POST)
        password = request.POST['password']
        email = request.POST['email']
        user = request.user

        print(check_password(password, user.password))
        # if password != user.set_unusable_password():

        #     messages.info(request, 'Na nowy adres mailowy otrzymałeś wiadomość z linkiem aktywującym nowy adfres e-mail.')
        #     return redirect('change_mail')


        return redirect('change_mail')
