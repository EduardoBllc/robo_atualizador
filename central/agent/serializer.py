from rest_framework import serializers

from central.agent.models import Agent


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = '__all__'
        read_only_fields = ('id', 'registered_date', 'modified_date')