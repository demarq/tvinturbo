from django.shortcuts import render, get_object_or_404, reverse
from django.contrib.auth import login as dologin
from django.contrib.auth import logout as dologout
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from .models import Message, MessageConfig, DatabaseConfig, MyUser
from .forms import *


@require_GET
@login_required
def index(request):
    messages_list = Message.objects.all().order_by('-id')
    if 'pattern' in request.GET:
        pattern = request.GET.get('pattern')
        messages_list = Message.objects.filter(message__contains=pattern) or\
            Message.objects.filter(user__username__contains=pattern) or\
            Message.objects.filter(number__contains=pattern)
    paginator = Paginator(messages_list, 20)
    page = request.GET.get('page', 1)
    info = paginator.get_page(page)
    return render(request, 'sms_interface/sended.html', {'messages': info,
                                                        })


@permission_required('sms_interface.is_staff', login_url='/login')
def users(request):
    users_list = MyUser.objects.all()
    context = {'info': users_list}
    change_perms_request = request.GET.get('admin_set')
    if change_perms_request:
        user = User.objects.get(id=request.GET.get('id'))

        if change_perms_request == 'True':
            user.is_superuser = True
        elif change_perms_request == 'False':
            user.is_superuser = False
        user.save()
        HttpResponseRedirect(reverse('users'))
    return render(request, 'sms_interface/users.html', context)


@permission_required('sms_interface.is_staff', login_url='/login')
def message_settings(request):
    if request.method == 'GET':
        databases = DatabaseConfig.objects.filter(is_deleted=False)
        settings = MessageConfig.objects.filter(is_deleted=False)
        form = MessageConfigForm()
        error = request.GET.get('error')
        context = {'settings': settings,
                   'form': form,
                   'errors': error,
                   'databases': databases}
        delete_id = request.GET.get('delete')
        if delete_id:
            message = MessageConfig.objects.get(id=delete_id)
            confirm = request.GET.get('del_confirm')
            if confirm:
                message.is_deleted = True
                message.save()
            else:
                context.update({'confirm': True,
                                'database_to_delete': message})
    if request.method == 'POST':
        form = MessageConfigForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('message_settings'))
        else:
            print('NOT_VALID')
            print(form.errors)
            return HttpResponseRedirect('%s?error=True' % reverse('message_settings'))
    return render(request, 'sms_interface/message_settings.html', context)


@permission_required('sms_interface.is_staff', login_url='/login')
def settings(request):
    if request.method == 'GET':
        databases = DatabaseConfig.objects.filter(is_deleted=False)
        messages = MessageConfig.objects.all()
        form = SettingsForm()
        errors = request.GET.get('error')
        context = {'info': databases,
                   'messages': messages,
                   'form': form,
                   'errors': errors}
        delete_id = request.GET.get('delete')
        if delete_id:
            database = DatabaseConfig.objects.get(id=delete_id)
            confirm = request.GET.get('del_confirm')
            if confirm:
                database.is_deleted = True
                database.save()
            else:
                context.update({'confirm': True,
                                'database_to_delete': database})
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        print(request.POST)
        if form.is_valid():
            form = form.save()
            return HttpResponseRedirect(reverse('settings'))
        else:
            return HttpResponseRedirect('%s?error=True' % reverse('settings'))
    return render(request, 'sms_interface/settings.html', context)
    # return render(request, 'sms_interface/settings.html', context)


@login_required
def dosend(request):
    reverse_url = reverse('dosend')
    if request.method == 'GET':
        form = DoSendForm()
        context = {'form': form,
                   }
    if request.method == 'POST':
        form = DoSendForm(request.POST)
        if form.is_valid():
            try:
                message_sender = form.confirm()
                mess = message_sender.get_message()
                nodes = message_sender._nodes
                length = message_sender.get_length()
                context = {'notice_list':
                               [{'title': "Подтвердите",
                                 'content': ['Будет отправленно: %s сообщений' % length,
                                             'Содержание сообщения будет выглядеть так: %s' % mess],
                                 }],
                           'form': form,
                           'confirm': True,
                           }
                if request.POST.get('confirm') == 'True':
                    message_sender.send()
                    for node in nodes:
                        message = Message(message=node.message, number=node.number)
                        message.save()
                        message.user.add(request.user)
                        message.save()
                    return HttpResponseRedirect(reverse('index'))
            except BaseException as e:
                context.update({'error': e})
            return render(request, 'sms_interface/dosend.html', context)
    return render(request, 'sms_interface/dosend.html', context)


def signup(request):
    if request.method == 'POST':
        print(request.POST)
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            dologin(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'sms_interface/signup.html', {'signup_form': form,
                                                                 'action_url': reverse('signup'),
                                                                 })

    else:
        form = SignUpForm()
        return render(request, 'sms_interface/signup.html', {'signup_form': form,
                                                             'action_url': reverse('signup'),
                                                             })


@require_GET
def logout(request):
    dologout(request)
    return HttpResponseRedirect('/')


@login_required
def user_page(request, id):
    print(id)
    return HttpResponseRedirect('')


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        next_ref = request.POST.get('next', '/')
        if form.is_valid():
            user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
            if user:
                dologin(request, user=user)
                return HttpResponseRedirect(next_ref)
            else:
                form.bad_login()
                return render(request, 'sms_interface/login.html', {'form': form})
        else:
            return render(request, 'sms_interface/login.html', {'form': form})
    else:
        next_ref = request.GET.get('next_ref', '/')
        form = LoginForm()
        return render(request, 'sms_interface/login.html', {'form': form,
                                                            'next_ref': next_ref
                                                            })
