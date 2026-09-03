from django.db import migrations
from django.contrib.auth.hashers import make_password


def criar_admin_padrao(apps, schema_editor):
    Administrador = apps.get_model('APP', 'Administrador')
    email = 'fl2646730@gmail.com'

    if Administrador.objects.filter(email=email).exists():
        return

    Administrador.objects.create(
        nome='Administrador',
        email=email,
        senha=make_password('12345678'),
        ativo=True,
    )


def remover_admin_padrao(apps, schema_editor):
    Administrador = apps.get_model('APP', 'Administrador')
    Administrador.objects.filter(email='fl2646730@gmail.com').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('APP', '0003_administrador_alter_cliente_options_and_more'),
    ]

    operations = [
        migrations.RunPython(criar_admin_padrao, remover_admin_padrao),
    ]
