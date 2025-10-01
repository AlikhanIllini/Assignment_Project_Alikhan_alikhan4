from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Project, Task, Status, Priority
import json

# View 1: HttpResponse view - Manual HTML response
def task_stats(request):
    """
    HttpResponse view that returns HTML manually (not using render shortcut)
    Shows total tasks, completed tasks, and overdue tasks
    """
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(status=Status.DONE).count()
    overdue_tasks = Task.objects.filter(
        due_date__lt=timezone.localdate(),
        status__in=[Status.TODO, Status.DOING]
    ).count()

    completion_rate = f"{(completed_tasks/total_tasks*100):.1f}%" if total_tasks > 0 else "0%"

    # Manual HTML string construction (HttpResponse style)
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Task Statistics</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .stats-container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .stat-box {{ display: inline-block; margin: 15px; padding: 20px; border-radius: 5px; text-align: center; color: white; min-width: 120px; }}
            .total {{ background: #3498db; }}
            .completed {{ background: #27ae60; }}
            .overdue {{ background: #e74c3c; }}
            .rate {{ background: #9b59b6; }}
            h1 {{ color: #2c3e50; }}
            .nav {{ margin-bottom: 20px; }}
            .nav a {{ margin-right: 15px; padding: 8px 15px; background: #34495e; color: white; text-decoration: none; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="stats-container">
            <h1>📊 Task Statistics Dashboard</h1>
            <div class="nav">
                <a href="/">Home</a>
                <a href="/tasks/">Task Board</a>
                <a href="/tasks/stats/">Statistics</a>
            </div>
            
            <div class="stat-box total">
                <h2>{total_tasks}</h2>
                <p>Total Tasks</p>
            </div>
            
            <div class="stat-box completed">
                <h2>{completed_tasks}</h2>
                <p>Completed</p>
            </div>
            
            <div class="stat-box overdue">
                <h2>{overdue_tasks}</h2>
                <p>Overdue</p>
            </div>
            
            <div class="stat-box rate">
                <h2>{completion_rate}</h2>
                <p>Completion Rate</p>
            </div>
            
            <p style="margin-top: 30px; color: #7f8c8d;">
                <strong>Note:</strong> This page is generated using HttpResponse with manual HTML construction.
            </p>
        </div>
    </body>
    </html>
    """

    return HttpResponse(html)

# View 2: render() view - Main task board
def task_board(request):
    """
    Main task board view using render() with template
    Shows all tasks organized by status columns
    """
    # Get all projects and tasks
    projects = Project.objects.all()

    # Organize tasks by status
    todo_tasks = Task.objects.filter(status=Status.TODO)
    doing_tasks = Task.objects.filter(status=Status.DOING)
    done_tasks = Task.objects.filter(status=Status.DONE)

    # Calculate overdue tasks
    overdue_tasks = Task.objects.filter(
        due_date__lt=timezone.localdate(),
        status__in=[Status.TODO, Status.DOING]
    )

    context = {
        'projects': projects,
        'todo_tasks': todo_tasks,
        'doing_tasks': doing_tasks,
        'done_tasks': done_tasks,
        'overdue_tasks': overdue_tasks,
        'current_date': timezone.localdate(),
    }

    return render(request, 'tasks/board.html', context)

# View 3: Project detail view with tasks
def project_detail(request, project_id):
    """
    Detail view for a specific project showing all its tasks
    Uses get_object_or_404 for error handling
    """
    project = get_object_or_404(Project, id=project_id)
    tasks = project.tasks.all()

    # Task counts for this project
    task_counts = {
        'total': tasks.count(),
        'todo': tasks.filter(status=Status.TODO).count(),
        'doing': tasks.filter(status=Status.DOING).count(),
        'done': tasks.filter(status=Status.DONE).count(),
    }

    context = {
        'project': project,
        'tasks': tasks,
        'task_counts': task_counts,
    }

    return render(request, 'tasks/project_detail.html', context)

# View 4: Task list by priority
def tasks_by_priority(request, priority_level):
    """
    Filter tasks by priority level
    Shows how to handle URL parameters and filtering
    """
    try:
        priority = int(priority_level)
        if priority not in [Priority.LOW, Priority.MED, Priority.HIGH]:
            raise ValueError
    except (ValueError, TypeError):
        return HttpResponse("Invalid priority level", status=400)

    tasks = Task.objects.filter(priority=priority)
    priority_name = Priority(priority).label

    context = {
        'tasks': tasks,
        'priority_level': priority,
        'priority_name': priority_name,
        'total_count': tasks.count(),
    }

    return render(request, 'tasks/tasks_by_priority.html', context)

# ASSIGNMENT 5 - CLASS-BASED VIEWS

from django.views import View
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages

# Class-Based View 1: Base View (inheriting from View)
class TaskStatsView(View):
    """
    Base class-based view that manually handles GET requests
    Shows task statistics using class-based approach
    """
    def get(self, request):
        total_tasks = Task.objects.count()
        completed_tasks = Task.objects.filter(status=Status.DONE).count()
        overdue_tasks = Task.objects.filter(
            due_date__lt=timezone.localdate(),
            status__in=[Status.TODO, Status.DOING]
        ).count()

        context = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks,
            'completion_rate': f"{(completed_tasks/total_tasks*100):.1f}%" if total_tasks > 0 else "0%"
        }

        return render(request, 'tasks/stats.html', context)

# Class-Based View 2: Generic ListView
class TaskListView(ListView):
    """
    Generic ListView showing all tasks with filtering and pagination
    """
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 10
    ordering = ['status', '-priority', 'due_date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.all()
        context['total_count'] = Task.objects.count()
        context['status_counts'] = {
            'todo': Task.objects.filter(status=Status.TODO).count(),
            'doing': Task.objects.filter(status=Status.DOING).count(),
            'done': Task.objects.filter(status=Status.DONE).count(),
        }
        return context

# Class-Based View 3: Generic DetailView
class ProjectDetailView(DetailView):
    """
    Generic DetailView for individual project with all its tasks
    """
    model = Project
    template_name = 'tasks/project_detail_cbv.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        tasks = project.tasks.all()

        context['tasks'] = tasks
        context['task_counts'] = {
            'total': tasks.count(),
            'todo': tasks.filter(status=Status.TODO).count(),
            'doing': tasks.filter(status=Status.DOING).count(),
            'done': tasks.filter(status=Status.DONE).count(),
        }
        context['overdue_tasks'] = tasks.filter(
            due_date__lt=timezone.localdate(),
            status__in=[Status.TODO, Status.DOING]
        )
        return context

# Class-Based View 4: Extra View - CreateView for Tasks
class TaskCreateView(CreateView):
    """
    Generic CreateView for creating new tasks
    """
    model = Task
    template_name = 'tasks/task_create.html'
    fields = ['title', 'description', 'project', 'priority', 'status', 'due_date']
    success_url = reverse_lazy('task_list_cbv')

    def form_valid(self, form):
        messages.success(self.request, f'Task "{form.instance.title}" created successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.all()
        return context
