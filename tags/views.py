from rest_framework import viewsets, permissions
from tags.models import Tag
from .serializers import TagSerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by("name")
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
