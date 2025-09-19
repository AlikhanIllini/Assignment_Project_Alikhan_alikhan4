# Task Board

A simple kanban task app with To Do, In Progress, and Done columns. Create tasks with a priority and optional due date, move them across the board, and see counts plus an overdue badge at a glance. No external APIs.

## Data Model

![ER Diagram](docs/notes/er_diagram.png)

The data model consists of two main entities: `Project` and `Task`.

-   **Project**: Represents a container for tasks. Each project has a name, an owner (a `User`), and a description.
-   **Task**: Represents a single task within a project. Each task has a title, description, priority, status, and an optional due date.

This model allows for organizing tasks into different projects, with a clear ownership structure.
