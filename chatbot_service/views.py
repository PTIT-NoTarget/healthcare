from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import json
import logging
from .chatbot_utils import get_answer, model_instance

logger = logging.getLogger(__name__)

# Create your views here.

class ChatbotAPIView(APIView):
    
    def post(self, request, format=None):
        try:
            # Get message from request
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            
            if not message:
                return Response(
                    {'error': 'No message provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Log the incoming message (optional, for debugging)
            logger.info(f"User {request.user.username} sent message: {message}")
            
            # Get response from the chatbot
            response = get_answer(message, model_instance)
            
            # Return the response
            return Response({'response': response})
            
        except Exception as e:
            logger.error(f"Error processing chatbot request: {e}")
            return Response(
                {'error': 'An error occurred while processing your request'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
