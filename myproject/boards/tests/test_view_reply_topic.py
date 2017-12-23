from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse, resolve

from ..models import Board, Post, Topic
from ..views import reply_topic
from ..forms import NewTopicForm

class ReplyTopicTestCase(TestCase):
    ''' 
    Base test case to be used in all `reply_topic` view tests
    '''
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.username = 'john'
        self.password = '123'
        user = User.objects.create_user(username=self.username, email='john@doe.com', password=self.password)
        self.topic = Topic.objects.create(subject='Hello, world', board=self.board, starter=user)
        Post.objects.create(message='Lorem ipsum dolor sit amet', topic=self.topic, created_by=user)
        self.url = reverse('reply_topic', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})


class LoginRequiredReplyTopicTest(ReplyTopicTestCase):
    def test_redirection(self):
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))
    

class ReplyTopicTests(ReplyTopicTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.get(self.url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)
        
    def test_view_function(self):
        view = resolve('/boards/1/topics/1/reply/')
        self.assertEquals(view.func, reply_topic)
    
    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        ''' 
        The view must contain two inputs: csrf, message textarea
        '''
        self.assertContains(self.response, '<input', 1)
        self.assertContains(self.response, '<textarea', 1)



class SucessfulReplyTopicTests(ReplyTopicTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {'message': 'Hello, world!'})     

    def test_redirection(self):
        ''' 
        A valid form submission should redirect the user
        '''
        topic_posts_url = reverse('topic_posts', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})
        self.assertRedirects(self.response, topic_posts_url)

    def test_reply_created(self):
        ''' 
        The total post count should be 2
        The one created in the `ReplyTopicTestCase` setUp
        nd another creted by the post data (self.response) in this class
        '''
        self.assertEquals(Post.objects.count(), 2)


class InvalidReplyTopicTests(ReplyTopicTestCase):
    def setUp(self):
        ''' 
        Submit an empty dictionnary to the `reply_topic` view
        '''
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {})

    def test_status_code(self):
        ''' 
        An invalid form submission should return to the same page
        '''
        self.assertEquals(self.response.status_code, 200)
    
    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)
        
        
        