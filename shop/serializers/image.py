from rest_framework import serializers

from shop.models import Image


class ImageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('image', 'tip', 'content_type', 'object_id')


class ImageDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('image', 'tip', 'content_type', 'object_id')


class ImageInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('image', 'content_type', 'object_id')
