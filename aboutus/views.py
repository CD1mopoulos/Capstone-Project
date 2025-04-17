from django.shortcuts import render
from platform_db.models import GeneralComment

# Show only the last 4 comments
def aboutus_page(request):
    comments = GeneralComment.objects.select_related('user', 'user__userdetails').order_by('-created')[:4]
    return render(request, 'aboutus/aboutus.html', {'comments': comments})
