# 🧮 Django Calc — калькулятор с личным кабинетом

Пошаговый гайд по созданию веб-калькулятора на Django с нуля.

**Статус проекта:** репозиторий создан, виртуальное окружение активировано, Django установлено, `requirements.txt` и `.gitignore` на месте. Теперь пишем сам проект.

---

## 📋 Содержание

1. [Шаг 1 — Создание Django-проекта](#шаг-1--создание-django-проекта)
2. [Шаг 2 — Создание приложения calculator](#шаг-2--создание-приложения-calculator)
3. [Шаг 3 — Регистрация приложения в настройках](#шаг-3--регистрация-приложения-в-настройках)
4. [Шаг 4 — Настройка языка и часового пояса](#шаг-4--настройка-языка-и-часового-пояса)
5. [Шаг 5 — Создание модели Calculation](#шаг-5--создание-модели-calculation)
6. [Шаг 6 — Создание форм](#шаг-6--создание-форм)
7. [Шаг 7 — Создание представлений (views)](#шаг-7--создание-представлений-views)
8. [Шаг 8 — Настройка URL-маршрутов](#шаг-8--настройка-url-маршрутов)
9. [Шаг 9 — Создание HTML-шаблонов](#шаг-9--создание-html-шаблонов)
10. [Шаг 10 — Миграции и суперпользователь](#шаг-10--миграции-и-суперпользователь)
11. [Шаг 11 — Запуск и проверка](#шаг-11--запуск-и-проверка)
12. [Шаг 12 — Сохранение зависимостей и коммит](#шаг-12--сохранение-зависимостей-и-коммит)
13. [Структура проекта](#структура-проекта)
14. [FAQ — решение частых проблем](#faq--решение-частых-проблем)

---

## Шаг 1 — Создание Django-проекта

Мы находимся в корне репозитория, виртуальное окружение уже активировано.

Команда `startproject` создаёт скелет Django-проекта — файлы настроек, точку входа и т.д. Точка в конце команды означает «создать проект в текущей директории» (без создания дополнительной вложенной папки).

```bash
django-admin startproject calc_project .
```

После выполнения появится структура:

```
calc_project/       ← директория с настройками проекта
├── __init__.py
├── settings.py     ← главный файл настроек
├── urls.py         ← главные URL-маршруты
├── wsgi.py
└── asgi.py
manage.py           ← скрипт для управления проектом
```

> **Что такое `manage.py`?** Это ваш главный инструмент разработчика. Через него запускается сервер, создаются миграции, управляется база данных и не только.

---

## Шаг 2 — Создание приложения calculator

В Django проект состоит из **приложений** (apps). Проект — это контейнер, а приложение — конкретная функциональность. У нас одна функциональность — калькулятор, значит одно приложение `calculator`.

```bash
python manage.py startapp calculator
```

Появится директория:

```
calculator/             ← наше приложение
├── __init__.py
├── admin.py            ← настройки админ-панели
├── apps.py             ← конфигурация приложения
├── models.py           ← описание моделей (таблиц БД)
├── views.py            ← логика обработки запросов
├── tests.py            ← тесты
└── migrations/         ← файлы миграций
    └── __init__.py
```

---

## Шаг 3 — Регистрация приложения в настройках

Django не «видит» приложения автоматически — их нужно явно зарегистрировать.

Открываем файл `calc_project/settings.py`, находим список `INSTALLED_APPS` и добавляем `'calculator'`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'calculator',  # ← добавляем наше приложение
]
```

> **Зачем это нужно?** Без этого Django не будет знать о существовании наших моделей, шаблонов и миграций из приложения `calculator`.

Также в том же файле добавляем в конец настройки авторизации:

```python
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
```

Эти строки указывают Django, куда перенаправлять пользователя при входе, выходе и при попытке доступа к защищённой странице без авторизации.

---

## Шаг 4 — Настройка языка и часового пояса

В файле `calc_project/settings.py` находим и меняем:

```python
LANGUAGE_CODE = 'ru-ru'          # было 'en-us'
TIME_ZONE = 'Europe/Moscow'      # было 'UTC'
```

Теперь админ-панель и все системные сообщения будут на русском языке, а даты — в московском часовом поясе.

---

## Шаг 5 — Создание модели Calculation

**Модель** — это Python-класс, который описывает таблицу в базе данных. Мы будем сохранять каждое вычисление, чтобы пользователь мог просматривать историю в личном кабинете.

Открываем `calculator/models.py` и заменяем всё содержимое:

```python
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Calculation(models.Model):
    OPERATION_CHOICES = [
        ('add', '➕ Сложение'),
        ('subtract', '➖ Вычитация'),
        ('multiply', '✖️ Умножение'),
        ('divide', '➗ Деление'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calculations')
    num1 = models.FloatField(validators=[MinValueValidator(-1e15), MaxValueValidator(1e15)])
    num2 = models.FloatField(validators=[MinValueValidator(-1e15), MaxValueValidator(1e15)])
    operation = models.CharField(max_length=10, choices=OPERATION_CHOICES)
    result = models.FloatField(null=True, blank=True)
    error_message = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        op = dict(self.OPERATION_CHOICES).get(self.operation, self.operation)
        return f'{self.num1} {op} {self.num2} = {self.result if self.error_message == "" else self.error_message}'
```

**Что здесь происходит:**

| Элемент | Описание |
|---------|----------|
| `user` | Связь с пользователем — каждое вычисление «принадлежит» конкретному юзеру |
| `num1`, `num2` | Операнды — числа с плавающей точкой с ограничением по диапазону |
| `operation` | Тип операции: сложение, вычитание, умножение или деление |
| `result` | Результат вычисления (может быть `null` при ошибке) |
| `error_message` | Текст ошибки, если что-то пошло не так (деление на ноль и т.д.) |
| `created_at` | Дата и время создания, заполняется автоматически |
| `ordering = ['-created_at']` | Сортировка по убыванию даты — свежие вычисления сверху |

---

## Шаг 6 — Создание форм

**Форма** в Django — это класс, который описывает поля ввода, их валидацию и отображение. Создадим две формы: для калькулятора и для регистрации.

Создаём файл `calculator/forms.py`:

```python
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Calculation


class CalculationForm(forms.Form):
    OPERATION_CHOICES = Calculation.OPERATION_CHOICES

    num1 = forms.FloatField(
        label='Первое число',
        widget=forms.NumberInput(attrs={
            'step': 'any',
            'placeholder': 'Введите число',
            'class': 'form-input',
        }),
        min_value=-1e15,
        max_value=1e15,
        error_messages={
            'required': 'Введите первое число',
            'invalid': 'Введите корректное число',
            'min_value': 'Число слишком малое',
            'max_value': 'Число слишком большое',
        },
    )
    num2 = forms.FloatField(
        label='Второе число',
        widget=forms.NumberInput(attrs={
            'step': 'any',
            'placeholder': 'Введите число',
            'class': 'form-input',
        }),
        min_value=-1e15,
        max_value=1e15,
        error_messages={
            'required': 'Введите второе число',
            'invalid': 'Введите корректное число',
            'min_value': 'Число слишком малое',
            'max_value': 'Число слишком большое',
        },
    )
    operation = forms.ChoiceField(
        label='Операция',
        choices=OPERATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
    )


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'email@example.com', 'class': 'form-input'}),
        error_messages={'required': 'Введите email'},
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Логин', 'class': 'form-input'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Пароль', 'class': 'form-input'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Подтвердите пароль', 'class': 'form-input'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Этот email уже зарегистрирован')
        return email
```

**Что здесь происходит:**

| Форма | Назначение |
|-------|------------|
| `CalculationForm` | Два числовых поля (num1, num2) + выпадающий список операции. Все поля обязательны, с валидацией типа и диапазона |
| `RegistrationForm` | Наследуется от встроенной `UserCreationForm` (логин + пароль с подтверждением), добавлено поле email с проверкой уникальности |

> **Зачем нужны формы вместо обычных HTML-полей?** Django-формы автоматически проверяют данные (числа ли это? не пустые ли поля? email корректен?), выводят понятные ошибки на русском языке и защищот от CSRF-атак.

---

## Шаг 7 — Создание представлений (views)

**Представление (view)** — это функция, которая принимает HTTP-запрос и возвращает ответ. Нам нужно пять представлений: калькулятор, регистрация, вход, выход и профиль.

Открываем `calculator/views.py` и заменяем содержимое:

```python
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
```

**Что здесь происходит:**

| Функция | Что делает |
|---------|------------|
| `register_view` | Отображает форму регистрации. При валидном .POST создаёт пользователя и сразу авторизует |
| `login_view` | Показывает форму входа. Проверяет логин/пароль через `authenticate()` |
| `logout_view` | Завершает сессию и перенаправляет на страницу входа |
| `index` | Калькулятор: обрабатывает форму, вычисляет результат, сохраняет в БД. Доступ только по авторизации (`@login_required`) |
| `profile_view` | Личный кабинет: показывает последние 50 вычислений и статистику (всего, сегодня, за неделю, популярная операция) |
| `clear_history` | Очищает историю вычислений текущего пользователя (только по POST-запросу) |

> **Что такое `@login_required`?** Это декоратор — он проверяет, авторизован ли пользователь. Если нет — автоматически перенаправляет на страницу входа.

---

## Шаг 8 — Настройка URL-маршрутов

URL-маршруты определяют, какая функция (view) будет обрабатывать запрос на определённый адрес.

**8.1 — Создаём `calculator/urls.py`** (файл маршрутов приложения):

```python
from django.urls import path
from . import views

app_name = 'calculator'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/clear/', views.clear_history, name='clear_history'),
]
```

**8.2 — Подключаем маршруты приложения в главном файле `calc_project/urls.py`:**

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('calculator.urls')),  # ← подключаем URL-ы приложения calculator
]
```

**Какие адреса получились:**

| URL | Представление | Описание |
|-----|---------------|----------|
| `/` | `index` | Калькулятор |
| `/register/` | `register_view` | Регистрация |
| `/login/` | `login_view` | Вход |
| `/logout/` | `logout_view` | Выход |
| `/profile/` | `profile_view` | Личный кабинет |
| `/admin/` | admin.site.urls | Админ-панель Django |

---

## Шаг 9 — Создание HTML-шаблонов

Шаблоны хранятся в папках `templates/` внутри приложений.

**9.1 — Создаём структуру директорий:**

```bash
mkdir calculator\templates\calculator
```

**9.2 — Базовый шаблон `calculator/templates/calculator/base.html`.**

Это общий шаблон для всех страниц — навигация, стили, flash-сообщения. Все остальные шаблоны будут наследоваться от него через `{% extends %}`:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Калькулятор{% endblock %}</title>
    <style>
        /* Все стили проекта: градиентный фон, карточки, формы, навигация */
        /* (см. файл calculator/templates/calculator/base.html в репозитории) */
    </style>
</head>
<body>
    <nav>
        <a href="{% url 'calculator:index' %}" class="brand">🧮 CalcApp</a>
        <div class="nav-links">
            {% if user.is_authenticated %}
                <a href="{% url 'calculator:index' %}">Калькулятор</a>
                <span class="user-badge">👤 {{ user.username }}</span>
                <a href="{% url 'calculator:profile' %}">Профиль</a>
                <a href="{% url 'calculator:logout' %}">Выйти</a>
            {% else %}
                <a href="{% url 'calculator:login' %}">Войти</a>
                <a href="{% url 'calculator:register' %}">Регистрация</a>
            {% endif %}
        </div>
    </nav>

    {% if messages %}
    <div class="messages">
        {% for msg in messages %}
            <div class="msg {{ msg.tags }}">{{ msg }}</div>
        {% endfor %}
    </div>
    {% endif %}

    <div class="content">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
```

**9.3 — Страница калькулятора `calculator/templates/calculator/index.html`.**

Содержит форму с двумя числовыми полями и выбором операции. Результат отображается после отправки:

```html
{% extends "calculator/base.html" %}
{% block title %}Калькулятор{% endblock %}
{% block content %}
<div class="card">
    <h1>🧮 Калькулятор</h1>
    <form method="post">
        {% csrf_token %}
        {% for field in form %}
        <div class="form-group">
            <label for="{{ field.id_for_label }}">{{ field.label }}</label>
            {{ field }}
            {% if field.errors %}
            <ul class="field-errors">
                {% for err in field.errors %}<li>⚠️ {{ err }}</li>{% endfor %}
            </ul>
            {% endif %}
        </div>
        {% endfor %}
        <button class="btn" type="submit">Вычислить</button>
    </form>
    {% if result is not None %}
    <div class="result-box">
        <p>Результат:</p>
        <p class="value">{{ result }}</p>
    </div>
    {% endif %}
</div>
{% endblock %}
```

**9.4 — Страница входа `calculator/templates/calculator/login.html`.**

Простая форма «логин + пароль» с обработкой ошибок авторизации.

**9.5 — Страница регистрации `calculator/templates/calculator/register.html`.**

Форма с полями логин, email, пароль и подтверждение пароля. Валидируется на стороне Django через `RegistrationForm`.

**9.6 — Профиль `calculator/templates/calculator/profile.html`.**

Личный кабинет: блок статистики (4 карточки) + таблица последних 50 вычислений с кнопкой «Очистить историю».

Создайте все пять файлов, скопировав полное содержимое из репозитория. Все CSS-стили уже встроены в `base.html`.

> **Что такое `{% csrf_token %}`?** Это защита от CSRF-атак (межсайтовая подделка запроса). Django требует этот токен в каждой POST-форме — без неё форма просто не отправится.

---

## Шаг 10 — Миграции и суперпользователь

Миграции — это механизм Django для синхронизации моделей (код Python) и базы данных (таблицы SQL).

**10.1 — Создать файл миграции:**

```bash
python manage.py makemigrations calculator
```

Результат:
```
Migrations for 'calculator':
  calculator/migrations/0001_initial.py
    + Create model Calculation
```

**10.2 — Применить миграцию:**

```bash
python manage.py migrate
```

Результат — список применённых миграций, каждая со статусом `OK`:
```
Applying calculator.0001_initial... OK
```

> **Когда запускать миграции?**
> - При первом запуске проекта
> - После каждого изменения моделей (добавление/изменение/удаление полей)
> - После `git pull`, если кто-то из команды изменил модели

**10.3 — Создать суперпользователя для доступа к админ-панели:**

```bash
python manage.py createsuperuser
```

Вводим данные (при вводе пароля символы **не отображаются** — это нормально):

```
Username: admin
Email address: admin@example.com
Password: ********
Password (again): ********
Superuser created successfully.
```

---

## Шаг 11 — Запуск и проверка

**11.1 — Запускаем сервер:**

```bash
python manage.py runserver
```

При успешном запуске:
```
System check identified no issues (0 silenced).
Django version 6.0.5, using settings 'calc_project.settings'
Starting development server at http://127.0.0.1:8000/
```

**11.2 — Проверяем в браузере:**

| Что проверяем | URL | Ожидаемый результат |
|---------------|-----|---------------------|
| Редирект на логин | http://127.0.0.1:8000/ | Страница входа |
| Регистрация | http://127.0.0.1:8000/register/ | Форма регистрации |
| Вход | http://127.0.0.1:8000/login/ | Форма входа |
| Админ-панель | http://127.0.0.1:8000/admin/ | Форма входа в админку |

**11.3 — Проверяем сценарий:**

1. Регистрируем нового пользователя (`/register/`)
2. Автоматически попадаем на калькулятор (`/`)
3. Вводим два числа, выбираем операцию, нажимаем «Вычислить»
4. Видим результат
5. Переходим в профиль (`/profile/`) — видим статистику и запись в истории
6. Выходим (`/logout/`) — снова на странице входа
7. Пытаемся открыть `/` — снова редирект на логин

🎉 **Приложение работает!**

---

## Шаг 12 — Сохранение зависимостей и коммит

**12.1 — Сохраняем список зависимостей в `requirements.txt`:**

```bash
pip freeze > requirements.txt
```

Эта команда записывает все установленные пакеты с точными версиями. Теперь любой разработчик сможет восстановить окружение командой:

```bash
pip install -r requirements.txt
```

**12.2 — Коммитим изменения:**

```bash
git add .
git commit -m "feat: калькулятор с личным кабинетом

- Создан проект calc_project и приложение calculator
- Модель Calculation для хранения истории вычислений
- Регистрация, вход и выход пользователей (django auth)
- Калькулятор с валидацией форм (сложение, вычитание, умножение, деление)
- Личный кабинет: статистика + история вычислений
- Flash-сообщения, базовый шаблон с навигацией, CSS-стили"
```

---

## 📁 Структура проекта

Итоговая структура после всех шагов:

```
django_calc/
├── .venv/                         # Виртуальное окружение (в .gitignore!)
├── .git/
├── .gitignore
├── manage.py                      # Скрипт управления проектом
├── README.md                      # Этот файл
├── requirements.txt               # Зависимости Python
│
├── calc_project/                  # Настройки проекта
│   ├── __init__.py
│   ├── settings.py               # INSTALLED_APPS, БД, язык, LOGIN_URL...
│   ├── urls.py                   # Главные URL-маршруты (admin + calculator)
│   ├── wsgi.py
│   └── asgi.py
│
├── calculator/                    # Приложение «Калькулятор»
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py                  # CalculationForm, RegistrationForm
│   ├── models.py                 # Модель Calculation
│   ├── views.py                  # index, register, login, logout, profile, clear_history
│   ├── urls.py                   # URL-маршруты приложения
│   ├── tests.py
│   └── migrations/
│       ├── __init__.py
│       └── 0001_initial.py      # Создание таблицы Calculation
│
├── calculator/templates/          # HTML-шаблоны
│   └── calculator/
│       ├── base.html             # Базовый шаблон (стили, навигация, flash)
│       ├── index.html            # Калькулятор
│       ├── login.html            # Вход
│       ├── register.html         # Регистрация
│       └── profile.html          # Личный кабинет + история
│
└── db.sqlite3                    # База данных SQLite (создаётся при migrate)
```

---

## ❓ FAQ — решение частых проблем

### `'python' is not recognized as an internal or external command`
Python не добавлен в PATH. На Windows попробуйте `py` вместо `python`.

### `No module named 'django'`
Забыли активировать виртуальное окружение или установить Django:
```bash
.venv\Scripts\activate
pip install django
```

### `You have unapplied migrations`
Забыли применить миграции:
```bash
python manage.py migrate
```

### `Forbidden (403) at /`
Забыли `{% csrf_token %}` в форме. Без него Django блокирует POST-запросы.

### `No reverse with name 'index'`
Ошибка в URL-имени. Проверьте, что `app_name = 'calculator'` указан в `calculator/urls.py`, а в шаблоне используется `{% url 'calculator:index' %}`.

### `OperationalError: no such table: calculator_calculation`
Миграция не применена. Выполните:
```bash
python manage.py makemigrations calculator
python manage.py migrate
```

### `Error: That port is already in use`
Порт 8000 занят. Запустите на другом:
```bash
python manage.py runserver 9000
```

### Страница открывается, но выглядит «голой» (без стилей)
Убедитесь, что шаблон наследуется от `base.html` через `{% extends "calculator/base.html" %}` и файл лежит в `calculator/templates/calculator/base.html`.

### Профиль пустой — история не сохраняется
Проверьте, что во view `index` происходит `Calculation.objects.create(...)`. Также убедитесь, что пользователь авторизован — анонимные вычисления не сохраняются.

### Ничего не работает — что делать?
Выполните всё по порядку с нуля:
```bash
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations calculator
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Если проблема сохраняется — скопируйте **полный текст ошибки из терминала** и обратитесь к преподавателю.

---

## 📚 Полезные ссылки

- [Документация Django (EN)](https://docs.djangoproject.com/)
- [Документация Django (RU)](https://djangoproject.ru/) — неполная, но полезная
- [Документация по Django Forms](https://docs.djangoproject.com/en/6.0/topics/forms/)
- [Документация по AUTH](https://docs.djangoproject.com/en/6.0/topics/auth/)
- [Про CSRF-защиту](https://docs.djangoproject.com/en/6.0/ref/csrf/)

---

*Проект создан в учебных целях. Приятного изучения Django! 🎓*
