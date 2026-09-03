from django.db import models
from django.contrib.auth.hashers import check_password, make_password


# models.py

from django.db import models

class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=128)
    Usuario_ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.nome

    @classmethod
    def autenticar(cls, email, senha):
        cliente = cls.objects.filter(email=email, Usuario_ativo=True).first()
        if cliente and check_password(senha, cliente.senha):
            return cliente
        return None

    @classmethod
    def cadastrar(cls, nome, email, senha):
        return cls.objects.create(
            nome=nome,
            email=email,
            senha=make_password(senha),
            Usuario_ativo=True,
        )


class Administrador(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=128)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'

    def __str__(self):
        return self.nome

    @classmethod
    def autenticar(cls, email, senha):
        admin = cls.objects.filter(email=email, ativo=True).first()
        if admin and check_password(senha, admin.senha):
            return admin
        return None

    def set_senha(self, senha):
        self.senha = make_password(senha)


class Mensagem(models.Model):
    mensagem = models.TextField()
    mensagem_da_ia = models.BooleanField(default=False)
    data_envio = models.DateTimeField(auto_now_add=True)
    chat_usuario = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='mensagens',
    )

    class Meta:
        verbose_name = 'Mensagem'
        verbose_name_plural = 'Mensagens'
        ordering = ['data_envio']

    def __str__(self):
        origem = 'IA' if self.mensagem_da_ia else 'Usuário'
        return f'{origem}: {self.mensagem[:50]}'

    @classmethod
    def cadastrar(cls, texto, da_ia, id_usuario):
        return cls.objects.create(
            mensagem=texto,
            mensagem_da_ia=da_ia,
            chat_usuario_id=id_usuario,
        )

    @classmethod
    def listar_por_usuario(cls, id_usuario):
        return cls.objects.filter(chat_usuario_id=id_usuario).order_by('data_envio')
