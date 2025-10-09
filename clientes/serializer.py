from rest_framework import serializers

from clientes.models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        exclude = ['data_cadastro', 'data_alteracao']