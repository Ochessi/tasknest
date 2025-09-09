from rest_framework import viewsets, permissions, decorators, response, serializers
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
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
    
    @swagger_auto_schema(
        operation_description="List all categories",
        responses={
            200: openapi.Response(
                description="List of categories",
                schema=CategorySerializer(many=True)
            )
        },
        tags=['Categories']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new category",
        request_body=CategorySerializer,
        responses={
            201: openapi.Response(
                description="Category created successfully",
                schema=CategorySerializer
            ),
            400: openapi.Response(
                description="Validation error"
            )
        },
        tags=['Categories']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Retrieve a specific category",
        responses={
            200: openapi.Response(
                description="Category details",
                schema=CategorySerializer
            ),
            404: openapi.Response(
                description="Category not found"
            )
        },
        tags=['Categories']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update a category completely",
        request_body=CategorySerializer,
        responses={
            200: openapi.Response(
                description="Category updated successfully",
                schema=CategorySerializer
            ),
            400: openapi.Response(
                description="Validation error"
            ),
            404: openapi.Response(
                description="Category not found"
            )
        },
        tags=['Categories']
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Partially update a category",
        request_body=CategorySerializer,
        responses={
            200: openapi.Response(
                description="Category updated successfully",
                schema=CategorySerializer
            ),
            400: openapi.Response(
                description="Validation error"
            ),
            404: openapi.Response(
                description="Category not found"
            )
        },
        tags=['Categories']
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Delete a category",
        responses={
            204: openapi.Response(
                description="Category deleted successfully"
            ),
            404: openapi.Response(
                description="Category not found"
            )
        },
        tags=['Categories']
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        method='get',
        operation_description="Get all tasks for this category (filtered by authenticated user)",
        responses={
            200: openapi.Response(
                description="List of tasks in this category",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description="Task object"
                    )
                )
            ),
            404: openapi.Response(
                description="Category not found"
            )
        },
        tags=['Categories']
    )
    @decorators.action(detail=True, methods=["get"])
    def tasks(self, request, pk=None):
        """Get all tasks for this category"""
        category = self.get_object()
        tasks = category.tasks.filter(user=request.user)
        from tasks.serializers import TaskSerializer
        serializer = TaskSerializer(tasks, many=True)
        return response.Response(serializer.data)
