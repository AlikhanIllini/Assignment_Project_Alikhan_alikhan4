# Django Views Presentation - Task Board Project
## Assignment 4 - 150 Second Presentation

---

## Slide 1: Project Overview & Views List

### 🎯 Task Board Project
**A kanban-style task management system with projects and priority tracking**

### 📋 Views I'm Presenting (4 Total):
1. **HttpResponse View**: `task_stats()` - Returns JSON task statistics
2. **render() View**: `task_board()` - Main kanban board with template
3. **Detail View**: `project_detail()` - Shows tasks for specific project
4. **Filter View**: `tasks_by_priority()` - Filters tasks by priority level

### 🗂️ Data Model:
- **Project** (container) → **Task** (with priority, status, due dates)
- ForeignKey relationship with CASCADE delete

---

## Slide 2: HttpResponse vs render() Views

### 🔧 View 1: HttpResponse (API-style)
```python
def task_stats(request):
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
        'completion_rate': f"{(completed_tasks/total_tasks*100):.1f}%"
    }
    
    return HttpResponse(json.dumps(stats), content_type='application/json')
```

**URL**: `/tasks/stats/`
**Output**: Raw JSON response
```json
{"total_tasks": 6, "completed_tasks": 1, "overdue_tasks": 0, "completion_rate": "16.7%"}
```

### 🖼️ View 2: render() (Template-based)
```python
def task_board(request):
    projects = Project.objects.all()
    todo_tasks = Task.objects.filter(status=Status.TODO)
    doing_tasks = Task.objects.filter(status=Status.DOING) 
    done_tasks = Task.objects.filter(status=Status.DONE)
    
    context = {
        'projects': projects,
        'todo_tasks': todo_tasks,
        'doing_tasks': doing_tasks,
        'done_tasks': done_tasks,
        'overdue_tasks': overdue_tasks,
        'current_date': timezone.localdate(),
    }
    
    return render(request, 'tasks/board.html', context)
```

**URL**: `/tasks/`
**Output**: Rendered HTML kanban board with 3 columns (To Do, In Progress, Done)

---

## Slide 3: Additional Views - Detail & Filter

### 🔍 View 3: Project Detail View
```python
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = project.tasks.all()
    
    task_counts = {
        'total': tasks.count(),
        'todo': tasks.filter(status=Status.TODO).count(),
        'doing': tasks.filter(status=Status.DOING).count(),
        'done': tasks.filter(status=Status.DONE).count(),
    }
    
    context = {'project': project, 'tasks': tasks, 'task_counts': task_counts}
    return render(request, 'tasks/project_detail.html', context)
```

**URL**: `/tasks/project/1/` (dynamic project ID)
**Features**: Error handling with `get_object_or_404`, task statistics

### 🎯 View 4: Priority Filter View
```python
def tasks_by_priority(request, priority_level):
    try:
        priority = int(priority_level)
        if priority not in [Priority.LOW, Priority.MED, Priority.HIGH]:
            raise ValueError
    except (ValueError, TypeError):
        return HttpResponse("Invalid priority level", status=400)
    
    tasks = Task.objects.filter(priority=priority)
    priority_name = Priority(priority).label
    
    context = {'tasks': tasks, 'priority_level': priority, 'priority_name': priority_name}
    return render(request, 'tasks/tasks_by_priority.html', context)
```

**URL**: `/tasks/priority/3/` (1=Low, 2=Medium, 3=High)
**Features**: URL parameter validation, error handling, filtering

---

## Slide 4: Template Inheritance & URL Routing

### 🏗️ Template Structure with {% block %} tags:

**base.html** (Template inheritance):
```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Task Board{% endblock %}</title>
</head>
<body>
    <div class="header">
        <h1>{% block header %}Task Board{% endblock %}</h1>
    </div>
    <nav class="nav">
        <a href="{% url 'task_board' %}">Board</a>
        <a href="{% url 'task_stats' %}">Stats</a>
    </nav>
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

### 🔄 {% for %} Loop with {% empty %} in board.html:
```html
{% for task in todo_tasks %}
    <div class="card">
        <h4>{{ task.title }}</h4>
        <p>{{ task.description|truncatewords:10 }}</p>
        <p><strong>Priority:</strong> {{ task.get_priority_display }}</p>
        {% if task.is_overdue %}
            <span style="color: red;">⚠️ OVERDUE</span>
        {% endif %}
    </div>
{% empty %}
    <div class="card">
        <p>No tasks to do! 🎉</p>
    </div>
{% endfor %}
```

### 🛣️ URL Routing Structure:
```python
# appserver/urls.py
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),                    # Root homepage
    path("tasks/", include("tasks.urls")),          # Include tasks URLs
]

# tasks/urls.py  
urlpatterns = [
    path('', views.task_board, name='task_board'),                      # /tasks/
    path('stats/', views.task_stats, name='task_stats'),               # /tasks/stats/
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),  # /tasks/project/1/
    path('priority/<int:priority_level>/', views.tasks_by_priority, name='tasks_by_priority'),  # /tasks/priority/3/
]
```

### 🔄 Request → View → Template → Browser Flow:
```
1. Browser: GET /tasks/
2. URLs: tasks/ → views.task_board
3. View: Queries database → Creates context dict
4. Template: board.html extends base.html → Renders with context
5. Browser: Receives complete HTML kanban board
```

---

## Key Features Demonstrated:

✅ **HttpResponse** view returning raw JSON  
✅ **render()** view with template and context  
✅ **{% for %}** loops with **{% empty %}** clauses  
✅ **Template inheritance** with {% block %} tags  
✅ **URL parameters** and error handling  
✅ **Database queries** and filtering  
✅ **GET request handling** and context passing  

### URLs to Test:
- `/` - Simple HttpResponse homepage
- `/tasks/` - Main kanban board (render)
- `/tasks/stats/` - JSON statistics (HttpResponse)
- `/tasks/project/1/` - Project detail
- `/tasks/priority/3/` - High priority tasks
