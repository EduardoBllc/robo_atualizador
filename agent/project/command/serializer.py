from rest_framework import serializers

from agent.project.command.models import Command


class CommandSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Command
        read_only_fields = ('id', 'registered_date', 'modified_date')
    