from datetime import datetime
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import TodoForm
from .models import Todo


def signup_user(request):
    form = UserCreationForm()

    if request.method == 'GET':
        return render(request, 'todo/signup_user.html', {'form': form})
    else:
        result = request.POST
        if result['password1'] == result['password2']:
            try:
                user = User.objects.create_user(result['username'], password=result['password1'])
                user.save()
                login(request, user)
                return redirect('current_todos')
            except IntegrityError:
                return render(request, 'todo/signup_user.html', {'form': form, 'error': 'User exist!'})
        else:
            return render(request, 'todo/signup_user.html', {'form': form, 'error': 'Passwords did not match!'})


@login_required
def current_todos(request):
    todos = Todo.objects.filter(user=request.user, end_date__isnull=True)
    return render(request, 'todo/current_todos.html', {'todos': todos})


@login_required
def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return render(request, 'todo/home.html')


def home(request):
    return render(request, 'todo/home.html')


def login_user(request):
    form = AuthenticationForm()

    if request.method == 'GET':
        return render(request, 'todo/login_user.html', {'form': form})
    else:
        result = request.POST
        user = authenticate(request, username=result['username'], password=result['password'])
        if user is None:
            return render(request, 'todo/login_user.html', {'form': form, 'error': 'Username and password did not match!'})
        else:
            login(request, user)
            return redirect('current_todos')


@login_required
def create_todo(request):
    form = TodoForm()
    if request.method == 'GET':
        return render(request, 'todo/create_todo.html', {'form': form})
    else:
        try:
            form = TodoForm(request.POST)
            new_todo = form.save(commit=False)
            new_todo.user = request.user
            new_todo.save()
            return redirect('current_todos')
        except ValueError:
            return render(request, 'todo/create_todo.html', {'form': form, 'error': 'Bad data in todo!'})


@login_required
def view_todo(request, todo_pk):
    todo_record = get_object_or_404(Todo, pk=todo_pk, user=request.user)

    if request.method == 'GET':
        form = TodoForm(instance=todo_record)
        return render(request, 'todo/view_todo.html', {'form': form, 'todo': todo_record})
    else:
        try:
            form = TodoForm(request.POST, instance=todo_record)
            form.save()
            return redirect('current_todos')
        except ValueError:
            return render(request, 'todo/view_todo.html', {'form': form, 'error': 'Bad data in todo!'})


@login_required
def complete_todo(request, todo_pk):
    todo_record = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo_record.end_date = datetime.now()
        todo_record.save()
        return redirect('current_todos')


@login_required
def delete_todo(request, todo_pk):
    todo_record = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo_record.delete()
        return redirect('current_todos')


@login_required
def completed_todos(request):
    todos = Todo.objects.filter(user=request.user, end_date__isnull=False).order_by('-end_date')
    return render(request, 'todo/completed_todos.html', {'todos': todos})

