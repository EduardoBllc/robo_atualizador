from rest_framework import serializers

from clientes.models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'
        read_only_fields = ('id', 'data_cadastro', 'data_alteracao')