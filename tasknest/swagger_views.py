from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views import View
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Create a completely custom schema view that bypasses all authentication
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class CustomSwaggerView(View):
    def get(self, request, *args, **kwargs):
        # Create schema view with minimal configuration
        schema_view = get_schema_view(
            openapi.Info(
                title="TaskNest API",
                default_version='v1.0',
                description="TaskNest API Documentation",
            ),
            public=True,
            permission_classes=[permissions.AllowAny],
            authentication_classes=[],
        )
        
        # Get the swagger view and call it
        swagger_view = schema_view.with_ui('swagger', cache_timeout=0)
        return swagger_view(request, *args, **kwargs)

@csrf_exempt
def simple_swagger_test(request):
    """Simple test view to check if the issue is with drf-yasg itself"""
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Swagger Test</title>
    </head>
    <body>
        <h1>Swagger Test Page</h1>
        <p>If you can see this, the URL routing is working.</p>
        <p>The issue is specifically with drf-yasg configuration.</p>
    </body>
    </html>
    """)
