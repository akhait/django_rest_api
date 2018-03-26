from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token
from rest_framework.test import APITestCase
from articles.models import *

class ArticleViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.other_user = User.objects.create_user(username='otheruser', password='pass')

    def tearDown(self):
        self.user.delete()
        self.other_user.delete()

    def test_get_articles(self):
        '''
        Test GET /articles/
        Should return list of user's articles and 200 OK
        '''
        url = reverse('articles-list')
        
        # unauthorized
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # authorized, no records
        self.client.login(username='testuser', password='pass')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])

        # authorized with records
        # adding records
        for i in range(1,4):
            article = Article.objects.create(title='Test Article '+str(i), author=self.user)
            article.save()

        # adding records as another user
        for i in range(1,3):
            article = Article.objects.create(title='Test Article (another) '+str(i),
                                            author=self.other_user)
            article.save()

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 3)

    def test_post_article(self):
        '''
        Test POST /articles/
        Should return newly created article and 201 Created
        '''
        url = reverse('articles-list')
        
        # unathorized
        resp = self.client.post(url, {'title':'New Test Article'})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # authorized
        self.client.login(username='testuser', password='pass')
        resp = self.client.post(url, {'title':'New Test Article'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['title'], 'New Test Article')

    def test_get_article(self):
        '''
        Test GET /article/<pk>/
        Should return article <pk> and 200 OK
        '''

        article = Article.objects.create(title='Test Article',
                                        author=self.user)
        
        other_article = Article.objects.create(title='Test Article (other)',
                                            author=self.other_user)

        url = reverse('articles-detail', kwargs={'pk':article.id})
        other_url = reverse('articles-detail', kwargs={'pk':other_article.id})

         # unathorized
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # authorized, not article author
        self.client.login(username='testuser', password='pass')
        resp = self.client.get(other_url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # authorized, article author
        self.client.login(username='testuser', password='pass')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['id'].replace('-',''), article.id.hex)
        self.assertEqual(resp.data['title'], 'Test Article')
        self.assertEqual(resp.data['author'], self.user.id)

    def test_update_article(self):
        '''
        Test PUT /article/<pk>/
        Should return updated article and 200 OK
        '''

        article = Article.objects.create(title='Test Article',
                                        author=self.user)

        other_article = Article.objects.create(title='Test Article (other)',
                                            author=self.other_user)

        url = reverse('articles-detail', kwargs={'pk':article.id})
        other_url = reverse('articles-detail', kwargs={'pk':other_article.id})

         # unathorized
        resp = self.client.put(url, {'title':'Changed Test Article'})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # authorized, not article author
        self.client.login(username='testuser', password='pass')
        resp = self.client.put(other_url, {'title':'Changed Test Article'})
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # authorized, article author
        self.client.login(username='testuser', password='pass')
        resp = self.client.put(url, {'title':'Changed Test Article'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['id'].replace('-',''), article.id.hex)
        self.assertEqual(resp.data['title'], 'Changed Test Article')
        self.assertEqual(resp.data['author'], self.user.id)

    def test_delete_article(self):
        '''
        Test DELETE /article/<pk>/
        Should return 204 No Content
        '''

        article = Article.objects.create(title='Test Article',
                                        author=self.user)

        other_article = Article.objects.create(title='Test Article (other)',
                                            author=self.other_user)

        url = reverse('articles-detail', kwargs={'pk':article.id})
        other_url = reverse('articles-detail', kwargs={'pk':other_article.id})

         # unathorized
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # authorized, not article author
        self.client.login(username='testuser', password='pass')
        resp = self.client.delete(other_url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # authorized, article author
        self.client.login(username='testuser', password='pass')
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_article_sentences(self):
        '''
        Test GET /article/<pk>/sentences/
        Should return article <pk> sentences and 200 OK
        '''

        article = Article.objects.create(title='Test Article',
                                        author=self.user)
        sentence = Sentence.objects.create(article=article, author=self.user)
        other_article = Article.objects.create(title='Test Article (other)',
                                            author=self.other_user)
        other_sentence = Sentence.objects.create(article=other_article,
                                            author=self.other_user)

        url = reverse('articles-sentences', kwargs={'pk':article.id})
        other_url = reverse('articles-sentences', kwargs={'pk':other_article.id})

         # unathorized
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # authorized, not article author
        self.client.login(username='testuser', password='pass')
        resp = self.client.get(other_url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # authorized, article author
        self.client.login(username='testuser', password='pass')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['article'].hex.replace('-',''), article.id.hex)

    def test_post_article_sentence(self):
        '''
        Test POST /article/<pk>/sentences/
        Should return new sentence and 201 CREATED
        '''

        article = Article.objects.create(title='Test Article',
                                        author=self.user)
        other_article = Article.objects.create(title='Test Article (other)',
                                            author=self.other_user)

        url = reverse('articles-sentences', kwargs={'pk':article.id})
        other_url = reverse('articles-sentences', kwargs={'pk':other_article.id})

         # unathorized
        resp = self.client.post(url, {'text':'Test sentence'})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # authorized, not article author
        self.client.login(username='testuser', password='pass')
        resp = self.client.post(other_url, {'text':'Test sentence'})
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # authorized, article author
        self.client.login(username='testuser', password='pass')
        for i in range(1,6):
            resp = self.client.post(url, {'text':'Test sentence'})
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
            self.assertEqual(resp.data['article'], article.id)
            self.assertEqual(resp.data['num'], i)
            self.assertEqual(resp.data['text'], 'Test sentence')

    def test_get_article_sentence(self):
        '''
        Test GET /article/<pk>/sentences/<sentence_num>/
        Should return sentence and 200 OK
        '''

        article = Article.objects.create(title='Test Article',
                                        author=self.user)
        other_article = Article.objects.create(title='Test Article (other)',
                                            author=self.other_user)
        sentence = Sentence.objects.create(article=article, author=self.user, text='test')
        other_sentence = Sentence.objects.create(article=other_article,
                                                author=self.other_user)
        url = reverse('articles-sentences/(?P<sentence-num>\d+)', kwargs={'pk':article.id,
                                                    'sentence_num':sentence.num})
        other_url = reverse('articles-sentences/(?P<sentence-num>\d+)', kwargs={'pk':other_article.id,
                                                    'sentence_num':other_sentence.num})

         # unathorized
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # authorized, not article author
        self.client.login(username='testuser', password='pass')
        resp = self.client.get(other_url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # authorized, article author
        self.client.login(username='testuser', password='pass')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['article'], article.id)
        self.assertEqual(resp.data['num'], 1)
        self.assertEqual(resp.data['text'], 'test')

    def test_update_article_sentence(self):
        '''
        Test PUT /article/<pk>/sentences/<sentence_num>/
        Should return updated sentence and 200 OK
        '''
        article = Article.objects.create(title='Test Article', author=self.user)
        other_article = Article.objects.create(title='Test Article (other)',
                                                author=self.other_user)
        sentence = Sentence.objects.create(article=article, author=self.user, text='test')
        other_sentence = Sentence.objects.create(article=other_article,
                                                author=self.other_user)
        url = reverse('articles-sentences/(?P<sentence-num>\d+)', kwargs={'pk':article.id,
                                                    'sentence_num':sentence.num})
        other_url = reverse('articles-sentences/(?P<sentence-num>\d+)', kwargs={'pk':other_article.id,
                                                    'sentence_num':other_sentence.num})

         # unathorized
        resp = self.client.put(url, {'text':'updated text'})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # authorized, not article author
        self.client.login(username='testuser', password='pass')
        resp = self.client.put(other_url, {'text':'updated text'})
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # authorized, article author
        self.client.login(username='testuser', password='pass')
        resp = self.client.put(url, {'text':'updated text'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['article'], article.id)
        self.assertEqual(resp.data['num'], 1)
        self.assertEqual(resp.data['text'], 'updated text')

    def test_delete_article_sentence(self):
        '''
        Test PUT /article/<pk>/sentences/<sentence_num>/
        Should return 204 No Content
        '''
        article = Article.objects.create(title='Test Article', author=self.user)
        other_article = Article.objects.create(title='Test Article (other)',
                                                author=self.other_user)
        sentence = Sentence.objects.create(article=article, author=self.user, text='test')
        other_sentence = Sentence.objects.create(article=other_article,
                                                author=self.other_user)
        url = reverse('articles-sentences/(?P<sentence-num>\d+)', kwargs={'pk':article.id,
                                                    'sentence_num':sentence.num})
        other_url = reverse('articles-sentences/(?P<sentence-num>\d+)', kwargs={'pk':other_article.id,
                                                    'sentence_num':other_sentence.num})

         # unathorized
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # authorized, not article author
        self.client.login(username='testuser', password='pass')
        resp = self.client.delete(other_url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # authorized, article author
        self.client.login(username='testuser', password='pass')
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
