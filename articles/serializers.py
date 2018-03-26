from django.contrib.auth.models import User
from .models import Article, Sentence 
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class SentenceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sentence
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    
    sentences = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Article
        fields = '__all__'
