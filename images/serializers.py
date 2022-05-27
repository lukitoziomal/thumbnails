from rest_framework import serializers
from .models import Image, Thumbnail, TemporaryLink
from django.urls import reverse


class ThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = ('height', 'link')


class TemporaryLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryLink
        fields = ('url', 'valid_to')


class CreateLinkSerializer(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        user_admin = self.root.context['request'].user.is_staff
        if 'view' in self.root.context:
            if user_admin and self.root.context['view'].__class__.__name__ == 'AllImagesView':
                return self.queryset
        return self.queryset.filter(
            owner=self.root.context['request'].user.id
        )


class DynamicFieldsSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ImageSerializer(DynamicFieldsSerializer):
    owner = serializers.SlugRelatedField(read_only=True, slug_field='username')
    thumbnails = ThumbnailSerializer(read_only=True, many=True)
    temp_link = TemporaryLinkSerializer(read_only=True)
    temporary_link_create = CreateLinkSerializer(queryset=Image.objects.all())
    duration = serializers.IntegerField(
        min_value=300,
        max_value=30000,
        help_text='300 - 30000 seconds',
        required=False
    )

    class Meta:
        model = Image
        fields = ('owner', 'original_file', 'temp_link', 'thumbnails', 'temporary_link_create', 'duration')
        extra_kwargs = {
            'original_file': {
                'help_text': 'upload an image or create expiring link'
            }
        }
