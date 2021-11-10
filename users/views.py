from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import CustomCreationForm


def sign_up(request):
    context = {}
    form = CustomCreationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('index')
    context['form'] = form
    return render(request, 'signup.html', context)
