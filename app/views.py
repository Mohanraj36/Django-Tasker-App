from django.contrib.auth.decorators import login_required
from datetime import datetime
from datetime import timedelta
import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.db.models import Q, Count
from .models import Employee, Task, Ticket, User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
# Create your views here.


def index(request):
    return render(request, 'index.html')


def user_login(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome {username}')
                return redirect('dashboard')
            else:
                messages.error(request, 'User Not Found')
                return redirect('login')

        return render(request, 'login.html')
    else:
        messages.success(request, 'Already LoggedIn')
        return redirect('index')


@login_required(login_url='login')
def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You Have Been Logged Out')
        return redirect('index')


def user_register(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data['username']
                password = form.cleaned_data['password1']
                user = authenticate(
                    request, username=username, password=password)
                login(request, user)
                messages.success(request, 'Registration Success')
                return redirect('index')
        else:
            form = SignUpForm()
            return render(request, 'register.html', {'form': form})
        return render(request, 'register.html', {'form': form})
    else:
        messages.success(request, 'Already LoggedIn')
        return redirect('index')


def task_collect(completed_tasks):

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=5)

    completion_counts = {}
    for task in completed_tasks:
        completion_counts[task['task_completed_at__date']
                          ] = task['completed_count']

    current_date = start_date
    while current_date <= end_date:
        if current_date not in completion_counts:
            completion_counts[current_date] = 0
        current_date += timedelta(days=1)
    return completion_counts


def ticket_collect(completed_tickets):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=5)

    completion_counts = {}
    for ticket in completed_tickets:
        completion_counts[ticket['ticket_completed_at__date']
                          ] = ticket['completed_count']

    # Fill in missing dates with zero completion counts
    current_date = start_date
    while current_date <= end_date:
        if current_date not in completion_counts:
            completion_counts[current_date] = 0
        current_date += timedelta(days=1)

    return completion_counts



def employee_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        try:
            employee = Employee.objects.get(Employee=user)
        except Employee.DoesNotExist:
            messages.warning(request,'Not Yet Authorized To Employee')
            return redirect('index')  # Redirect to a not authorized page
        return view_func(request, *args, **kwargs)
    return _wrapped_view



@login_required(login_url="login")
@employee_required
def dashboard(request):

    user_obj = User.objects.get(id=request.user.id)
    emp_obj = Employee.objects.get(Employee=user_obj)
    print(emp_obj)
    task_obj = Task.objects.filter(Q(task_assigned_to=emp_obj) | Q(task_assigned_by=emp_obj)).distinct().order_by('task_created_at').reverse()
    tickets_obj = Ticket.objects.filter(Q(ticket_assigned_to=emp_obj) | Q(ticket_assigned_by=emp_obj)).distinct().order_by('ticket_created_at').reverse()

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=5)

    completed_tickets = Ticket.objects.filter(ticket_status='Completed', ticket_completed_at__date__range=[start_date, end_date], ticket_assigned_to=emp_obj).values('ticket_completed_at__date').annotate(completed_count=Count('ticket_id'))
    completed_tasks = Task.objects.filter(task_status='Completed', task_completed_at__date__range=[start_date, end_date], task_assigned_to=emp_obj).values('task_completed_at__date').annotate(completed_count=Count('task_id'))

    completion_counts = task_collect(completed_tasks)

    sorted_date = dict(sorted(list(completion_counts.items())))
    task_total_data = [v for v in sorted_date.values()]

    # -----------------------------------------------------------------------------------------------------

    completion_counts = ticket_collect(completed_tickets)

    sorted_date = dict(sorted(list(completion_counts.items())))
    total_data = [v for v in sorted_date.values()]
    total_data_labels = [datetime.strftime(
        k, '%d/%m') for k in sorted_date.keys()]
    chart_data = {
        'ticket_labels': ["Total Ticket", 'Open', 'In Progress', 'Completed'],
        'ticket_total': [tickets_obj.count(), tickets_obj.filter(ticket_status='Open').count(), tickets_obj.filter(ticket_status='In Progress').count(), tickets_obj.filter(ticket_status='Completed').count()],
        'task_labels': ["Total Task", 'Open',  'In Progress', 'Completed'],
        'task_total': [task_obj.count(), task_obj.filter(task_status='Open').count(), task_obj.filter(task_status='In Progress').count(), task_obj.filter(task_status='Completed').count()],
        'total_data_labels': total_data_labels,
        'total_data': total_data,
        'task_total_data': task_total_data,
    }

    alert_badge = sum(
        1 for ticket in tickets_obj if ticket.ticket_raised_by_client and ticket.ticket_status != 'Completed')

    current_t = datetime.now()

    chart_data = json.dumps(chart_data)

    return render(request, 'dashboard.html', {'ticks': tickets_obj, "tasks": task_obj, 'chart_data': chart_data, 'alert_badge': alert_badge, 'current_t': current_t})


def ticket_form(request):
    if request.method == 'POST':

        ticket_id = request.POST.get('ticket_id')
        ticket_status = request.POST.get('ticket_status')

        try:
            if Ticket.objects.filter(pk=ticket_id).update(ticket_status=ticket_status):
                return redirect('dashboard')

        except Ticket.DoesNotExist:
            return redirect('dashboard')


def task_form(request):
    if request.method == 'POST':

        task_id = request.POST.get('task_id')
        task_status = request.POST.get('task_status')

        try:
            if Task.objects.filter(pk=task_id).update(task_status=task_status):
                return redirect('dashboard')

        except Task.DoesNotExist:
            return redirect('dashboard')


def search(request):

    search_ = request.GET.get('q')
    search_t = request.GET.get('t')

    results = ''

    if search_ != "":
        if search_t == "Task":

            results = Task.objects.filter(task_name__icontains=search_)

            return render(request, 'result.html', {'results': results, 'Task': 'Task'})

        else:

            results = Ticket.objects.filter(ticket_name__icontains=search_)

            return render(request, 'result.html', {'results': results, 'Ticket': 'Ticket'})

    else:
        return JsonResponse({}, status=204)
