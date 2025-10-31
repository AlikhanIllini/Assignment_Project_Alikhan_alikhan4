# Task Board

A simple kanban task app with To Do, In Progress, and Done columns. Create tasks with a priority and optional due date, move them across the board, and see counts plus an overdue badge at a glance. No external APIs.

## Assignment 4 Updates

Added comprehensive Django view functionality with two distinct approaches: an HttpResponse view that manually constructs HTML for task statistics, and a render() view that uses templates for the main kanban board. Both demonstrate the full request → view → template → response cycle with proper URL routing and template inheritance.

## Assignment 5 Updates

Implemented class-based views (CBVs) alongside existing function-based views to demonstrate Django's object-oriented approach to handling HTTP requests. Added base View, generic ListView, DetailView, and CreateView with proper URL refactoring using include() and app-level routing with named URL patterns for reverse lookups.

## Assignment 6 Updates

Extended the project with comprehensive comparison between BASE class-based views and GENERIC class-based views. Implemented manual View inheritance for statistics with explicit model queries, alongside Django's generic ListView, DetailView, and CreateView that automatically handle common patterns. This demonstrates the trade-off between control and convenience in Django's CBV architecture.

## Assignment 7 Updates

Implemented search/filtering and aggregations functionality to demonstrate Django's ORM capabilities. Added GET-based search form that filters tasks across multiple fields (title, description, project name) using Q() objects for OR logic. Implemented both overall aggregations (total tasks, completed count, overdue tasks) and grouped aggregations (tasks by project, tasks by status) with proper template rendering using {% for %}/{% empty %} blocks. This showcases QuerySet lazy evaluation, double-underscore field lookups, and Django's aggregation framework.

## IP7 Updates

Implemented static files management and data visualization features to demonstrate Django's static pipeline and chart generation capabilities. Added Illinois Blue and Orange theme styling using CSS custom properties, integrated Matplotlib for server-side PNG chart generation, and Plotly for interactive client-side visualizations. Created comprehensive charts dashboard showing task distribution by status, priority, and project using Django ORM aggregations with both overall totals and grouped breakdowns.

## Assignment 8 Updates

Implemented comprehensive form handling demonstrating GET vs POST methods and comparing Function-Based Views with Class-Based Views. **GET vs POST in this project**: GET is used for the search/filter functionality where query parameters appear in the URL (?q=search) allowing bookmarkable results, while POST is used for task creation forms with CSRF protection to securely submit data that modifies the database. **FBV vs CBV for forms**: The Function-Based View (task_create_fbv) provides explicit control with manual if/else branching for GET/POST methods, making the flow easy to understand but requiring more boilerplate code, while the Class-Based View (TaskCreateView) uses Django's generic CreateView to automatically handle form instantiation, validation, and success redirection with minimal code but requiring understanding of Django's class hierarchy and method overriding.

## Assignment 9 Updates

Implemented JSON API endpoints and server-side chart generation to demonstrate Django's JsonResponse capabilities and the difference between HttpResponse and JsonResponse. Created both function-based and class-based API views: `/api/tasks/` returns all tasks with count and results structure, `/api/stats/` provides aggregated statistics including overall totals and breakdowns by status/priority/project, and `/api/stats/cbv/` demonstrates the same functionality using a CBV approach. Built server-side chart generation view that fetches data from the JSON API using urllib.request, parses it with json.load(), generates matplotlib visualizations, and returns PNG images via HttpResponse with image/png content type. Added demonstration endpoints `/api/ping/` (JsonResponse with application/json) and `/api/ping/text/` (HttpResponse with text/plain) to clearly illustrate MIME type differences and automatic JSON serialization versus manual string formatting.

## Data Model

![ER Diagram](docs/notes/er_diagram.png)

The data model consists of two main entities: `Project` and `Task`.

-   **Project**: Represents a container for tasks. Each project has a name, an owner (a `User`), and a description.
-   **Task**: Represents a single task within a project. Each task has a title, description, priority, status, and an optional due date.

This model allows for organizing tasks into different projects, with a clear ownership structure.
