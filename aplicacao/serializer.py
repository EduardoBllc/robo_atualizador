from rest_framework import serializers

from aplicacao.models import Aplicacao


class AplicacaoSerializer(serializers.Serializer):
    class Meta:
        fields = '__all__'
        model = Aplicacao