from .models import Company

def company_info(request):
    """
    Adds the company information to the template context.
    """
    try:
        # Assuming you only have one company entry (the current company).
        # We use .first() to prevent an error if no company is registered yet.
        current_company = Company.objects.first()
    except Company.DoesNotExist:
        current_company = None
    except Exception:
        # Handle potential database errors during startup/testing
        current_company = None
        
    return {
        'CURRENT_COMPANY': current_company
    }