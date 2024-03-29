from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreationForm


# Страница регистрации нового пользователя
class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'
