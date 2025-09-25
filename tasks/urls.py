from django.urls import path
from . import views

urlpatterns = [
    # Main task board view (render)
    path('', views.task_board, name='task_board'),

    # Task statistics API (HttpResponse)
    path('stats/', views.task_stats, name='task_stats'),

    # Project detail view
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),

    # Tasks filtered by priority
    path('priority/<int:priority_level>/', views.tasks_by_priority, name='tasks_by_priority'),
]
