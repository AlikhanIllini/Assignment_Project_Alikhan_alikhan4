# IP8: Individual Presentation - Forms & POST (GET vs POST, FBV vs CBV)

---

## Slide 1: Project Overview (10-15s)

**Task Management System** - Django web app for managing tasks and projects with Kanban board functionality.

**Model Used:** Task model with fields: title, description, project, priority, status, due_date

**Three Views to Demonstrate:**
- ✅ GET Search (Task filtering with query parameters)
- ✅ FBV Create (Function-based view for task creation)
- ✅ CBV Create (Class-based view for task creation)

---

## Slide 2: GET (Search / Filter) (25-30s)

### HTML Form (method="get")
```html
<form method="get">
    <input type="text" name="q" value="{{ search_query }}" 
           placeholder="Search tasks...">
    <button type="submit">🔍 Search</button>
</form>
```

### View Logic (request.GET usage)
```python
def get_queryset(self):
    search_query = self.request.GET.get('q', '')
    if search_query:
        return queryset.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
```

### Screenshots
- **Before Search:** Shows all tasks in the list
- **After Search:** Filtered results based on query

**Why GET?** Search results are bookmarkable and idempotent (safe to repeat).

---

## Slide 3: FBV for POST (Create) (30-35s)

### Function-Based View Code
```python
def task_create_fbv(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('task_list_cbv')
    else:
        form = TaskForm()
    return render(request, 'template.html', {'form': form})
```

### Screenshots
- **Form with Validation Error:** Shows field-specific error messages
- **Success:** Task created and redirected to task list

**CSRF Protection:** `{% csrf_token %}` prevents Cross-Site Request Forgery attacks by validating a unique token on each form submission.

---

## Slide 4: CBV for POST (CreateView) (30-35s)

### Class-Based View Code
```python
class TaskCreateView(CreateView):
    model = Task
    fields = ['title', 'description', 'project', 'priority']
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list_cbv')
    
    def form_valid(self, form):
        messages.success(self.request, 'Task created!')
        return super().form_valid(form)
```

### Screenshot
- **Same Form Design:** Template can be shared between FBV and CBV approaches

**CBV Benefits:** Reduces boilerplate code and provides built-in functionality. **Prefer FBV when:** you need complex custom logic or fine-grained control.

---

## Slide 5: Security & Takeaway (20-30s)

### Security Features
- **CSRF Protection:** Prevents malicious websites from submitting forms on behalf of users
- **POST + Validation:** Ensures data integrity and prevents unauthorized state changes
- **ModelForm Validation:** Automatic field validation and data cleaning

### What I Would Harden Next
- **Authentication Check:** Require login before task creation
- **Rate Limiting:** Prevent form spam and abuse
- **POST-Only Endpoints:** Ensure state-changing operations only use POST/PUT/DELETE methods

**Key Takeaway:** Always use POST for state changes, include CSRF protection, and validate all user input.
