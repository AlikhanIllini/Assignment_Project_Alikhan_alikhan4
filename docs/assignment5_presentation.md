# Assignment 5 Presentation: Class-Based Views
## Task Board Project - Django CBV Implementation

---

## Slide 1: Project Overview & Class-Based Views List
**Time: 30 seconds**

### 🎯 Project Reminder
**Task Board** - A kanban-style task management system with projects, tasks, priorities, and due dates. Users can organize tasks across To Do, In Progress, and Done columns with overdue tracking.

### 📋 Class-Based Views I'm Presenting (4 Total):

1. **Base View**: `TaskStatsView` 
   - Inherits from Django's base `View` class
   - Manual GET request handling for task statistics dashboard

2. **Generic ListView**: `TaskListView`
   - Uses Django's generic `ListView` 
   - Paginated display of all tasks with filtering and counts

3. **Generic DetailView**: `ProjectDetailView`
   - Uses Django's generic `DetailView`
   - Individual project page showing all associated tasks

4. **Generic CreateView**: `TaskCreateView`
   - Uses Django's generic `CreateView`
   - Form-based task creation with automatic validation

### 🔄 Key Improvement: URL Refactoring
- Moved from direct URL patterns to app-level `urls.py` with `include()`
- Added named URL patterns for reverse lookups in templates

---

## Slide 2: Base View - TaskStatsView
**Time: 30 seconds**

### 🔧 Code Snippet:
```python
class TaskStatsView(View):
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
            'completion_rate': f"{(completed_tasks/total_tasks*100):.1f}%"
        }
        
        return render(request, 'tasks/stats.html', context)
```

### 🛣️ Request Flow:
```
Browser: GET /tasks/cbv/stats/
    ↓
URLs: TaskStatsView.as_view()
    ↓  
View: get() method → database queries → context creation
    ↓
Template: stats.html renders with context
    ↓
Browser: Displays colorful statistics dashboard
```

### ✨ Key Features:
- **Manual method handling**: Custom `get()` method for HTTP requests
- **Database aggregation**: Multiple query operations for statistics  
- **Context preparation**: Dictionary passed to template
- **Class-based organization**: Better than function-based approach

### 🖼️ Screenshot: `/tasks/cbv/stats/`
*Shows 4 colorful stat boxes: Total Tasks, Completed, Overdue, Completion Rate*

---

## Slide 3: Generic ListView - TaskListView  
**Time: 30 seconds**

### 🔧 Code Snippet:
```python
class TaskListView(ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 10
    ordering = ['status', '-priority', 'due_date']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = Task.objects.count()
        context['status_counts'] = {
            'todo': Task.objects.filter(status=Status.TODO).count(),
            'doing': Task.objects.filter(status=Status.DOING).count(),
            'done': Task.objects.filter(status=Status.DONE).count(),
        }
        return context
```

### 🛣️ Request Flow:
```
Browser: GET /tasks/cbv/
    ↓
URLs: TaskListView.as_view()
    ↓
View: Auto queryset → pagination → custom context
    ↓
Template: task_list.html with {% for %}/{% empty %}
    ↓
Browser: Displays paginated task list with counts
```

### ✨ Key Features:
- **Automatic pagination**: 10 tasks per page with navigation
- **Custom ordering**: Status, priority, due date sorting
- **Extended context**: Additional data beyond default queryset
- **Built-in functionality**: Less code than function-based views

### 🔄 Template {% for %} with {% empty %}:
```html
{% for task in tasks %}
    <div class="card">
        <h4>{{ task.title }}</h4>
        <p>{{ task.description }}</p>
    </div>
{% empty %}
    <div class="card">
        <h4>No tasks found</h4>
        <p>Use the "Create New Task" button to add your first task.</p>
    </div>
{% endfor %}
```

### 🖼️ Screenshot: `/tasks/cbv/`
*Shows paginated task list, status counts, pagination controls*

---

## Slide 4: Generic DetailView & CreateView
**Time: 30 seconds**

### 🔍 DetailView Code:
```python
class ProjectDetailView(DetailView):
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
        return context
```

### ➕ CreateView Code:
```python
class TaskCreateView(CreateView):
    model = Task
    template_name = 'tasks/task_create.html'
    fields = ['title', 'description', 'project', 'priority', 'status', 'due_date']
    success_url = reverse_lazy('task_list_cbv')
    
    def form_valid(self, form):
        messages.success(self.request, f'Task "{form.instance.title}" created!')
        return super().form_valid(form)
```

### ✨ Key Features:
- **DetailView**: Automatic object retrieval with `get_object()`
- **CreateView**: Automatic form generation and validation
- **Success handling**: Messages and redirects built-in
- **URL parameters**: `<int:pk>` automatically passed to view

### 🖼️ Screenshots:
- **DetailView**: `/tasks/cbv/project/1/` - Project with all tasks
- **CreateView**: `/tasks/cbv/create/` - Task creation form

---

## Slide 5: Template Inheritance & URL Refactoring
**Time: 30 seconds**

### 🏗️ Template Inheritance (base.html):
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
        <a href="{% url 'task_list_cbv' %}">Tasks (CBV)</a>
        <a href="{% url 'task_stats_cbv' %}">Stats (CBV)</a>
        <a href="{% url 'task_create_cbv' %}">Create Task</a>
    </nav>
    
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

### 🛣️ URL Refactoring Structure:
```python
# appserver/urls.py (Project Level)
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("tasks/", include("tasks.urls")),  # 🔄 include() for app-level routing
]

# tasks/urls.py (App Level) 
urlpatterns = [
    # Class-based views with named patterns
    path('cbv/', TaskListView.as_view(), name='task_list_cbv'),
    path('cbv/stats/', TaskStatsView.as_view(), name='task_stats_cbv'),
    path('cbv/project/<int:pk>/', ProjectDetailView.as_view(), name='project_detail_cbv'),
    path('cbv/create/', TaskCreateView.as_view(), name='task_create_cbv'),
]
```

### 🔄 Benefits of URL Refactoring:
- **Better organization**: App-specific URLs in separate file
- **Named patterns**: `{% url 'task_list_cbv' %}` for reverse lookups
- **Maintainability**: Easier to modify and extend URL structure
- **Namespace support**: Prevents URL name conflicts

### 📋 Template Features Demonstrated:
- **{% block %} inheritance**: title, header, content blocks
- **{% url %} reverse lookups**: Named URL pattern references  
- **{% for %} with {% empty %}**: Graceful handling of empty querysets
- **Template filters**: `|date:"M d, Y"`, `|truncatewords:15`

---

## 🎯 Key Learning Points Summary

### Class-Based Views vs Function-Based Views:
- **CBVs**: Object-oriented, reusable, built-in functionality
- **FBVs**: Procedural, explicit, more control

### Generic Views Benefits:
- **Less code**: Automatic handling of common patterns
- **Built-in features**: Pagination, form handling, object retrieval
- **Consistency**: Standard Django patterns and practices

### URL Refactoring Benefits:  
- **Organization**: App-level URL configuration
- **Reverse lookups**: Named patterns for template URLs
- **Maintainability**: Easier to modify and extend

---

## 📸 Screenshot Checklist:

1. **Base View**: `/tasks/cbv/stats/` - Statistics dashboard
2. **ListView**: `/tasks/cbv/` - Paginated task list  
3. **DetailView**: `/tasks/cbv/project/1/` - Project detail page
4. **CreateView**: `/tasks/cbv/create/` - Task creation form
5. **{% empty %} state**: Delete all tasks, then view `/tasks/cbv/`

---

## 🕐 Timing Breakdown (150 seconds total):
- **Slide 1**: Project overview (30s)
- **Slide 2**: Base View explanation (30s)  
- **Slide 3**: ListView with {% for %}/{% empty %} (30s)
- **Slide 4**: DetailView & CreateView (30s)
- **Slide 5**: Templates & URL refactoring (30s)

**Your Assignment 5 presentation is ready! All class-based views are implemented and functional.**
