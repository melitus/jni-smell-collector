__author__ = 'consultadd66'

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from tixdo.third_party_apps.votes.models import Vote
from django.core.urlresolvers import reverse
from tixdo.movies.models import Movies
from tixdo.users.models import User
from django.contrib.contenttypes.models import ContentType


class CreateVoteTest(APITestCase):

    def setUp(self):
        self.username = 'admin'
        self.password = 'admin'
        self.email = 'admin@gmail.com'
        self.user = User.objects.create_user(self.username, self.email, self.password)
        self.content_type = ContentType.objects.get(app_label="users", model="user")
        self.data = {'content_type': self.content_type.id, 'object_id': 1, 'user': self.user.id}

    def test_can_create_vote(self):
        response = self.client.post(reverse('vote-list'), self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ReadVoteTest(APITestCase):
    def setUp(self):
        self.vote = Vote.objects.create(content_type_id=1, object_id=1, user_id=1)

    def test_can_read_vote_list(self):
        response = self.client.get(reverse('vote-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_read_vote_detail(self):
        response = self.client.get(reverse('vote-detail', args=[self.vote.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UpdateVoteTest(APITestCase):
    def setUp(self):
        self.username = 'admin'
        self.password = 'admin'
        self.email = 'admin@gmail.com'
        self.user = User.objects.create_user(self.username, self.email, self.password)
        self.content_type = ContentType.objects.get(app_label="users", model="user")
        self.data = {'content_type': self.content_type.id, 'object_id': 1, 'user': self.user.id}
        self.vote = Vote.objects.create(content_type_id=1, object_id=1, user_id=1)

    def test_can_update_vote(self):
        response = self.client.put(reverse('vote-detail', args=[self.vote.id]), self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DeleteVoteTest(APITestCase):
    def setUp(self):
        self.vote = Vote.objects.create(content_type_id=1, object_id=1, user_id=1)

    def test_can_delete_vote(self):
        response = self.client.delete(reverse('vote-detail', args=[self.vote.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class VoteQuerysetTest(APITestCase):
    def setUp(self):
        self.username = 'admin'
        self.password = 'admin'
        self.email = 'admin@gmail.com'
        self.user = User.objects.create_user(self.username, self.email, self.password)

        self.movie = Movies.objects.create(title='movie_name', release_date='2016-01-01')

    def test_up(self):
        # user should be login to vote
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('vote-list') + 'up/', {'model': 'movies', 'id': str(self.movie.id), 'vote': 'true'})
        assert response.status_code == 200
        assert response.data['message'] == 'Successfully voted'

        response = self.client.get(reverse('vote-list') + 'up/', {'model': 'movies', 'id': str(self.movie.id)})
        assert response.data['message'] == "Please provide a like or dislike parameter."

    def test_up_post(self):
        # user should be login to vote
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(reverse('vote-list') + 'up/?model=movies&id='+str(self.movie.id)+'vote=true', content_type="application/json")
        assert response.status_code == 200
        assert response.data['message'] == 'Successfully voted'

    def test_down(self):
        # user should be login to down vote
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('vote-list') + 'down/', {'model': 'movies', 'id': str(self.movie.id)})
        assert response.status_code == 200
        assert response.data['message'] == 'Successfully un-voted'

    def test_down_post(self):
        # user should be login to down vote
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(reverse('vote-list') + 'down/?model=movies&id='+str(self.movie.id), content_type="application/json")
        assert response.status_code == 200
        assert response.data['message'] == 'Successfully un-voted'

    def test_exists(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('vote-list') + 'exists/', {'model': 'movies', 'id': str(self.movie.id)})
        assert response.status_code == 200
        assert response.data

    def test_all(self):
        self.client.login(username=self.username, password=self.password)

        # check after up-vote
        self.client.get(reverse('vote-list') + 'up/?model=movies&id='+str(self.movie.id)+'&vote=true')
        response = self.client.get(reverse('vote-list') + 'all/?model=movies&id='+str(self.movie.id))
        assert response.status_code == 200
        assert response.data

        # check after down-vote
        self.client.get(reverse('vote-list') + 'down/', {'model': 'movies', 'id': str(self.movie.id)})
        response = self.client.get(reverse('vote-list') + 'all/', {'model': 'movies', 'id': str(self.movie.id)})
        assert response.status_code == 200
        assert len(response.data) == 0

    def test_count(self):
        self.client.login(username=self.username, password=self.password)

        # check before vote
        response = self.client.get(reverse('vote-list') + 'count/', {'model': 'movies', 'id': str(self.movie.id)})
        assert response.status_code == 200
        self.assertDictEqual(response.data, {'vote_count': 0})

        # check after vote
        self.client.get(reverse('vote-list') + 'up/', {'model': 'movies', 'id': str(self.movie.id), 'vote': 'true'})
        response = self.client.get(reverse('vote-list') + 'count/', {'model': 'movies', 'id': str(self.movie.id)})
        assert response.status_code == 200
        self.assertDictEqual(response.data, {'vote_count': 1})

    def test_users(self):
        response = self.client.get(reverse('vote-list') + 'users/', {'model': 'movies', 'id': str(self.movie.id)})
        assert response.status_code == 200

    def test_likes(self):
        response = self.client.get(reverse('vote-list') + 'likes/?model=movies&id='+str(self.movie.id))
        assert response.status_code == 200