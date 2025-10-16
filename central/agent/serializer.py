from rest_framework import serializers

from central.agent.models import Agent


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = '__all__'
        read_only_fields = ('id', 'registered_date', 'modified_date')


class AgentProjectSerializer(serializers.Serializer):
    agent_id = serializers.IntegerField(required=True)
    path = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    branch_trunc = serializers.CharField(required=False)
    branch_dev = serializers.CharField(required=False)
    branch_homolog = serializers.CharField(required=False)
    branch_prod = serializers.CharField(required=False)
    remote = serializers.CharField(required=False)