from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http.response import Http404, JsonResponse
from django.shortcuts import render, redirect
from datetime import datetime as dt
from django.contrib import messages
from app.models import Evento


def login_user(request):
    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    return redirect('/')


def submit_login(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        usuario = authenticate(username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            return redirect('/')
        else:
            messages.error(request, 'Usuário ou senha inválido!')
    
    return redirect('/')


@login_required(login_url='/login/')
def lista_eventos(request):  
    usuario = request.user
    data_atual = dt.now()
    eventos = Evento.objects.filter(
        usuario=usuario, data_evento__gt=data_atual)
    
    dados = {'eventos': eventos}
    return render(request, 'agenda.html', dados)


@login_required(login_url='/login/')
def evento(request):
    id_evento = request.GET.get('id')
    
    dados = {}
    if id_evento:
        dados['evento'] = Evento.objects.get(id=id_evento)
    
    return render(request, 'evento.html', dados)


@login_required(login_url='/login/')
def submit_evento(request):
    if request.POST:
        titulo = request.POST.get('titulo')
        data_evento = request.POST.get('data_evento')
        descricao = request.POST.get('descricao')
        usuario = request.user

        id_evento = request.POST.get('id_evento')
        if id_evento:
            evento = Evento.objects.get(id=id_evento)

            if evento.usuario == usuario:
                evento.titulo = titulo
                evento.data_evento = data_evento
                evento.descricao = descricao
                evento.save()
                
            # Evento.objects.filter(id=id_evento).update(
            #     titulo=titulo, data_evento=data_evento, descricao=descricao)
        else:
            Evento.objects.create(
                titulo=titulo, data_evento=data_evento, descricao=descricao, usuario=usuario)
    return redirect('/')


@login_required(login_url='/login/')
def delete_evento(request, id_evento):
    usuario = request.user
    try:
        evento = Evento.objects.get(id=id_evento)
    except Exception:
        raise Http404()
        
    if usuario == evento.usuario:
        evento.delete()
    else:
        raise Http404()
    
    return redirect('/')


# @login_required(login_url='/login/')
def json_lista_evento(request, id_usuario):
    usuario = Evento.objects.get(id=id_usuario).values('')
    evento = Evento.objects.filter(usuario=usuario).values('id', 'titulo')
    return JsonResponse(list(evento), safe=False)
