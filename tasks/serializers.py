from rest_framework import serializers
from tasks.models import Task
from categories.models import Category
from tags.models import Tag

class TaskSerializer(serializers.ModelSerializer):
    # write via ids; read via nested names
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Category.objects.all(), write_only=True, required=False
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), write_only=True, required=False
    )
    categories = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )
    tags = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )

    class Meta:
        model = Task
        fields = [
            "id", "user", "title", "description", "is_completed",
            "due_date", "priority", "created_at", "updated_at",
            "categories", "tags", "category_ids", "tag_ids"
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at", "categories", "tags"]

    def create(self, validated_data):
        cat_ids = validated_data.pop("category_ids", [])
        tag_ids = validated_data.pop("tag_ids", [])
        task = Task.objects.create(**validated_data)
        if cat_ids:
            task.categories.set(cat_ids)
        if tag_ids:
            task.tags.set(tag_ids)
        return task

    def update(self, instance, validated_data):
        cat_ids = validated_data.pop("category_ids", None)
        tag_ids = validated_data.pop("tag_ids", None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if cat_ids is not None:
            instance.categories.set(cat_ids)
        if tag_ids is not None:
            instance.tags.set(tag_ids)
        return instance
