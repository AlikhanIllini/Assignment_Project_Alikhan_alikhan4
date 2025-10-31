from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Count, Q, Case, When, Value, CharField
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django import forms
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
import json
import plotly
import plotly.graph_objs as go
from plotly.utils import PlotlyJSONEncoder
import urllib.request
import urllib.error

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

# ASSIGNMENT 8 - FORMS & POST (FBV)

# Form definition for Task creation
class TaskForm(forms.ModelForm):
    """
    ModelForm for creating/editing tasks
    Provides automatic field generation and validation
    """
    class Meta:
        model = Task
        fields = ['title', 'description', 'project', 'priority', 'status', 'due_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_title(self):
        """
        Custom validation for title field
        Ensures title is not too short and doesn't contain only special characters
        """
        title = self.cleaned_data.get('title')
        if title:
            # Remove whitespace for validation
            if len(title.strip()) < 3:
                raise forms.ValidationError("Title must be at least 3 characters long.")
            # Check if title contains at least one alphanumeric character
            if not any(c.isalnum() for c in title):
                raise forms.ValidationError("Title must contain at least one letter or number.")
        return title

# Function-Based View for Task Creation
def task_create_fbv(request):
    """
    FBV for creating tasks using POST method
    Demonstrates manual form handling with validation and CSRF protection
    """
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect('task_list_cbv')
    else:
        form = TaskForm()

    return render(request, 'tasks/task_create_fbv.html', {'form': form})

# ASSIGNMENT 6 - BASE and GENERIC CLASS-BASED VIEWS

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

# IP7 - STATIC FILES AND DATA VISUALIZATION

# Chart Dashboard View
class ChartsDashboardView(TemplateView):
    """
    Class-based view to display Matplotlib and Plotly charts.
    """
    template_name = 'tasks/charts_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # --- Data Aggregation ---
        chart_data = self.get_chart_data()
        context['chart_data'] = chart_data

        # --- Chart Generation ---
        context['matplotlib_chart'] = self.generate_matplotlib_chart(chart_data)
        context['plotly_chart'] = self.generate_plotly_chart(chart_data)

        # --- Overall Stats ---
        context['total_stats'] = {
            'total_tasks': Task.objects.count(),
            'completed_tasks': Task.objects.filter(status=Status.DONE).count(),
            'pending_tasks': Task.objects.exclude(status=Status.DONE).count(),
        }

        return context

    def get_chart_data(self):
        """
        Gathers and aggregates all data needed for the charts.
        Returns keys compatible with both the template (status_data/priority_data/project_data)
        and the plotting helpers (status_breakdown/priority_breakdown/project_breakdown).
        """
        # Group by status with human-readable name
        status_qs = (
            Task.objects
            .values('status')
            .annotate(
                count=Count('id'),
                status_name=Case(
                    When(status=Status.TODO, then=Value('To Do')),
                    When(status=Status.DOING, then=Value('In Progress')),
                    When(status=Status.DONE, then=Value('Done')),
                    default=Value('Unknown'),
                    output_field=CharField(),
                ),
            )
            .order_by('status')
        )

        # Group by priority with human-readable name
        priority_qs = (
            Task.objects
            .values('priority')
            .annotate(
                count=Count('id'),
                priority_name=Case(
                    When(priority=Priority.LOW, then=Value('Low')),
                    When(priority=Priority.MED, then=Value('Medium')),
                    When(priority=Priority.HIGH, then=Value('High')),
                    default=Value('Unknown'),
                    output_field=CharField(),
                ),
            )
            .order_by('priority')
        )

        # Group by project
        project_qs = (
            Project.objects
            .annotate(task_count=Count('tasks'))
            .order_by('-task_count')[:5]
        )

        return {
            # For template compatibility
            'status_data': list(status_qs),
            'priority_data': list(priority_qs),
            'project_data': list(project_qs),  # model instances with .name and .task_count

            # For plotting helpers
            'status_breakdown': list(status_qs),
            'priority_breakdown': list(priority_qs),
            'project_breakdown': list(project_qs),
        }

    def generate_matplotlib_chart(self, chart_data):
        """
        Generates a Matplotlib chart (pie + bar) and returns it as a base64 string.
        """
        # --- Data Preparation ---
        status_labels = [Status(item['status']).label if isinstance(item, dict) else Status(item.status).label for item in chart_data['status_breakdown']]
        status_counts = [item['count'] if isinstance(item, dict) else item.count for item in chart_data['status_breakdown']]

        priority_labels = [Priority(item['priority']).label if isinstance(item, dict) else Priority(item.priority).label for item in chart_data['priority_breakdown']]
        priority_counts = [item['count'] if isinstance(item, dict) else item.count for item in chart_data['priority_breakdown']]

        # --- Charting ---
        plt.style.use('seaborn-v0_8-talk')
        illinois_colors = ['#13294B', '#FF5F05', '#E8F4FD', '#000000'] # Blue, Orange, Gray, Black

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Plot 1: Status Distribution (Pie Chart)
        status_data = chart_data['status_breakdown']
        status_labels = [Status(item['status']).label for item in status_data]
        status_counts = [item['count'] for item in status_data]

        ax1.set_title('Tasks by Status', fontsize=12)
        if sum(status_counts) > 0:
            ax1.pie(
                status_counts,
                labels=status_labels,
                autopct='%1.1f%%',
                startangle=90,
                colors=illinois_colors[:len(status_labels)],
                wedgeprops={'edgecolor': 'white', 'linewidth': 2}
            )
            ax1.axis('equal')
        else:
            ax1.text(0.5, 0.5, 'No tasks to display', ha='center', va='center')
            ax1.axis('off')

        # Plot 2: Tasks by Priority (Bar Chart)
        priority_data = chart_data['priority_breakdown']
        priority_labels = [Priority(item['priority']).label for item in priority_data]
        priority_counts = [item['count'] for item in priority_data]

        ax2.set_title('Tasks by Priority', fontsize=12)
        ax2.bar(priority_labels, priority_counts, color=illinois_colors[:len(priority_labels)])
        ax2.set_ylabel('Number of Tasks')
        ax2.grid(axis='y', linestyle='--', alpha=0.7)

        plt.tight_layout(rect=[0, 0, 1, 0.96])

        # --- Convert to Base64 ---
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=90)
        plt.close(fig)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def generate_plotly_chart(self, chart_data):
        """
        Generates an interactive Plotly bar chart and returns it as JSON.
        """
        project_names = [p.name for p in chart_data['project_breakdown']]
        project_counts = [p.task_count for p in chart_data['project_breakdown']]

        fig = go.Figure(data=[
            go.Bar(
                x=project_names,
                y=project_counts,
                marker_color=['#13294B', '#FF5F05', '#1E90FF', '#FFD700', '#32CD32'],
                text=project_counts,
                textposition='auto'
            )
        ])

        fig.update_layout(
            title_text='Top 5 Projects by Task Count',
            xaxis_title='Project',
            yaxis_title='Number of Tasks',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#13294B')
        )

        return json.dumps(fig, cls=PlotlyJSONEncoder)


# IP9 - JSON API ENDPOINTS AND SERVER-SIDE CHART GENERATION

def tasks_api(request):
    """
    JSON API endpoint that returns all tasks with their details.
    Uses JsonResponse for automatic JSON serialization and proper Content-Type.
    """
    try:
        tasks = Task.objects.select_related('project').all()

        tasks_data = []
        for task in tasks:
            tasks_data.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'project': task.project.name,
                'priority': task.get_priority_display(),
                'priority_value': task.priority,
                'status': task.get_status_display(),
                'status_value': task.status,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'is_overdue': task.is_overdue,
                'created_at': task.created_at.isoformat(),
            })

        # JsonResponse automatically sets Content-Type: application/json
        return JsonResponse({
            'count': len(tasks_data),
            'results': tasks_data
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)


def task_stats_api(request):
    """
    JSON API endpoint that returns task statistics and aggregations.
    Uses JsonResponse for proper JSON response with correct MIME type.
    """
    try:
        # Overall aggregations
        total_tasks = Task.objects.count()
        completed_tasks = Task.objects.filter(status=Status.DONE).count()
        overdue_tasks = Task.objects.filter(
            due_date__lt=timezone.localdate(),
            status__in=[Status.TODO, Status.DOING]
        ).count()

        # Status breakdown
        status_breakdown = []
        for status_item in Task.objects.values('status').annotate(count=Count('id')).order_by('status'):
            status_breakdown.append({
                'status': Status(status_item['status']).label,
                'status_value': status_item['status'],
                'count': status_item['count']
            })

        # Priority breakdown
        priority_breakdown = []
        for priority_item in Task.objects.values('priority').annotate(count=Count('id')).order_by('priority'):
            priority_breakdown.append({
                'priority': Priority(priority_item['priority']).label,
                'priority_value': priority_item['priority'],
                'count': priority_item['count']
            })

        # Project breakdown
        project_breakdown = []
        for project in Project.objects.annotate(task_count=Count('tasks')).order_by('-task_count'):
            project_breakdown.append({
                'id': project.id,
                'name': project.name,
                'task_count': project.task_count
            })

        return JsonResponse({
            'count': total_tasks,
            'results': {
                'overall': {
                    'total_tasks': total_tasks,
                    'completed_tasks': completed_tasks,
                    'pending_tasks': total_tasks - completed_tasks,
                    'overdue_tasks': overdue_tasks,
                    'completion_rate': round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0
                },
                'status_breakdown': status_breakdown,
                'priority_breakdown': priority_breakdown,
                'project_breakdown': project_breakdown
            }
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)


def api_ping(request):
    """
    JsonResponse demo - Returns JSON with proper Content-Type: application/json
    Automatically serializes Python dict to JSON
    """
    try:
        return JsonResponse({
            "ok": True,
            "message": "API is working!",
            "timestamp": timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)


def api_ping_text(request):
    """
    HttpResponse demo - Returns plain text with Content-Type: text/plain
    Must manually format the response string
    """
    try:
        return HttpResponse(
            "ok: true\n"
            "message: API is working (plain text)\n"
            f"timestamp: {timezone.now().isoformat()}\n",
            content_type="text/plain"
        )
    except Exception as e:
        return HttpResponse(
            f"error: {str(e)}\n"
            "status: error\n",
            content_type="text/plain",
            status=500
        )


# CLASS-BASED API VIEW
class TaskStatsAPIView(View):
    """
    Class-based API view that returns task statistics as JSON.
    Demonstrates CBV approach to API endpoints with JsonResponse.
    """
    def get(self, request):
        try:
            # Aggregate statistics
            total_tasks = Task.objects.count()
            completed_tasks = Task.objects.filter(status=Status.DONE).count()
            overdue_tasks = Task.objects.filter(
                due_date__lt=timezone.localdate(),
                status__in=[Status.TODO, Status.DOING]
            ).count()

            # Status breakdown
            status_breakdown = []
            for status_item in Task.objects.values('status').annotate(count=Count('id')).order_by('status'):
                status_breakdown.append({
                    'status': Status(status_item['status']).label,
                    'count': status_item['count']
                })

            # Return JSON response
            return JsonResponse({
                'count': total_tasks,
                'results': {
                    'total_tasks': total_tasks,
                    'completed_tasks': completed_tasks,
                    'pending_tasks': total_tasks - completed_tasks,
                    'overdue_tasks': overdue_tasks,
                    'completion_rate': round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0,
                    'status_breakdown': status_breakdown
                }
            })
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'status': 'error'
            }, status=500)

def task_chart_png(request):
    """
    Server-side chart generation view that:
    1. Fetches data from our task_stats_api (with a short timeout)
    2. Falls back to local ORM aggregation if the API call fails (avoids dev-server deadlocks)
    3. Supports forcing local aggregation via query param (?local=1 or ?src=local)
    4. Uses matplotlib to create a visualization and returns PNG
    """
    try:
        # Decide data source
        src = (request.GET.get('src') or '').lower()
        force_local = request.GET.get('local') == '1' or src in {'local', 'db'}

        data = None
        if not force_local:
            # Build absolute URL for the API endpoint
            api_path = reverse('task_stats_api')
            api_url = request.build_absolute_uri(api_path)

            # Try to fetch JSON data from our API (server-side) with a short timeout
            try:
                with urllib.request.urlopen(api_url, timeout=1.0) as response:
                    data = json.load(response)
            except Exception:
                data = None

        if data is None:
            # Fallback: compute the same data structure locally
            data = {'results': _compute_task_stats_results()}

        # Create matplotlib figure
        plt.style.use('seaborn-v0_8-talk')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        # Plot 1: Status Distribution (Pie Chart)
        status_data = data['results']['status_breakdown']
        status_labels = [item['status'] for item in status_data]
        status_counts = [item['count'] for item in status_data]

        if sum(status_counts) > 0:
            ax1.pie(status_counts, labels=status_labels, autopct='%1.1f%%',
                    colors=['#13294B', '#FF5F05', '#E8F4FD'],
                    wedgeprops={'edgecolor': 'white', 'linewidth': 2})
            ax1.set_title('Task Status Distribution')
        else:
            ax1.text(0.5, 0.5, 'No tasks to display', ha='center', va='center')
            ax1.set_title('Task Status Distribution')
            ax1.axis('off')

        # Plot 2: Tasks Overview (Bar Chart)
        overview = data['results']['overall']
        metrics = ['Total', 'Completed', 'Pending', 'Overdue']
        values = [
            overview['total_tasks'],
            overview['completed_tasks'],
            overview['pending_tasks'],
            overview['overdue_tasks']
        ]

        bars = ax2.bar(metrics, values, color=['#13294B', '#28a745', '#FF5F05', '#dc3545'])
        ax2.set_title('Task Overview')
        ax2.grid(axis='y', linestyle='--', alpha=0.7)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}',
                    ha='center', va='bottom')

        plt.tight_layout()

        # Save to BytesIO buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        buffer.seek(0)

        # Return as PNG image
        return HttpResponse(buffer.getvalue(), content_type='image/png')

    except Exception as e:
        # If anything goes wrong, return a placeholder error image
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, f'Error generating chart:\n{str(e)}',
                ha='center', va='center', wrap=True)
        plt.axis('off')

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        plt.close()
        buffer.seek(0)

        return HttpResponse(buffer.getvalue(), content_type='image/png', status=500)

def _compute_task_stats_results():
    """
    Local fallback: compute the same data structure returned under 'results' by task_stats_api.
    This avoids deadlock when the dev server can't serve a nested HTTP request.
    """
    # Overall aggregations
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(status=Status.DONE).count()
    overdue_tasks = Task.objects.filter(
        due_date__lt=timezone.localdate(),
        status__in=[Status.TODO, Status.DOING]
    ).count()

    # Status breakdown
    status_breakdown = []
    for status_item in Task.objects.values('status').annotate(count=Count('id')).order_by('status'):
        status_breakdown.append({
            'status': Status(status_item['status']).label,
            'status_value': status_item['status'],
            'count': status_item['count']
        })

    # Priority breakdown
    priority_breakdown = []
    for priority_item in Task.objects.values('priority').annotate(count=Count('id')).order_by('priority'):
        priority_breakdown.append({
            'priority': Priority(priority_item['priority']).label,
            'priority_value': priority_item['priority'],
            'count': priority_item['count']
        })

    # Project breakdown
    project_breakdown = []
    for project in Project.objects.annotate(task_count=Count('tasks')).order_by('-task_count'):
        project_breakdown.append({
            'id': project.id,
            'name': project.name,
            'task_count': project.task_count
        })

    return {
        'overall': {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': total_tasks - completed_tasks,
            'overdue_tasks': overdue_tasks,
            'completion_rate': round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0
        },
        'status_breakdown': status_breakdown,
        'priority_breakdown': priority_breakdown,
        'project_breakdown': project_breakdown
    }
