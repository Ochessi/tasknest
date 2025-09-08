from rest_framework import viewsets, permissions, decorators, response, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Task
from .serializers import TaskSerializer
from .permissions import IsOwner

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_completed', 'priority', 'due_date']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'due_date', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).select_related("user").prefetch_related("categories", "tags")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @decorators.action(detail=True, methods=["patch"])
    def complete(self, request, pk=None):
        task = self.get_object()
        is_completed = request.data.get("is_completed")
        if is_completed is None:
            return response.Response({"detail": "is_completed required"}, status=400)
        task.is_completed = bool(is_completed)
        task.save()
        return response.Response(self.get_serializer(task).data, status=status.HTTP_200_OK)

    @decorators.action(detail=False, methods=["get"])
    def completed(self, request):
        """Get all completed tasks"""
        completed_tasks = self.get_queryset().filter(is_completed=True)
        serializer = self.get_serializer(completed_tasks, many=True)
        return response.Response(serializer.data)

    @decorators.action(detail=False, methods=["get"])
    def pending(self, request):
        """Get all pending tasks"""
        pending_tasks = self.get_queryset().filter(is_completed=False)
        serializer = self.get_serializer(pending_tasks, many=True)
        return response.Response(serializer.data)

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
