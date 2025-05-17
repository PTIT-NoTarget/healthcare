from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Nurse
from .serializers import NurseSerializer
from .permissions import IsNurseOrAdmin, IsAdminUser

class NurseCreateView(generics.CreateAPIView):
    queryset = Nurse.objects.all()
    serializer_class = NurseSerializer
    permission_classes = [permissions.AllowAny]

class NurseDetailView(generics.RetrieveUpdateAPIView):
    queryset = Nurse.objects.all()
    serializer_class = NurseSerializer
    permission_classes = [IsNurseOrAdmin]

class NurseListView(generics.ListAPIView):
    queryset = Nurse.objects.all()
    serializer_class = NurseSerializer
    permission_classes = [IsNurseOrAdmin]
