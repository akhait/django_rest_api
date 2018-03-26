from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from articles.models import *
from articles.serializers import *

class ArticleViewSet(ModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Article.objects.filter(author=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @detail_route(methods=['get', 'post'])
    def sentences(self, request, *args, **kwargs):
        ''' Retrieve list of sentences in an article for GET,
            add a new sentence to an article for POST.'''
        article_id = self.kwargs['pk']
        article = get_object_or_404(Article.objects.all(), pk=article_id)
        queryset = Sentence.objects.filter(article=article)

        if request.user != article.author:
            return Response(status=404)

        # GET all sentences
        if request.method == 'GET':
            serializer = SentenceSerializer(queryset, many=True)
            return Response(serializer.data)
        
        # POST a sentence
        elif request.method == 'POST':
            text = self.request.data['text']  # sentence text
            author = self.request.user  # sentence author
            num = 1  # default sentence number
            if queryset:
                num = queryset.last().num + 1  # override number
            new_sentence = Sentence.objects.create(text=self.request.data['text'],
                                                    article=article,
                                                    num=num,
                                                    author=self.request.user)
            new_sentence.save()
            serializer = SentenceSerializer(new_sentence)
            return Response(serializer.data, status=201)

    @detail_route(methods=['get', 'put', 'delete'], url_path='sentences/(?P<sentence_num>\d+)')
    def sentence_detail(self, request, *args, **kwargs):
        '''Retrieve, update or delete a sentence in an article'''
        article_id = self.kwargs['pk']
        article = get_object_or_404(Article.objects.all(), pk=article_id)
        sentence_num = self.kwargs['sentence_num']
        queryset = Sentence.objects.filter(article=article_id)
        sentence = get_object_or_404(queryset, num=sentence_num)
        serializer =  SentenceSerializer(sentence)

        if request.user != article.author:
            return Response(status=404)
       
        # GET sentence 
        if request.method == 'GET':
            return Response(serializer.data)
        
        # PUT (update) sentence
        elif request.method == 'PUT':
            for attr, value in self.request.data.items():            
                if value:  # if attribute is not in data, value shouldn't be updated
                    setattr(sentence, attr, value)
            sentence.save()
            return Response(serializer.data)

        # DELETE a sentence
        elif request.method == 'DELETE':
            sentence.delete()
            # cascade nums
            for s in Sentence.objects.filter(article=article_id, num__gt=sentence.num):
                s.num = s.num-1
                s.save()
            return Response(status=204)
