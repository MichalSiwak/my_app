import verify_email.models
from userpanel.forms import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage
from django.views import View
from django.db import transaction
from django.shortcuts import render, redirect
from verify_email.email_handler import send_verification_email
from django.conf import settings
from django.template.loader import render_to_string


class TestView(View):
    def get(self, request):
        users = User.objects.all()
        print(users)
        for user in users:
            print(user.pk, user.natural_key())

        em = verify_email.models.LinkCounter.objects.all()
        print(em)
        for i in em:
            print(i.requester, i.sent_count)
        return render(request, 'test.html')

    def post(self, request):
        template = render_to_string('email_template.html')

        email = EmailMessage(
            'Tytuł maila testowego',
            template,
            settings.EMAIL_HOST_USER,
            ['michal_siwak@o2.pl'],
        )

        email.fail_silently = False
        email.send()

        return redirect('/test')


class IndexView(View):
    def get(self, request):
        if request.user.is_authenticated:
            user_name = request.user
            login = True
            print(login)
            return render(request, 'index.html', {'user_name': user_name, 'login': login})
        else:
            login = False
            print(login)
            return render(request, 'index.html')



# ----------------------users view--------------------------------


class RegisterView(View):
    def get(self, request):
        form = RegisterUserForm()
        register = True
        return render(request, 'register.html', {'form': form, 'register': register})

    @transaction.atomic
    def post(self, request):
        form = RegisterUserForm(request.POST)

        if form.errors:
            messages.error(request, next(iter(form.errors.values())))
            return redirect('/register')

        if not form.is_valid():
            return redirect('/register')

        form.save()
        send_verification_email(request, form)
        messages.info(request, 'Rejestracja przebiegła pomyślnie.')
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

            username = request.POST["username"]
            password = request.POST["password"]
            # new = User.objects.get(username=username)

            if user is not None:
                login(request, user)
                return redirect('home')

            # elif new and new.check_password(password):
            #     messages.error(request, 'Email nie został zweryfikowany')
            #     return render(request, 'login.html', {'form': form})

            else:
                messages.error(request, 'Błędny login lub hasło')
                return render(request, 'login.html', {'form': form})
        else:
            messages.error(request, 'Nastąpił błąd. Skontaktuj sie z nami!!!')
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
        login = True
        return render(request, 'user.html', {'form': form, 'login': login})


class EditProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        # user_name = User.objects.get(id=user.id)
        login = True

        form = EditProfileForm(initial={"username": user.username,
                                        "first_name": user.first_name,
                                        "last_name": user.last_name,
                                        "email": user.email})
        # return render(request, 'edit_profile.html', {'login': login, 'form': form})

        return render(request, 'edit_profile.html', {'login': login, 'form': form})

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
        else:
            User.objects.filter(id=user.id).update(username=username,
                                                   first_name=first_name,
                                                   last_name=last_name, email=email)
        return redirect('edit_profile')
