from byrdie import route, runserver
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

@route()
def index(request):
    if request.user.is_authenticated:
        return {'message': f'Welcome, {request.user.username}!', 'user': request.user}
    else:
        return redirect('/login/')

@route('/login/')
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

@route(is_authenticated=True)
def profile(request):
    return {'message': 'This is protected content.', 'user': request.user}

if __name__ == '__main__':
    runserver()
