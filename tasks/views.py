from rest_framework import viewsets, permissions, decorators, response, status, serializers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Task
from .serializers import TaskSerializer
from .permissions import IsOwner

# Response serializers for Swagger documentation
class TaskStatsResponseSerializer(serializers.Serializer):
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()
    high_priority_tasks = serializers.IntegerField()
    completion_rate = serializers.FloatField()

class TaskCompletionSerializer(serializers.Serializer):
    is_completed = serializers.BooleanField()

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_completed', 'priority', 'due_date']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'due_date', 'priority']
    ordering = ['-created_at']
    
    @swagger_auto_schema(
        operation_description="List all tasks for the authenticated user",
        responses={
            200: openapi.Response(
                description="List of tasks",
                schema=TaskSerializer(many=True)
            )
        },
        tags=['Tasks']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new task",
        request_body=TaskSerializer,
        responses={
            201: openapi.Response(
                description="Task created successfully",
                schema=TaskSerializer
            ),
            400: openapi.Response(
                description="Validation error"
            )
        },
        tags=['Tasks']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Retrieve a specific task",
        responses={
            200: openapi.Response(
                description="Task details",
                schema=TaskSerializer
            ),
            404: openapi.Response(
                description="Task not found"
            )
        },
        tags=['Tasks']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update a task completely",
        request_body=TaskSerializer,
        responses={
            200: openapi.Response(
                description="Task updated successfully",
                schema=TaskSerializer
            ),
            400: openapi.Response(
                description="Validation error"
            ),
            404: openapi.Response(
                description="Task not found"
            )
        },
        tags=['Tasks']
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Partially update a task",
        request_body=TaskSerializer,
        responses={
            200: openapi.Response(
                description="Task updated successfully",
                schema=TaskSerializer
            ),
            400: openapi.Response(
                description="Validation error"
            ),
            404: openapi.Response(
                description="Task not found"
            )
        },
        tags=['Tasks']
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Delete a task",
        responses={
            204: openapi.Response(
                description="Task deleted successfully"
            ),
            404: openapi.Response(
                description="Task not found"
            )
        },
        tags=['Tasks']
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).select_related("user").prefetch_related("categories", "tags")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        method='patch',
        operation_description="Mark a task as completed or incomplete",
        request_body=TaskCompletionSerializer,
        responses={
            200: openapi.Response(
                description="Task completion status updated",
                schema=TaskSerializer
            ),
            400: openapi.Response(
                description="is_completed field is required",
                examples={
                    "application/json": {
                        "detail": "is_completed required"
                    }
                }
            ),
            404: openapi.Response(
                description="Task not found"
            )
        },
        tags=['Tasks']
    )
    @decorators.action(detail=True, methods=["patch"])
    def complete(self, request, pk=None):
        task = self.get_object()
        is_completed = request.data.get("is_completed")
        if is_completed is None:
            return response.Response({"detail": "is_completed required"}, status=400)
        task.is_completed = bool(is_completed)
        task.save()
        return response.Response(self.get_serializer(task).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        method='get',
        operation_description="Get all completed tasks for the authenticated user",
        responses={
            200: openapi.Response(
                description="List of completed tasks",
                schema=TaskSerializer(many=True)
            )
        },
        tags=['Tasks']
    )
    @decorators.action(detail=False, methods=["get"])
    def completed(self, request):
        """Get all completed tasks"""
        completed_tasks = self.get_queryset().filter(is_completed=True)
        serializer = self.get_serializer(completed_tasks, many=True)
        return response.Response(serializer.data)

    @swagger_auto_schema(
        method='get',
        operation_description="Get all pending (incomplete) tasks for the authenticated user",
        responses={
            200: openapi.Response(
                description="List of pending tasks",
                schema=TaskSerializer(many=True)
            )
        },
        tags=['Tasks']
    )
    @decorators.action(detail=False, methods=["get"])
    def pending(self, request):
        """Get all pending tasks"""
        pending_tasks = self.get_queryset().filter(is_completed=False)
        serializer = self.get_serializer(pending_tasks, many=True)
        return response.Response(serializer.data)

    @swagger_auto_schema(
        method='get',
        operation_description="Get task statistics for the authenticated user",
        responses={
            200: openapi.Response(
                description="Task statistics",
                schema=TaskStatsResponseSerializer
            )
        },
        tags=['Tasks']
    )
    @decorators.action(detail=False, methods=["get"])
    def stats(self, request):
        """Get task statistics for the user"""
        queryset = self.get_queryset()
        total_tasks = queryset.count()
        completed_tasks = queryset.filter(is_completed=True).count()
        pending_tasks = queryset.filter(is_completed=False).count()
        high_priority = queryset.filter(priority='High').count()
        
        return response.Response({
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'high_priority_tasks': high_priority,
            'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2)
        })
