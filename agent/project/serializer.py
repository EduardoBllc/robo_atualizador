from rest_framework import serializers

from agent.project.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Project
        read_only_fields = ('id', 'registered_date', 'modified_date')


    def to_representation(self, instance: Project):
        representacao = super().to_representation(instance)

        representacao['ultimo_commit'] = {
            'hash': instance.actual_commit.hexsha,
            'data': instance.actual_commit_date,
        }
        representacao['branch_ativa'] = instance.active_branch.name if instance.active_branch else None

        return representacao