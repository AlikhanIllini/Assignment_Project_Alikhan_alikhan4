from django.urls import path
from . import views

# Import class-based views
from .views import TaskStatsView, TaskListView, ProjectDetailView, TaskCreateView, ChartsDashboardView

urlpatterns = [
    # Function-based views (Assignment 4)
    path('', views.task_board, name='task_board'),
    path('stats/', views.task_stats, name='task_stats'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('priority/<int:priority_level>/', views.tasks_by_priority, name='tasks_by_priority'),

    # Class-based views (Assignment 5)
    path('cbv/', TaskListView.as_view(), name='task_list_cbv'),
    path('cbv/stats/', TaskStatsView.as_view(), name='task_stats_cbv'),
    path('cbv/project/<int:pk>/', ProjectDetailView.as_view(), name='project_detail_cbv'),
    path('cbv/create/', TaskCreateView.as_view(), name='task_create_cbv'),

    # Data Visualization (IP7)
    path('charts/', ChartsDashboardView.as_view(), name='charts_dashboard'),
    path('chart/matplotlib.png', views.matplotlib_chart_png, name='matplotlib_chart_png'),
]
