from rest_framework import viewsets, permissions, decorators, response, serializers
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
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
    
    @swagger_auto_schema(
        operation_description="List all tags",
        responses={
            200: openapi.Response(
                description="List of tags",
                schema=TagSerializer(many=True)
            )
        },
        tags=['Tags']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new tag",
        request_body=TagSerializer,
        responses={
            201: openapi.Response(
                description="Tag created successfully",
                schema=TagSerializer
            ),
            400: openapi.Response(
                description="Validation error"
            )
        },
        tags=['Tags']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Retrieve a specific tag",
        responses={
            200: openapi.Response(
                description="Tag details",
                schema=TagSerializer
            ),
            404: openapi.Response(
                description="Tag not found"
            )
        },
        tags=['Tags']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update a tag completely",
        request_body=TagSerializer,
        responses={
            200: openapi.Response(
                description="Tag updated successfully",
                schema=TagSerializer
            ),
            400: openapi.Response(
                description="Validation error"
            ),
            404: openapi.Response(
                description="Tag not found"
            )
        },
        tags=['Tags']
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Partially update a tag",
        request_body=TagSerializer,
        responses={
            200: openapi.Response(
                description="Tag updated successfully",
                schema=TagSerializer
            ),
            400: openapi.Response(
                description="Validation error"
            ),
            404: openapi.Response(
                description="Tag not found"
            )
        },
        tags=['Tags']
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Delete a tag",
        responses={
            204: openapi.Response(
                description="Tag deleted successfully"
            ),
            404: openapi.Response(
                description="Tag not found"
            )
        },
        tags=['Tags']
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        method='get',
        operation_description="Get all tasks for this tag (filtered by authenticated user)",
        responses={
            200: openapi.Response(
                description="List of tasks with this tag",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description="Task object"
                    )
                )
            ),
            404: openapi.Response(
                description="Tag not found"
            )
        },
        tags=['Tags']
    )
    @decorators.action(detail=True, methods=["get"])
    def tasks(self, request, pk=None):
        """Get all tasks for this tag"""
        tag = self.get_object()
        tasks = tag.tasks.filter(user=request.user)
        from tasks.serializers import TaskSerializer
        serializer = TaskSerializer(tasks, many=True)
        return response.Response(serializer.data)
