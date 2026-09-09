import os
import sys

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from django.utils.html import escape

from .forms import AdminLoginForm, AdministradorForm, AdminPerfilForm, ClienteAdminForm, ClienteForm
from .models import Cliente, Administrador, Mensagem

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

_ia_instance = None
_ia_erro = None


def get_ia():
    global _ia_instance, _ia_erro
    if _ia_instance is not None:
        return _ia_instance
    if _ia_erro is not None:
        raise RuntimeError(_ia_erro)
    try:
        from IA.InteligenciaArtificial import InteligenciaArtificial
        _ia_instance = InteligenciaArtificial()
        return _ia_instance
    except Exception as exc:
        _ia_erro = str(exc)
        raise RuntimeError(_ia_erro) from exc


def get_ia_info():
    try:
        from IA.backend import info_backend
        return info_backend()
    except Exception as exc:
        return f"Indisponível ({exc})"


def formatar_bloco_codigo(conteudo):
    conteudo = conteudo.lstrip('\n').rstrip('\n')
    linhas = conteudo.split('\n')
    linguagem = 'código'
    codigo = conteudo

    primeira = linhas[0].strip() if linhas else ''
    if primeira and ' ' not in primeira and len(primeira) <= 20:
        linguagem = primeira
        codigo = '\n'.join(linhas[1:]).rstrip('\n')

    return (
        '<div class="codigo-bloco">'
        '<div class="codigo-header">'
        '<div class="codigo-dots">'
        '<span class="dot dot-red"></span>'
        '<span class="dot dot-yellow"></span>'
        '<span class="dot dot-green"></span>'
        '</div>'
        f'<span class="codigo-lang">{escape(linguagem)}</span>'
        '</div>'
        f'<pre class="codigo-pre"><code>{escape(codigo)}</code></pre>'
        '</div>'
    )


def formatar_conteudo_mensagem(texto, da_ia=False):
    if not da_ia or '```' not in texto:
        return f'<p class="mensagem-texto">{escape(texto)}</p>'

    partes = texto.split('```')
    blocos = []

    for indice, parte in enumerate(partes):
        if not parte:
            continue
        if indice % 2 == 0:
            blocos.append(f'<p class="mensagem-texto">{escape(parte)}</p>')
        else:
            blocos.append(formatar_bloco_codigo(parte))

    return ''.join(blocos)


def renderizar_mensagens(mensagens):
    html = ''
    for msg in mensagens:
        css = 'mensagem-ia' if msg.mensagem_da_ia else 'mensagem-usuario'
        conteudo = formatar_conteudo_mensagem(msg.mensagem, msg.mensagem_da_ia)
        html += f'<div class="mensagem {css}">{conteudo}</div>'
    return html


def login_required_cliente(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('cliente_id'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def login_required_admin(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('admin_id'):
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def home(request):
    return redirect('login')


def login(request):
    if request.session.get('cliente_id'):
        return redirect('chat')

    mensagem = ''
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('password')
        cliente = Cliente.autenticar(email, senha)
        if cliente:
            request.session['cliente_id'] = cliente.id
            request.session['cliente_nome'] = cliente.nome
            return redirect('chat')
        mensagem = 'Email ou senha inválidos.'

    return render(request, 'index.html', {'mensagem': mensagem})


def cadastro(request):
    if request.session.get('cliente_id'):
        return redirect('chat')

    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conta criada com sucesso! Faça login para continuar.')
            return redirect('login')
    else:
        form = ClienteForm()

    return render(request, 'formes.html', {'form': form})


def logout_cliente(request):
    request.session.flush()
    return redirect('login')


@login_required_cliente
def chat(request):
    cliente_id = request.session['cliente_id']
    cliente_nome = request.session.get('cliente_nome', 'Usuário')

    if request.method == 'POST':
        texto = request.POST.get('mensagem', '').strip()
        if texto:
            Mensagem.cadastrar(texto, False, cliente_id)
            try:
                resposta = get_ia().inferencia(texto)
                Mensagem.cadastrar(resposta, True, cliente_id)
            except RuntimeError as exc:
                messages.error(
                    request,
                    f'IA indisponível: {exc}',
                )

    conversas = Mensagem.listar_por_usuario(cliente_id)
    ia_ativa = _ia_instance is not None
    return render(request, 'chat.html', {
        'cliente_nome': cliente_nome,
        'conversas_html': renderizar_mensagens(conversas),
        'ia_info': get_ia_info() if not ia_ativa else _ia_instance.device_descricao,
        'ia_carregada': ia_ativa,
    })


def admin_login(request):
    if request.session.get('admin_id'):
        return redirect('admin_dashboard')

    form = AdminLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        admin = Administrador.autenticar(
            form.cleaned_data['email'],
            form.cleaned_data['senha'],
        )
        if admin:
            request.session['admin_id'] = admin.id
            request.session['admin_nome'] = admin.nome
            return redirect('admin_dashboard')
        messages.error(request, 'Credenciais de administrador inválidas.')

    return render(request, 'admin/login.html', {'form': form})


def admin_logout(request):
    request.session.pop('admin_id', None)
    request.session.pop('admin_nome', None)
    return redirect('admin_login')


@login_required_admin
def admin_dashboard(request):
    return render(request, 'admin/dashboard.html', {
        'total_clientes': Cliente.objects.count(),
        'total_admins': Administrador.objects.count(),
        'total_mensagens': Mensagem.objects.count(),
    })


@login_required_admin
def admin_clientes_list(request):
    clientes = Cliente.objects.all().order_by('-id')
    return render(request, 'admin/clientes_list.html', {'clientes': clientes})


@login_required_admin
@require_http_methods(['POST'])
def admin_cliente_toggle(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    cliente.Usuario_ativo = not cliente.Usuario_ativo
    cliente.save()
    status = 'ativado' if cliente.Usuario_ativo else 'desativado'
    messages.success(request, f'Usuário {cliente.nome} {status} com sucesso.')
    return redirect('admin_clientes_list')


@login_required_admin
def admin_cliente_create(request):
    form = ClienteAdminForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cliente cadastrado com sucesso.')
        return redirect('admin_clientes_list')
    return render(request, 'admin/cliente_form.html', {
        'form': form,
        'titulo': 'Novo Usuário',
    })


@login_required_admin
def admin_cliente_edit(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    form = ClienteAdminForm(request.POST or None, instance=cliente)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cliente atualizado com sucesso.')
        return redirect('admin_clientes_list')
    return render(request, 'admin/cliente_form.html', {
        'form': form,
        'titulo': f'Editar: {cliente.nome}',
        'objeto': cliente,
    })


@login_required_admin
@require_http_methods(['GET', 'POST'])
def admin_cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente removido com sucesso.')
        return redirect('admin_clientes_list')
    return render(request, 'admin/confirm_delete.html', {
        'objeto': cliente,
        'tipo': 'cliente',
        'voltar_url': 'admin_clientes_list',
    })


@login_required_admin
def admin_admins_list(request):
    admins = Administrador.objects.all().order_by('-id')
    return render(request, 'admin/admins_list.html', {
        'admins': admins,
        'admin_logado_id': request.session.get('admin_id'),
    })


@login_required_admin
@require_http_methods(['POST'])
def admin_admin_toggle(request, pk):
    admin = get_object_or_404(Administrador, pk=pk)
    if request.session.get('admin_id') == admin.id:
        messages.error(request, 'Você não pode desativar sua própria conta.')
        return redirect('admin_admins_list')
    admin.ativo = not admin.ativo
    admin.save()
    status = 'ativado' if admin.ativo else 'desativado'
    messages.success(request, f'Administrador {admin.nome} {status} com sucesso.')
    return redirect('admin_admins_list')


@login_required_admin
def admin_meu_perfil(request):
    admin = get_object_or_404(Administrador, pk=request.session['admin_id'])
    form = AdministradorForm(request.POST or None, instance=admin)
    if request.method == 'POST' and form.is_valid():
        admin = form.save()
        request.session['admin_nome'] = admin.nome
        messages.success(request, 'Seu perfil foi atualizado com sucesso.')
        return redirect('admin_meu_perfil')
    return render(request, 'admin/meu_perfil.html', {
        'form': form,
        'admin': admin,
    })


@login_required_admin
def admin_admin_create(request):
    form = AdministradorForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Administrador cadastrado com sucesso.')
        return redirect('admin_admins_list')
    return render(request, 'admin/admin_form.html', {
        'form': form,
        'titulo': 'Novo Administrador',
    })


@login_required_admin
def admin_admin_edit(request, pk):
    admin = get_object_or_404(Administrador, pk=pk)
    form = AdministradorForm(request.POST or None, instance=admin)
    if request.method == 'POST' and form.is_valid():
        admin = form.save()
        if request.session.get('admin_id') == admin.id:
            request.session['admin_nome'] = admin.nome
        messages.success(request, 'Administrador atualizado com sucesso.')
        return redirect('admin_admins_list')
    return render(request, 'admin/admin_form.html', {
        'form': form,
        'titulo': f'Editar: {admin.nome}',
        'objeto': admin,
    })


@login_required_admin
@require_http_methods(['GET', 'POST'])
def admin_admin_delete(request, pk):
    admin = get_object_or_404(Administrador, pk=pk)
    if Administrador.objects.count() <= 1:
        messages.error(request, 'Não é possível remover o único administrador.')
        return redirect('admin_admins_list')
    if request.method == 'POST':
        if request.session.get('admin_id') == admin.id:
            messages.error(request, 'Você não pode remover sua própria conta.')
            return redirect('admin_admins_list')
        admin.delete()
        messages.success(request, 'Administrador removido com sucesso.')
        return redirect('admin_admins_list')
    return render(request, 'admin/confirm_delete.html', {
        'objeto': admin,
        'tipo': 'administrador',
        'voltar_url': 'admin_admins_list',
    })
