from rest_framework import serializers

from aplicacao.models import Aplicacao


class AplicacaoSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Aplicacao
        read_only_fields = ('id', 'data_cadastro', 'data_alteracao')


    def to_representation(self, instance: Aplicacao):
        representacao = super().to_representation(instance)

        representacao['ultimo_commit'] = {
            'hash': instance.commit_atual.hexsha,
            'data': instance.data_commit_atual,
        }
        representacao['branch_ativa'] = instance.branch_ativa.name if instance.branch_ativa else None

        return representacao