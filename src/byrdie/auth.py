from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.conf import settings

def login(request):
    if request.method == 'POST':
        # NOTE: This is a simplified login view for demonstration purposes.
        # In a real application, you would use a proper Django form for validation.
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            if remember_me:
                request.session.set_expiry(settings.SESSION_REMEMBER_ME_AGE)
            else:
                request.session.set_expiry(0)  # Session expires when browser closes
            return redirect('/')
        else:
            # Invalid login
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')
