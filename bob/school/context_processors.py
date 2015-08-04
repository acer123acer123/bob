from datetime import date
# Don't forget to update TEMPLATE_CONTEXT_PROCESSORS in settings.py

def active_semester_processor(request):
    return {'active_semester': request.session.get('active_semester')}

def today_processor(request):
    today = date.today()
    return {'today': today}
