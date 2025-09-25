from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Project, Task, Status, Priority
import json

# View 1: HttpResponse view - API-style task count
def task_stats(request):
    """
    HttpResponse view that returns task statistics as JSON
    Shows total tasks, completed tasks, and overdue tasks
    """
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(status=Status.DONE).count()
    overdue_tasks = Task.objects.filter(
        due_date__lt=timezone.localdate(),
        status__in=[Status.TODO, Status.DOING]
    ).count()

    stats = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'completion_rate': f"{(completed_tasks/total_tasks*100):.1f}%" if total_tasks > 0 else "0%"
    }

    return HttpResponse(json.dumps(stats), content_type='application/json')

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
