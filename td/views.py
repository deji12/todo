from django.shortcuts import render, redirect
from .models import Task, AllUsers
from django.http import HttpResponse, response
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage, send_mail, BadHeaderError
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes

# Create your views here.
@login_required()
def HomePage(request):
    if request.method == 'POST':
        incoming_task = request.POST['add_task']

        new_task = Task(my_user=request.user, task=incoming_task, completed=False)
        new_task.save()

    task = Task.objects.filter(my_user=request.user).order_by('-id')

    finished = Task.objects.filter(completed=True, my_user=request.user)
    unfinished = Task.objects.filter(completed=False, my_user=request.user)
    
    sum_finished = 0
    for i in finished:
        sum_finished += 1

    sum_unfinished = 0
    for j in unfinished:
        sum_unfinished += 1

    context = {
        'tasks': task,
        'finished': sum_finished,
        'unfinished': sum_unfinished
    }
    
    return render(request, 'td/index.html', context)

@login_required()
def UpdateTask(request, id):
    if request.method == 'POST':
        new_task_name = request.POST['update_task']
        com = request.POST.get('completed', False)

        if new_task_name:
            get_task = Task.objects.get(id=id)
            get_task.task = new_task_name
            get_task.save()

        if com:
            get_task = Task.objects.get(id=id)
            get_task.completed = True
            get_task.save()

        if not com:
            get_task = Task.objects.get(id=id)
            get_task.completed = False
            get_task.save()

        if not new_task_name:
            return redirect('home')


        return redirect('home')

    get_task_ini = Task.objects.get(id=id)

    completed_or_not = get_task_ini.completed

    context = {
        'completed': completed_or_not
    }    

    return render(request, 'td/update.html', context)

@login_required()
def DeleteTask(request, id):
    del_task = Task.objects.get(id=id)
    if request.method == 'POST':
        del_task.delete()
        return redirect('home')

    return render(request, 'td/delete.html', {})
    

def Login(request):
    if request.method == 'POST':
        username = request.POST['uname']
        password = request.POST['pass']

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, f'Error, wrong user details or user does not exist')
            return render(request, 'td/login.html', {})

    return render(request, 'td/login.html', {})

def Logout(request):
    logout(request)
    return redirect('login')

def Register(request):
    if request.method =='POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        username = request.POST['uname']
        email = request.POST['email']
        password = request.POST['pass']
        confirm_pass = request.POST['pass2']


        if len(password) < 5:
            messages.error(request, 'Password must be equal to or greater than 5 characters')
            return render(request, 'td/reg.html', {})
        
        if password != confirm_pass:
            messages.error(request, 'Passwords do not match, Try again')
            return render(request, 'td/reg.html', {})
        
        try:
            all_users = User.objects.filter(username=username)
            
            if all_users.exists():
                return HttpResponse(f'A user with username "{username}" already exixts. Pick another name!')

            else:
                if '-superuser' in username:
                    splitted = username.split("-")
                    s_uname = splitted[0]
                    new_super_user = User.objects.create_superuser(username=s_uname, email=email, password=password)
                    new_super_user.save()
                    return redirect('login')
                else:
                    new_user = User.objects.create_user(username=username, email=email, password=password)
                    new_user.first_name = fname
                    new_user.last_name = lname
                    new_user.save()
                    return redirect('login')


                # save_new_user = AllUsers(first_name=fname, last_name=lname, username=username, email=email)
                # save_new_user.save()
                

        except:
            return HttpResponse('Error, Something Went wrong')

    return render(request, 'td/reg.html', {})

@login_required
def UpdateProfile(request, id):
    my_user = User.objects.get(id=id)
    if request.method == 'POST':
        new_fname = request.POST['update_fname']
        new_lname = request.POST['update_lname']
        new_email = request.POST['update_email']
        new_uname = request.POST['update_uname']
        new_pass = request.POST['new_pass']
        confirm_pass = request.POST['new_pass2']

        if new_fname:
            my_user.first_name = new_fname
            my_user.save()

        if new_lname:
            myuser.last_name = new_lname
            my_user.save()

        if new_email:
            my_user.email = new_email
            my_user.save()
        
        if new_uname:
            my_user.username = new_uname
            my_user.save()
        
        if new_pass:
            if len(new_pass) < 5:
                messages.error(request, 'Password too short!')
                return render(request, 'td/update_profile.html', {})
            
            if new_pass == confirm_pass:
                my_user.set_password(new_pass)
                my_user.save()
                logout(request)
                messages.success(request, 'Profile updated successfully! Login Again')
                return redirect('home')
                
            else:
                messages.error(request, 'Passwords do not match! Try again')
                return render(request, 'td/update_profile.html', {})

        
        return render(request, 'td/index.html', {})


    return render(request, 'td/update_profile.html', {})

@login_required()
def DashBoard(request):
    if request.method == 'POST':
        data = request.POST['search']

        append_for_users = []
        user = get_user_model().objects.values()
        for get_user in user:
            h = get_user.get('username')
            append_for_users.append(h)
        if data in append_for_users:
            get_pat_user = get_user_model().objects.get(username=data)
            email = get_pat_user.email
            date_joined = get_pat_user.date_joined

            j = 0
            users = get_user_model().objects.values()
            for i in users:
                j+=1
        
            a = 0
            for b in Task.objects.all().values('task'):
                a+=1
            
            c = 0
            for d in Task.objects.filter(completed=True):
                c+=1        

            d = 0
            for e in Task.objects.filter(completed=False):
                d+=1

            context = {
                'get_user_name': get_pat_user,
                'email': email,
                'joined': date_joined,
                'num_users': j,
                'task_num': a,
                'completed': c,
                'un_complete': d,
            }
            return render(request, 'td/search_result.html', context)

        else:
            messages.error(request, 'User does not exist!')
            return render(request, 'td/search_result.html')


    users = get_user_model().objects.values()
    
    j = 0
    for i in users:
        j+=1
  
    a = 0
    for b in Task.objects.all().values('task'):
        a+=1
    
    c = 0
    for d in Task.objects.filter(completed=True):
        c+=1        

    d = 0
    for e in Task.objects.filter(completed=False):
        d+=1

    #get usernames
    names = []
    emails = []
    created = []
    user_name = get_user_model().objects.values()

    for all_users in user_name:
        final_dict = all_users.get('username')
        names.append(final_dict)
        
    
    for all_emails in user_name:
        final = all_emails.get('email')
        emails.append(final)

    for creation_dates in user_name:
        final_dates = creation_dates.get('date_joined')
        created.append(final_dates)
        

    context = {
        'users':users,
        'num_users': j,
        'task_num': a,
        'completed': c,
        'un_complete': d,
        'names': names,
        'email': emails,
        'created': created,
    }
    if request.user.is_superuser:
        return render(request, 'td/d2.html',context)

    

    else:
        return render(request, 'td/index.html',context)

@login_required()
def DeleteUser(request):
    if request.method == 'POST':
        get_username = request.POST['del']
        try:
            user = User.objects.get(username=get_username)
            user.delete()
            return redirect('dash')
        except User.DoesNotExist:
            messages.error(request, 'Error, user does not exist')
            return render(request, 'td/delete_user.html')

    j = 0
    users = get_user_model().objects.values()
    for i in users:
            j+=1
        
    a = 0
    for b in Task.objects.all().values('task'):
        a+=1
            
    c = 0
    for d in Task.objects.filter(completed=True):
        c+=1        

    d = 0
    for e in Task.objects.filter(completed=False):
        d+=1

    context = {
        'num_users': j,
        'task_num': a,
        'completed': c,
        'un_complete': d,
    }

    return render(request, 'td/delete_user.html', context)


def Notify(request):
    if request.method == 'POST':

        emails = []
        
        user_name = get_user_model().objects.values()
        
        for all_emails in user_name:
            final = all_emails.get('email')
            emails.append(final)
        # print(emails)

        for i in emails:
            use = User.objects.get(email=i)
            get_finished_task = Task.objects.filter(my_user=use, completed=True)
            get_unfinished_task = Task.objects.filter(my_user=use, completed=False)

            tot = 0
            for j in get_unfinished_task:
                tot += 1

            if tot == 0:
                pass
            else:
            
                template = render_to_string('td/email_template.html', {'name': use, 'total': tot, 'tasks': get_unfinished_task})
                # Send email
                email = EmailMessage(
                    'Uncompleted Task Reminder',
                    template,
                    settings.EMAIL_HOST_USER,
                    [i]
                )

                email.fail_silently = True
                email.send()
              

    return render(request, 'td/send_email.html', {})


def password_reset_request(request):
    if request.method == 'POST':
        pass_reset_form = PasswordResetForm(request.POST)
        if pass_reset_form.is_valid():
            data = pass_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
               for user in associated_users:
                   subject = 'Password Reset Requested'
                   email_templat_name = 'td/password_reset_email.txt'
                   c = {"email": user.email,"domain": "todoappdj.herokuapp.com","site_name": "Todoappdj","uid": urlsafe_base64_encode(force_bytes(user.pk)),"user": user,"token": default_token_generator.make_token(user),"protocol": 'http'}
                   email = render_to_string(email_templat_name, c)     
                   try:
                        send_mail(
                           subject,
                           email,
                           settings.EMAIL_HOST_USER,
                           [user.email],
                           fail_silently=False
                       )
                   except BadHeaderError:
                        return HttpResponse('Invalid header found')
                   return redirect("password_reset_done")

            else:
                messages.error(request, 'Wrong email or user does not exist')      
                password_reset_form = PasswordResetForm()
                return render(request, 'td/password_reset.html', {'password_reset_form': password_reset_form}) 
                
    password_reset_form = PasswordResetForm()
    return render(request, 'td/password_reset.html', {'password_reset_form': password_reset_form})
