from django.shortcuts import render
from .services import get_chef_suggestions
from django.core.files.storage import FileSystemStorage

def chef_home(request):
    result = None
    if request.method == "POST":
        text = request.POST.get("ingredients")
        image = request.FILES.get("fridge_image")
        
        
        if not request.session.session_key:
            request.session.create()
        thread_id = request.session.session_key
        
        image_path = None
        if image:
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            image_path = fs.path(filename)
            
        result = get_chef_suggestions(text, image_path, thread_id)
        
    return render(request, "chef_app/index.html", {"result": result})