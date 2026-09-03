from django import forms
from django.contrib.auth.hashers import make_password
from .models import Cliente, Administrador


class ClienteForm(forms.ModelForm):
    confirmar_senha = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repita a senha'}),
    )

    class Meta:
        model = Cliente
        fields = ['nome', 'email', 'senha']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Seu nome completo'}),
            'email': forms.EmailInput(attrs={'placeholder': 'seu@email.com'}),
            'senha': forms.PasswordInput(attrs={'placeholder': 'Crie uma senha'}),
        }

    def clean(self):
        dados = super().clean()
        senha = dados.get('senha')
        confirmar = dados.get('confirmar_senha')
        if senha and confirmar and senha != confirmar:
            raise forms.ValidationError('As senhas não conferem.')
        return dados


class AdminLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'admin@jarvas.com'}),
    )
    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Sua senha'}),
    )


class AdministradorForm(forms.ModelForm):
    confirmar_senha = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repita a senha'}),
        required=False,
    )

    class Meta:
        model = Administrador
        fields = ['nome', 'email', 'senha', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome do administrador'}),
            'email': forms.EmailInput(attrs={'placeholder': 'admin@jarvas.com'}),
            'senha': forms.PasswordInput(attrs={'placeholder': 'Senha de acesso'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'checkbox-ativo'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['senha'].required = False
            self.fields['confirmar_senha'].required = False

    def clean(self):
        dados = super().clean()
        senha = dados.get('senha')
        confirmar = dados.get('confirmar_senha')
        if senha or confirmar:
            if senha != confirmar:
                raise forms.ValidationError('As senhas não conferem.')
        elif not self.instance.pk:
            raise forms.ValidationError('Informe uma senha para o novo administrador.')
        return dados

    def save(self, commit=True):
        admin = super().save(commit=False)
        senha = self.cleaned_data.get('senha')
        if senha:
            admin.set_senha(senha)
        if commit:
            admin.save()
        return admin


class AdminPerfilForm(forms.ModelForm):
    confirmar_senha = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repita a senha'}),
        required=False,
    )

    class Meta:
        model = Administrador
        fields = ['nome', 'email', 'senha']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Seu nome'}),
            'email': forms.EmailInput(attrs={'placeholder': 'seu@email.com'}),
            'senha': forms.PasswordInput(attrs={'placeholder': 'Nova senha (opcional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['senha'].required = False
        self.fields['confirmar_senha'].required = False

    def clean(self):
        dados = super().clean()
        senha = dados.get('senha')
        confirmar = dados.get('confirmar_senha')
        if senha or confirmar:
            if senha != confirmar:
                raise forms.ValidationError('As senhas não conferem.')
        return dados

    def save(self, commit=True):
        admin = super().save(commit=False)
        senha = self.cleaned_data.get('senha')
        if senha:
            admin.set_senha(senha)
        if commit:
            admin.save()
        return admin


class ClienteAdminForm(forms.ModelForm):
    confirmar_senha = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repita a senha'}),
        required=False,
    )

    class Meta:
        model = Cliente
        fields = ['nome', 'email', 'senha', 'Usuario_ativo']
        labels = {
            'Usuario_ativo': 'Usuário ativo',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome do cliente'}),
            'email': forms.EmailInput(attrs={'placeholder': 'cliente@email.com'}),
            'senha': forms.PasswordInput(attrs={'placeholder': 'Nova senha (opcional na edição)'}),
            'Usuario_ativo': forms.CheckboxInput(attrs={'class': 'checkbox-ativo'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['senha'].required = False

    def clean(self):
        dados = super().clean()
        senha = dados.get('senha')
        confirmar = dados.get('confirmar_senha')
        if senha or confirmar:
            if senha != confirmar:
                raise forms.ValidationError('As senhas não conferem.')
        elif not self.instance.pk:
            raise forms.ValidationError('Informe uma senha para o novo cliente.')
        return dados

    def save(self, commit=True):
        cliente = super().save(commit=False)
        senha = self.cleaned_data.get('senha')
        if senha:
            cliente.senha = make_password(senha)
        if commit:
            cliente.save()
        return cliente
