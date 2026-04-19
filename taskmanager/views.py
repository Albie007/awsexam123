from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q

from .models import Task, Category
from .forms import RegisterForm, LoginForm, TaskForm, CategoryForm


# ──────────────────────────────────────────────
#  Auth
# ──────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Welcome, {user.username}! Account created.')
        return redirect('dashboard')
    return render(request, 'taskmanager/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Welcome back, {user.username}!')
        return redirect('dashboard')
    return render(request, 'taskmanager/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# ──────────────────────────────────────────────
#  Dashboard
# ──────────────────────────────────────────────

@login_required
def dashboard(request):
    tasks = Task.objects.filter(owner=request.user)

    # Filter
    status   = request.GET.get('status', '')
    priority = request.GET.get('priority', '')
    search   = request.GET.get('q', '')

    if status:
        tasks = tasks.filter(status=status)
    if priority:
        tasks = tasks.filter(priority=priority)
    if search:
        tasks = tasks.filter(Q(title__icontains=search) | Q(description__icontains=search))

    # Stats
    stats = {
        'total':       Task.objects.filter(owner=request.user).count(),
        'todo':        Task.objects.filter(owner=request.user, status='todo').count(),
        'in_progress': Task.objects.filter(owner=request.user, status='in_progress').count(),
        'done':        Task.objects.filter(owner=request.user, status='done').count(),
    }

    context = {
        'tasks':      tasks,
        'stats':      stats,
        'categories': Category.objects.all(),
        'status':     status,
        'priority':   priority,
        'search':     search,
    }
    return render(request, 'taskmanager/dashboard.html', context)


# ──────────────────────────────────────────────
#  Tasks
# ──────────────────────────────────────────────

@login_required
def task_create(request):
    form = TaskForm(request.POST or None)
    if form.is_valid():
        task = form.save(commit=False)
        task.owner = request.user
        task.save()
        messages.success(request, 'Task created successfully!')
        return redirect('dashboard')
    return render(request, 'taskmanager/task_form.html', {'form': form, 'action': 'Create'})


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    form = TaskForm(request.POST or None, instance=task)
    if form.is_valid():
        form.save()
        messages.success(request, 'Task updated!')
        return redirect('dashboard')
    return render(request, 'taskmanager/task_form.html', {'form': form, 'action': 'Edit', 'task': task})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted.')
        return redirect('dashboard')
    return render(request, 'taskmanager/task_confirm_delete.html', {'task': task})


@login_required
def task_toggle(request, pk):
    """Quick toggle: todo → in_progress → done → todo"""
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    cycle = {'todo': 'in_progress', 'in_progress': 'done', 'done': 'todo'}
    task.status = cycle.get(task.status, 'todo')
    task.save()
    return redirect('dashboard')


# ──────────────────────────────────────────────
#  Categories
# ──────────────────────────────────────────────

@login_required
def category_list(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Category added!')
        return redirect('categories')
    categories = Category.objects.annotate(task_count=Count('task'))
    return render(request, 'taskmanager/categories.html', {'form': form, 'categories': categories})


@login_required
def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        cat.delete()
        messages.success(request, 'Category deleted.')
    return redirect('categories')
