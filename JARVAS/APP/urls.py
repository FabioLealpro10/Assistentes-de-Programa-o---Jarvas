from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('logout/', views.logout_cliente, name='logout'),
    path('chat/', views.chat, name='chat'),

    path('painel/login/', views.admin_login, name='admin_login'),
    path('painel/logout/', views.admin_logout, name='admin_logout'),
    path('painel/', views.admin_dashboard, name='admin_dashboard'),

    path('painel/clientes/', views.admin_clientes_list, name='admin_clientes_list'),
    path('painel/clientes/novo/', views.admin_cliente_create, name='admin_cliente_create'),
    path('painel/clientes/<int:pk>/editar/', views.admin_cliente_edit, name='admin_cliente_edit'),
    path('painel/clientes/<int:pk>/excluir/', views.admin_cliente_delete, name='admin_cliente_delete'),

    path('painel/clientes/<int:pk>/toggle/', views.admin_cliente_toggle, name='admin_cliente_toggle'),

    path('painel/administradores/', views.admin_admins_list, name='admin_admins_list'),
    path('painel/administradores/novo/', views.admin_admin_create, name='admin_admin_create'),
    path('painel/administradores/<int:pk>/editar/', views.admin_admin_edit, name='admin_admin_edit'),
    path('painel/administradores/<int:pk>/excluir/', views.admin_admin_delete, name='admin_admin_delete'),
    path('painel/administradores/<int:pk>/toggle/', views.admin_admin_toggle, name='admin_admin_toggle'),
    path('painel/meu-perfil/', views.admin_meu_perfil, name='admin_meu_perfil'),
]
