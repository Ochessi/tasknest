from rest_framework import viewsets, permissions, decorators, response
from rest_framework.filters import SearchFilter, OrderingFilter
from categories.models import Category
from .serializers import CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @decorators.action(detail=True, methods=["get"])
    def tasks(self, request, pk=None):
        """Get all tasks for this category"""
        category = self.get_object()
        tasks = category.tasks.filter(user=request.user)
        from tasks.serializers import TaskSerializer
        serializer = TaskSerializer(tasks, many=True)
        return response.Response(serializer.data)
