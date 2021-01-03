from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from todoapi.models import Todo
from todoapi.serializers import TodoSerializer

import json

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework.request import Request


# PREPERATIONS
# ==============================
# Test parameters
user_data_1 = {'name': 'testuser1', 'email': 'test1@example.com', 'password': 'Test.1234'}
user_data_2 = {'name': 'testuser2', 'email': 'test2@example.com', 'password': 'Jest.1234'}
# todo_endpoint = '/todos/'   # No need to use this constant
todo_payload_1 = {'title': 'new todo', 'content': 'You have to do this'}
todo_payload_2 = {'title': 'another todo', 'content': 'Some boring task'}
invalid_todo_payload_1 = {'title': '', 'content': 'Not blank'}
invalid_todo_payload_2 = {'title': 'Not blank', 'content': ''}
invalid_todo_payload_3 = {'title': 'Not blank', 'content': 'Not blank', 'user': 1}
updated_payload_1 = {'title': 'altered todo', 'content': 'You still have to do this', 'is_finished': True}
edited_payload_1 = {'title': 'altered field'}
list_url = reverse('todo-list')


# Helper functions
def get_detail_url(pk):
    return reverse('todo-detail', args=[pk])


def create_user(user_data):
    user = get_user_model().objects.create_user(
            email=user_data["email"],
            username=user_data["name"],
            password=user_data["password"]
            )
    return user


def create_todo(payload):
    Todo.objects.create(
        title=payload["title"],
        content=payload["content"],
        is_finished=payload.get("is_finished", False),
        user=get_user(payload.get("user", 1))
        )

    
def get_all_todos():
    return Todo.objects.all()


def get_single_todo(pk):
    return Todo.objects.get(pk=pk)


def delete_todo(pk):
    todo = get_single_todo(pk)
    todo.delete()
    

def get_user(pk):
    return get_user_model().objects.get(pk=pk)


def get_all_users():
    return get_user_model().objects.all()


# TESTING MODELS
# ==============================
class TodoTest(TestCase):
    """ Test model for todo model """
    def setUp(self):
        create_user(user_data_1)
        create_todo(todo_payload_1)
        self.todo = get_single_todo(1)
        
        
    def test_todo_title(self):
        self.assertEqual(self.todo.title, todo_payload_1["title"])


    def test_todo_content(self):
        self.assertEqual(self.todo.content, todo_payload_1["content"])

                         
    def test_todo_user(self):
        self.assertEqual(self.todo.user.id, get_user(1).id)

                         
    def test_todo_is_finished(self):
        self.assertEqual(self.todo.is_finished, False)

    
# TESTING API
# ==============================
class TodoTests(APITestCase):
    def setUp(self):
        # Creating users to be able to create todos and force first user to authenticate
        self.user_1 = create_user(user_data_1)
        self.user_2 = create_user(user_data_2)
        self.client.force_authenticate(self.user_1)
        create_todo(todo_payload_1)

        
    def test_create_todo(self):
        """
        Ensure that we can create a todo
        """
        # Delete the todo record created in setUp, we need to create from scratch using POST request 
        delete_todo(1)
        # Creating a todo by posting some arbitrary data
        response = self.client.post(list_url, todo_payload_1, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)      
        self.assertEqual(Todo.objects.count(), 1)
        self.assertEqual(Todo.objects.get().title, todo_payload_1["title"])


    def test_create_invalid_todo(self):
        """
        Ensure that we cannot create invalid todo
        For example a todo object without title or content
        or with user field specified (User has to be authenticated user)
        """
        response1 = self.client.post(list_url, invalid_todo_payload_1,
                                   content_type='application/json')
        response2 = self.client.post(list_url, invalid_todo_payload_2,
                                   content_type='application/json')
        response3 = self.client.post(list_url, invalid_todo_payload_3,
                                   content_type='application/json')
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)

        

    def test_retrieve_todo(self):
        """
        Ensure that we can retrieve todos
        """
        # Creating second todo to get them as a list of items
        create_todo(todo_payload_2)
        todos = get_all_todos()
        response = self.client.get(list_url)
        factory = APIRequestFactory()
        request = factory.get(list_url)
        context = {'request': request}
        serializer = TodoSerializer(todos, context=context, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Todo.objects.count(), 2)        
        self.assertEqual(response.data["results"], serializer.data)
        

    def test_get_single_todo(self):
        """
        Ensure that we can get single item
        """
        todo_1 = get_single_todo(1)
        response = self.client.get(get_detail_url(1))
        factory = APIRequestFactory()
        request = factory.get(get_detail_url(1))
        context = {'request': request}
        serializer = TodoSerializer(todo_1, context=context)
        results = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(results, serializer.data)
        

    def test_get_single_invalid_todo(self):
        """
        Ensure that we cannot get an item if it is no in the database
        """
        response = self.client.get(get_detail_url(100))
        results = response.data
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_update_todo(self):
        """
        We can update 3 editable fields: title, content and is_finished
        """
        response = self.client.put(get_detail_url(1), data=updated_payload_1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], updated_payload_1["title"])



    def test_edit_todo(self):
        """
        Ensure that we can update only one field using PATCH request
        As our case we are updating only title field
        """
        response = self.client.patch(get_detail_url(1), data=edited_payload_1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], edited_payload_1["title"])

                         
    def test_delete_todo(self):
        """
        Ensure that we can remove one item from db using DELETE request
        """
        response = self.client.delete(get_detail_url(1))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

 
