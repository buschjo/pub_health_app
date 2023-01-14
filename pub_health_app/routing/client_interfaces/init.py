from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


from ..buisness_logic.router import Router

router = Router()

@api_view(['POST'])
def get_map(request):
    return Response(status=status.HTTP_204_NO_CONTENT)