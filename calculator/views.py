from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from .forms import CalculationForm, RegistrationForm
from .models import Calculation


def register_view(request):
    if request.user.is_authenticated:
        return redirect('calculator:index')

    form = RegistrationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Добро пожаловать, {user.username}!')
        return redirect('calculator:index')

    return render(request, 'calculator/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('calculator:index')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'С возвращением, {user.username}!')
            return redirect('calculator:index')
        else:
            error = 'Неверный логин или пароль'

    return render(request, 'calculator/login.html', {'error': error})


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта')
    return redirect('calculator:login')


@login_required
def index(request):
    result = None
    calc_instance = None
    form = CalculationForm(request.POST or None)

    if form.is_valid():
        a = form.cleaned_data['num1']
        b = form.cleaned_data['num2']
        operation = form.cleaned_data['operation']

        error_msg = ''
        try:
            if operation == 'add':
                result = a + b
            elif operation == 'subtract':
                result = a - b
            elif operation == 'multiply':
                result = a * b
            elif operation == 'divide':
                if b == 0:
                    error_msg = 'Деление на ноль невозможно!'
                    result = None
                else:
                    result = a / b
            else:
                error_msg = 'Неизвестная операция'
                result = None
        except (OverflowError, ValueError) as e:
            error_msg = f'Ошибка вычисления: {e}'
            result = None

        Calculation.objects.create(
            user=request.user,
            num1=a,
            num2=b,
            operation=operation,
            result=result,
            error_message=error_msg,
        )

    return render(request, 'calculator/index.html', {
        'form': form,
        'result': result,
    })


@login_required
def profile_view(request):
    user = request.user
    calculations = user.calculations.all()[:50]

    total = user.calculations.count()
    today = user.calculations.filter(
        created_at__date=timezone.now().date()
    ).count()
    week = user.calculations.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()

    popular = (
        user.calculations
        .values('operation')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )
    popular_op = dict(Calculation.OPERATION_CHOICES).get(
        popular['operation'], '—'
    ) if popular else '—'

    return render(request, 'calculator/profile.html', {
        'calculations': calculations,
        'total': total,
        'today': today,
        'week': week,
        'popular_op': popular_op,
    })


@login_required
def clear_history(request):
    if request.method == 'POST':
        user.calculations.all().delete()
        messages.success(request, 'История очищена')
    return redirect('calculator:profile')
