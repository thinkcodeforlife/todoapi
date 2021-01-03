from django.contrib.auth.models import User
from rest_framework import serializers
from todoapi.models import Todo


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'todos']
        read_only_fields = ('id', 'username', 'todos')

        
class TodoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Todo
        fields = '__all__'
        # exclude = ('user',)
