from rest_framework import viewsets, permissions, decorators, response, status
from .models import Task
from .serializers import TaskSerializer
from .permissions import IsOwner

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

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
