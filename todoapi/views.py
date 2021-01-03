from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from todoapi.serializers import UserSerializer, TodoSerializer
from todoapi.models import Todo



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
 

class TodoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows to-do-list to be view or edited.
    """
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    
    def create(self, request):
        user = request.user
        data = self.request.data
        title = data.get('title', None)
        content = data.get('content', None)
        is_finished = data.get('is_finished', False)
        Todo.objects.create(
            title=title,
            content=content,
            user=user,
            is_finished=is_finished
            )
        return Response(status=status.HTTP_201_CREATED)

        
    def get_queryset(self):
        """
        Filtering againist query parameters
        """
        queryset = Todo.objects.all()
        qp = self.request.query_params
        title = qp.get('title', None)
        user = qp.get('user', None)
        content = qp.get('content', None)
        is_finished = qp.get('is_finished', None)
        created_at = qp.get('created_at', None)
        updated_at = qp.get('updated_at', None)
        # print("query params ::", qp)
        if user is not None:
            queryset = queryset.filter(user=user)
        if title is not None:
            queryset = queryset.filter(title=title)
        if content is not None:
            queryset = queryset.filter(content=content)
        if is_finished is not None:
            is_finished_true_list = ["1", "y", "yes", "t", "true"]
            if is_finished.lower() in is_finished_true_list:
                is_finished = True
            else:
                is_finished = False
            queryset = queryset.filter(is_finished=is_finished)
        if created_at is not None:
            queryset = queryset.filter(created_at=created_at)
        if updated_at is not None:
            queryset = queryset.filter(updated_at=updated_at)
        return queryset
