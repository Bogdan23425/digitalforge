from rest_framework import serializers


class ServiceHealthSerializer(serializers.Serializer):
    service = serializers.CharField()
    status = serializers.CharField()


class DetailSerializer(serializers.Serializer):
    detail = serializers.CharField()


class UpdatedCountSerializer(serializers.Serializer):
    updated_count = serializers.IntegerField()
