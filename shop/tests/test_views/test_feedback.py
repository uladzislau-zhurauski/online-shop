import pytest
from django.urls import reverse
from rest_framework import status

from shop.models import Feedback
from shop.serializers.feedback import FeedbackListSerializer, FeedbackDetailSerializer
from shop.tests.conftest import nonexistent_pk, ClientType, existent_pk, Arg


@pytest.mark.django_db
class TestFeedbackViews:
    def test_get_feedback_list(self, api_client):
        feedback_list = Feedback.moderated_feedback.all()
        url = reverse('feedback-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == FeedbackListSerializer(instance=feedback_list, many=True).data

    @pytest.mark.parametrize('client_type, feedback_product, title, content, images, status_code', [
        (ClientType.NOT_AUTH_CLIENT, None, None, None, None, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, None, None, None, None, status.HTTP_400_BAD_REQUEST),
        (ClientType.AUTH_CLIENT, None, None, 'content', Arg.CORRECT, status.HTTP_400_BAD_REQUEST),
        (ClientType.AUTH_CLIENT, None, 'title', 'content', Arg.CORRECT, status.HTTP_400_BAD_REQUEST),
        (ClientType.AUTH_CLIENT, nonexistent_pk, 'title', 'content', Arg.CORRECT, status.HTTP_400_BAD_REQUEST),
        (ClientType.AUTH_CLIENT, existent_pk, None, 'content', Arg.CORRECT, status.HTTP_400_BAD_REQUEST),
        (ClientType.AUTH_CLIENT, existent_pk, 'title', None, Arg.CORRECT, status.HTTP_400_BAD_REQUEST),
        (ClientType.AUTH_CLIENT, existent_pk, 'title', 'content', Arg.INCORRECT, status.HTTP_400_BAD_REQUEST),
        (ClientType.AUTH_CLIENT, existent_pk, 'title', 'content', Arg.CORRECT, status.HTTP_201_CREATED),
    ])
    def test_post_feedback(self, client_type, feedback_product, title, content, images, status_code, multi_client,
                           get_in_memory_image_file, get_in_memory_file):
        url = reverse('feedback-list')
        data = {
            'product': feedback_product or '',
            'title': title or '',
            'content': content or ''
        }
        if images == Arg.CORRECT:
            data['images'] = get_in_memory_image_file
        elif images == Arg.INCORRECT:
            data['images'] = [get_in_memory_image_file, get_in_memory_file]
        response = multi_client(client_type, None).post(url, data=data)

        assert response.status_code == status_code

    def test_get_feedback_with_nonexistent_pk(self, api_client):
        url = reverse('feedback-detail', kwargs={'pk': nonexistent_pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_unmoderated_feedback(self, api_client):
        unmoderated_feedback = Feedback.objects.filter(is_moderated=False).first()
        url = reverse('feedback-detail', kwargs={'pk': unmoderated_feedback.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_moderated_feedback(self, api_client):
        moderated_feedback = Feedback.moderated_feedback.first()
        url = reverse('feedback-detail', kwargs={'pk': moderated_feedback.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == FeedbackDetailSerializer(instance=moderated_feedback).data

    @pytest.mark.parametrize(
        'client_type, feedback_product, title, content, images, status_code', [
            (ClientType.NOT_AUTH_CLIENT, None, None, None, None, status.HTTP_403_FORBIDDEN),
            (ClientType.AUTH_CLIENT, None, None, None, None, status.HTTP_403_FORBIDDEN),
            (ClientType.ADMIN_CLIENT, None, None, None, None, status.HTTP_400_BAD_REQUEST),
            (ClientType.ADMIN_CLIENT, None, None, 'content', Arg.CORRECT, status.HTTP_400_BAD_REQUEST),
            (ClientType.ADMIN_CLIENT, None, 'title', 'content', Arg.CORRECT, status.HTTP_400_BAD_REQUEST),
            (ClientType.ADMIN_CLIENT, nonexistent_pk, 'title', 'content', Arg.CORRECT, status.HTTP_400_BAD_REQUEST),
            (ClientType.ADMIN_CLIENT, existent_pk, None, 'content', Arg.CORRECT, status.HTTP_400_BAD_REQUEST),
            (ClientType.ADMIN_CLIENT, existent_pk, 'title', None, Arg.CORRECT, status.HTTP_400_BAD_REQUEST),
            (ClientType.ADMIN_CLIENT, existent_pk, 'title', 'content', Arg.INCORRECT, status.HTTP_400_BAD_REQUEST),
            (ClientType.ADMIN_CLIENT, existent_pk, 'title', 'content', Arg.CORRECT, status.HTTP_200_OK),
            (ClientType.AUTHOR_CLIENT, None, None, None, Arg.CORRECT, status.HTTP_400_BAD_REQUEST),
            (ClientType.AUTHOR_CLIENT, None, None, 'content', Arg.CORRECT, status.HTTP_400_BAD_REQUEST),
            (ClientType.AUTHOR_CLIENT, None, 'title', 'content', Arg.CORRECT, status.HTTP_400_BAD_REQUEST),
            (ClientType.AUTHOR_CLIENT, nonexistent_pk, 'title', 'content', Arg.CORRECT, status.HTTP_400_BAD_REQUEST),
            (ClientType.AUTHOR_CLIENT, existent_pk, None, 'content', Arg.CORRECT, status.HTTP_400_BAD_REQUEST),
            (ClientType.AUTHOR_CLIENT, existent_pk, 'title', None, Arg.CORRECT, status.HTTP_400_BAD_REQUEST),
            (ClientType.AUTHOR_CLIENT, existent_pk, 'title', 'content', Arg.INCORRECT, status.HTTP_400_BAD_REQUEST),
            (ClientType.AUTHOR_CLIENT, existent_pk, 'title', 'content', Arg.CORRECT, status.HTTP_200_OK),
        ]
    )
    def test_put_feedback(self, client_type, status_code, feedback_product, title, content, images, multi_client,
                          get_in_memory_image_file, get_in_memory_file):
        moderated_feedback = Feedback.moderated_feedback.first()
        url = reverse('feedback-detail', kwargs={'pk': moderated_feedback.pk})
        data = {
            'product': feedback_product or '',
            'title': title or '',
            'content': content or ''
        }
        if images == Arg.CORRECT:
            data['images'] = get_in_memory_image_file
        elif images == Arg.INCORRECT:
            data['images'] = [get_in_memory_image_file, get_in_memory_file]
        user = moderated_feedback.author if client_type is ClientType.AUTHOR_CLIENT else None
        response = multi_client(client_type, user).put(url, data=data)

        assert response.status_code == status_code

    @pytest.mark.parametrize(
        'client_type, status_code', [
            (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
            (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
            (ClientType.ADMIN_CLIENT, status.HTTP_204_NO_CONTENT),
            (ClientType.AUTHOR_CLIENT, status.HTTP_204_NO_CONTENT),
        ]
    )
    def test_delete_feedback(self, client_type, status_code, multi_client):
        moderated_feedback = Feedback.moderated_feedback.first()
        url = reverse('feedback-detail', kwargs={'pk': moderated_feedback.pk})
        user = moderated_feedback.author if client_type is ClientType.AUTHOR_CLIENT else None
        response = multi_client(client_type, user).delete(url)

        assert response.status_code == status_code

    def test_delete_feedback_with_nonexistent_pk(self, authenticated_api_client):
        url = reverse('feedback-detail', kwargs={'pk': nonexistent_pk})
        response = authenticated_api_client(is_admin=True).delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
