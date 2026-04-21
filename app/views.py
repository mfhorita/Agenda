from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http.response import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
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
    data_atual = timezone.now()
    eventos = Evento.objects.filter(
        usuario=usuario, data_evento__gt=data_atual)
    
    dados = {'eventos': eventos}
    return render(request, 'agenda.html', dados)


@login_required(login_url='/login/')
def evento(request):
    id_evento = request.GET.get('id')

    dados = {}
    if id_evento:
        dados['evento'] = get_object_or_404(Evento, id=id_evento, usuario=request.user)

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
            evento = get_object_or_404(Evento, id=id_evento, usuario=usuario)
            evento.titulo = titulo
            evento.data_evento = data_evento
            evento.descricao = descricao
            evento.save()
        else:
            Evento.objects.create(
                titulo=titulo, data_evento=data_evento, descricao=descricao, usuario=usuario)
    return redirect('/')


@login_required(login_url='/login/')
def delete_evento(request, id_evento):
    evento = get_object_or_404(Evento, id=id_evento, usuario=request.user)
    evento.delete()
    return redirect('/')


@login_required(login_url='/login/')
def json_lista_evento(request):
    eventos = Evento.objects.filter(usuario=request.user).values('id', 'titulo')
    return JsonResponse(list(eventos), safe=False)
