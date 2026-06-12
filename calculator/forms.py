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

    def clean_num1(self):
        value = self.cleaned_data.get('num1')
        if value is not None and abs(value) > 1e15:
            raise forms.ValidationError('Число должно быть от -1 000 000 000 000 000 до 1 000 000 000 000 000')
        return value

    def clean_num2(self):
        value = self.cleaned_data.get('num2')
        if value is not None and abs(value) > 1e15:
            raise forms.ValidationError('Число должно быть от -1 000 000 000 000 000 до 1 000 000 000 000 000')
        return value


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
    