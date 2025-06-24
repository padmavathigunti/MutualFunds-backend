from rest_framework.response import Response
from rest_framework import status as drf_status

def success_response(message, data=None, status=drf_status.HTTP_200_OK):
    return Response({
        "status": True,
        "message": message,
        "data": data
    }, status=status)

def error_response(message, errors=None, status=drf_status.HTTP_400_BAD_REQUEST):
    return Response({
        "status": False,
        "message": message,
        "errors": errors
    }, status=status)
