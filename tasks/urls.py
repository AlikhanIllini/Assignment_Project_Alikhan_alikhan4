from django.urls import path
from . import views
# Import class-based views
from .views import TaskStatsView, TaskListView, ProjectDetailView, TaskCreateView, ChartsDashboardView, TaskStatsAPIView

urlpatterns = [
    # Function-based views (Assignment 4)
    path('', views.task_board, name='task_board'),
    path('stats/', views.task_stats, name='task_stats'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('priority/<int:priority_level>/', views.tasks_by_priority, name='tasks_by_priority'),

    # ASSIGNMENT 8 - Forms & POST (FBV)
    path('create/fbv/', views.task_create_fbv, name='task_create_fbv'),

    # Class-based views (Assignment 5)
    path('cbv/', TaskListView.as_view(), name='task_list_cbv'),
    path('cbv/stats/', TaskStatsView.as_view(), name='task_stats_cbv'),
    path('cbv/project/<int:pk>/', ProjectDetailView.as_view(), name='project_detail_cbv'),
    path('cbv/create/', TaskCreateView.as_view(), name='task_create_cbv'),

    # Data Visualization (IP7)
    path('charts/', ChartsDashboardView.as_view(), name='charts_dashboard'),

    # JSON API Endpoints (Assignment 9)
    path('api/tasks/', views.tasks_api, name='tasks_api'),  # FBV - All tasks
    path('api/stats/', views.task_stats_api, name='task_stats_api'),  # FBV - Statistics
    path('api/stats/cbv/', TaskStatsAPIView.as_view(), name='task_stats_api_cbv'),  # CBV - Statistics
    path('api/chart.png', views.task_chart_png, name='task_chart_png'),  # Server-side PNG chart

    # HttpResponse vs JsonResponse Demo (Assignment 9)
    path('api/ping/', views.api_ping, name='api_ping'),  # JsonResponse
    path('api/ping/text/', views.api_ping_text, name='api_ping_text'),  # HttpResponse

    # External API Integration (IP10)
    path('api/ext/quote/', views.quote_api, name='quote_api'),  # JSON API endpoint
    path('quote/', views.quote_display, name='quote_display'),  # HTML display view
]
