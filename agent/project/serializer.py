from rest_framework import serializers

from agent.project.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Project
        read_only_fields = ('id', 'registered_date', 'modified_date')


    def to_representation(self, instance: Project):
        repr = super().to_representation(instance)

        repr['last_commit'] = {
            'hash': instance.actual_commit.hexsha,
            'data': instance.actual_commit_date,
        }
        repr['active_branch'] = instance.active_branch.name if instance.active_branch else None

        return repr