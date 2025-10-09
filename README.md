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

## Data Model

![ER Diagram](docs/notes/er_diagram.png)

The data model consists of two main entities: `Project` and `Task`.

-   **Project**: Represents a container for tasks. Each project has a name, an owner (a `User`), and a description.
-   **Task**: Represents a single task within a project. Each task has a title, description, priority, status, and an optional due date.

This model allows for organizing tasks into different projects, with a clear ownership structure.
