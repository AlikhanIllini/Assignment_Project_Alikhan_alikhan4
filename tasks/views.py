from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count, Q, Case, When, Value, CharField
from tasks.models import Project, Task, Status, Priority

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

# ASSIGNMENT 6 - BASE and GENERIC CLASS-BASED VIEWS

from django.views import View
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages

# BASE CBV - Inheriting from View (Manual Implementation)
class TaskStatsView(View):
    """
    Base class-based view inheriting from View
    Manually handles GET requests and explicitly queries the model
    """
    def get(self, request):
        # Explicit model queries
        total_tasks = Task.objects.count()
        completed_tasks = Task.objects.filter(status=Status.DONE).count()
        overdue_tasks = Task.objects.filter(
            due_date__lt=timezone.localdate(),
            status__in=[Status.TODO, Status.DOING]
        ).count()

        # Manual context preparation
        context = {
            'stats_data': {  # Custom context variable name
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'overdue_tasks': overdue_tasks,
                'completion_rate': f"{(completed_tasks/total_tasks*100):.1f}%" if total_tasks > 0 else "0%"
            }
        }

        # Explicitly return rendered template
        return render(request, 'tasks/task_stats.html', context)

# GENERIC CBV - ListView (Automatic Implementation)
class TaskListView(ListView):
    """
    Generic ListView using Django's built-in functionality
    Automatically handles queryset, pagination, and context
    """
    model = Task
    template_name = 'tasks/task_list.html'  # Custom template name
    context_object_name = 'tasks'  # Override default 'object_list'
    paginate_by = 10
    ordering = ['status', '-priority', 'due_date']

    def get_queryset(self):
        """Filter tasks based on search query"""
        queryset = Task.objects.select_related('project')  # Optimize queries

        # Get search query from GET parameters
        search_query = self.request.GET.get('q', '')

        if search_query:
            # Filter using Q objects for OR logic across multiple fields
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(project__name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Search query for form persistence
        context['search_query'] = self.request.GET.get('q', '')

        # OVERALL AGGREGATIONS
        context['total_stats'] = {
            'total_tasks': Task.objects.count(),
            'completed_tasks': Task.objects.filter(status=Status.DONE).count(),
            'overdue_count': Task.objects.filter(
                due_date__lt=timezone.localdate(),
                status__in=[Status.TODO, Status.DOING]
            ).count(),
        }

        # GROUPED AGGREGATIONS
        # 1. Tasks by Status (grouped count)
        context['status_breakdown'] = Task.objects.values('status').annotate(
            count=Count('id'),
            status_name=Case(
                When(status=Status.TODO, then=Value('To Do')),
                When(status=Status.DOING, then=Value('In Progress')),
                When(status=Status.DONE, then=Value('Done')),
                default=Value('Unknown'),
                output_field=CharField()
            )
        ).order_by('status')

        # 2. Tasks by Priority (grouped count)
        context['priority_breakdown'] = Task.objects.values('priority').annotate(
            count=Count('id'),
            priority_name=Case(
                When(priority=Priority.LOW, then=Value('Low')),
                When(priority=Priority.MED, then=Value('Medium')),
                When(priority=Priority.HIGH, then=Value('High')),
                default=Value('Unknown'),
                output_field=CharField()
            )
        ).order_by('-priority')

        # 3. Tasks by Project (grouped count)
        context['project_breakdown'] = Project.objects.annotate(
            task_count=Count('tasks'),
            completed_count=Count('tasks', filter=Q(tasks__status=Status.DONE)),
        ).order_by('-task_count')

        return context

# GENERIC CBV - DetailView (Automatic Implementation)
class ProjectDetailView(DetailView):
    """
    Generic DetailView using automatic object retrieval
    Uses default template naming convention
    """
    model = Project
    template_name = 'tasks/project_detail.html'
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
        return context

# GENERIC CBV - CreateView (Form Handling)
class TaskCreateView(CreateView):
    """
    Generic CreateView for creating new tasks
    Automatic form generation and validation
    """
    model = Task
    template_name = 'tasks/task_form.html'
    fields = ['title', 'description', 'project', 'priority', 'status', 'due_date']
    success_url = reverse_lazy('task_list_cbv')

    def form_valid(self, form):
        messages.success(self.request, f'Task "{form.instance.title}" created successfully!')
        return super().form_valid(form)

# ASSIGNMENT 8 - STATIC FILES AND DATA VISUALIZATION

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
import json
import plotly
import plotly.graph_objs as go
from plotly.utils import PlotlyJSONEncoder
from django.http import JsonResponse

# Chart Dashboard View
class ChartsDashboardView(View):
    """
    Dashboard view showing both Matplotlib and Plotly charts
    Demonstrates static files integration and data visualization
    """
    def get(self, request):
        # Get aggregated data for charts
        chart_data = self.get_chart_data()

        # Generate Matplotlib chart (PNG)
        matplotlib_chart = self.generate_matplotlib_chart(chart_data)

        # Generate Plotly chart (JSON)
        plotly_chart = self.generate_plotly_chart(chart_data)

        context = {
            'matplotlib_chart': matplotlib_chart,
            'plotly_chart': plotly_chart,
            'chart_data': chart_data,
        }

        return render(request, 'tasks/charts_dashboard.html', context)

    def get_chart_data(self):
        """Get aggregated data for charts"""
        # Tasks by Status
        status_data = Task.objects.values('status').annotate(
            count=Count('id'),
            status_name=Case(
                When(status=Status.TODO, then=Value('To Do')),
                When(status=Status.DOING, then=Value('In Progress')),
                When(status=Status.DONE, then=Value('Done')),
                default=Value('Unknown'),
                output_field=CharField()
            )
        ).order_by('status')

        # Tasks by Priority
        priority_data = Task.objects.values('priority').annotate(
            count=Count('id'),
            priority_name=Case(
                When(priority=Priority.LOW, then=Value('Low')),
                When(priority=Priority.MED, then=Value('Medium')),
                When(priority=Priority.HIGH, then=Value('High')),
                default=Value('Unknown'),
                output_field=CharField()
            )
        ).order_by('-priority')

        # Tasks by Project
        project_data = Project.objects.annotate(
            task_count=Count('tasks')
        ).order_by('-task_count')[:5]  # Top 5 projects

        return {
            'status_data': status_data,
            'priority_data': priority_data,
            'project_data': project_data,
        }

    def generate_matplotlib_chart(self, chart_data):
        """Generate Matplotlib PNG chart as base64 string"""
        # Set Illinois colors
        illinois_colors = ['#13294B', '#FF5F05', '#E8F4FD']
        plt.style.use('default')

        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.patch.set_facecolor('white')

        # Chart 1: Tasks by Status (Pie Chart)
        status_labels = [item['status_name'] for item in chart_data['status_data']]
        status_counts = [item['count'] for item in chart_data['status_data']]

        ax1.pie(status_counts, labels=status_labels, colors=illinois_colors,
                autopct='%1.1f%%', startangle=90)
        ax1.set_title('Tasks by Status', fontsize=14, fontweight='bold', color='#13294B')

        # Chart 2: Tasks by Priority (Bar Chart)
        priority_labels = [item['priority_name'] for item in chart_data['priority_data']]
        priority_counts = [item['count'] for item in chart_data['priority_data']]

        bars = ax2.bar(priority_labels, priority_counts, color=['#DC3545', '#FF5F05', '#28A745'])
        ax2.set_title('Tasks by Priority', fontsize=14, fontweight='bold', color='#13294B')
        ax2.set_ylabel('Number of Tasks')

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')

        plt.tight_layout()

        # Convert to base64 string
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()

        graphic = base64.b64encode(image_png)
        graphic = graphic.decode('utf-8')

        return graphic

    def generate_plotly_chart(self, chart_data):
        """Generate Plotly interactive chart as JSON"""
        # Prepare data for Plotly
        project_names = [project.name for project in chart_data['project_data']]
        project_counts = [project.task_count for project in chart_data['project_data']]

        # Create interactive bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=project_names,
                y=project_counts,
                marker_color=['#13294B', '#FF5F05', '#E8F4FD', '#6C757D', '#28A745'],
                text=project_counts,
                textposition='auto',
            )
        ])

        fig.update_layout(
            title={
                'text': 'Tasks per Project (Interactive)',
                'x': 0.5,
                'font': {'size': 16, 'color': '#13294B'}
            },
            xaxis_title='Projects',
            yaxis_title='Number of Tasks',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'color': '#13294B'},
            height=400,
        )

        # Convert to JSON
        graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)
        return graphJSON

# Matplotlib PNG View (Alternative approach)
def matplotlib_chart_png(request):
    """
    Returns a Matplotlib chart as PNG image
    Demonstrates Django's HttpResponse with image content
    """
    # Get chart data
    status_data = Task.objects.values('status').annotate(count=Count('id'))

    # Create chart
    plt.figure(figsize=(8, 6))
    labels = ['To Do', 'In Progress', 'Done']
    sizes = [item['count'] for item in status_data]
    colors = ['#13294B', '#FF5F05', '#E8F4FD']

    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.title('Task Status Distribution', fontsize=16, fontweight='bold', color='#13294B')

    # Return as HTTP response
    response = HttpResponse(content_type='image/png')
    plt.savefig(response, format='png', dpi=150, bbox_inches='tight')
    plt.close()

    return response

