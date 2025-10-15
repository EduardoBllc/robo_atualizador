from rest_framework import serializers

class SelfRegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=True)
    ip_address = serializers.IPAddressField(required=True)
    port = serializers.IntegerField(required=False)
    uses_tls = serializers.BooleanField(default=False, required=False)

    def to_representation(self, instance):
        return {
            'name': instance['name'],
            'ip_address': instance['ip_address'],
            'port': instance['port'],
            'uses_tls': instance['uses_tls'],
        }