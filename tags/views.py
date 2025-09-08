from rest_framework import viewsets, permissions, decorators, response
from rest_framework.filters import SearchFilter, OrderingFilter
from tags.models import Tag
from .serializers import TagSerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by("name")
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @decorators.action(detail=True, methods=["get"])
    def tasks(self, request, pk=None):
        """Get all tasks for this tag"""
        tag = self.get_object()
        tasks = tag.tasks.filter(user=request.user)
        from tasks.serializers import TaskSerializer
        serializer = TaskSerializer(tasks, many=True)
        return response.Response(serializer.data)
