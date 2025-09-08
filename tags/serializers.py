from rest_framework import serializers
from tags.models import Tag

class TagSerializer(serializers.ModelSerializer):
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = ["id", "name", "color", "created_at", "task_count"]
        read_only_fields = ["id", "created_at", "task_count"]
    
    def get_task_count(self, obj):
        return obj.tasks.count()
