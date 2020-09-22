from django.shortcuts import render
from django.http import HttpResponse
import json, requests
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from credits.models import Person, BanList, Program, CreditRequest
from credits.serializers import CreditRequestSerializer


def index(request):
    return HttpResponse(f"Salam world!")


@api_view(['POST'])
def check_request(request):
    try:
        ser = CreditRequestSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
        return Response(ser.data, status = status.HTTP_201_CREATED)
    except Exception as e:
        print(f"Error: {e}")
    return Response({"result": "Error"}, status=status.HTTP_400_BAD_REQUEST)
