from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import TaskSerializer, UserLoginSerializer, UserRegistrationSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Task

class UserRegistrationAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Once the user is saved, create a token for the user
            token, created = Token.objects.get_or_create(user=user)
            # Return the token in the response
            return Response({"token": token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserLoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        serializer = TaskSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            task = serializer.save()

            return Response({'id': task.pk}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, *args, **kwargs):
        task_id = kwargs.get('task_id')
        if task_id:
            try:
                task = request.user.task_set.get(pk=task_id)
                serializer = TaskSerializer(task)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Task.DoesNotExist:
                return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            name_filter = request.query_params.get('name', None)
            desc_filter = request.query_params.get('description', None)
            due_date_from = request.query_params.get('due_date_from', None)
            due_date_to = request.query_params.get('due_date_to', None)

            filter_kwargs = {}
            if name_filter:
                filter_kwargs['name__icontains'] = name_filter
            if desc_filter:
                filter_kwargs['description__icontains'] = desc_filter
            if due_date_from:
                filter_kwargs['due_date__gte'] = due_date_from
            if due_date_to:
                filter_kwargs['due_date__lte'] = due_date_to

            tasks = request.user.task_set.filter(**filter_kwargs)

            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


