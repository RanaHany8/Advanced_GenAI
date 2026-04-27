from django.shortcuts import render
# من السطر 2:
from .services import get_chef_suggestions, nutrition_agent, NutritionAnalysis, llm
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

#lab2
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from langchain_core.messages import HumanMessage
from .services import nutrition_agent, NutritionAnalysis, llm
import base64

def nutrition_expert(request):
    result = None
    response = None 

    if request.method == "POST":
        text = request.POST.get("meal_desc")
        image = request.FILES.get("meal_image")
        
        if not request.session.session_key:
            request.session.create()
        config = {"configurable": {"thread_id": request.session.session_key}}

        content = [{"type": "text", "text": text or "Analyze this meal"}]
        
        if image:
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            img_path = fs.path(filename)
            with open(img_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")
            content.append({
                "type": "image_url", 
                "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
            })

        response = nutrition_agent.invoke(
            {"messages": [HumanMessage(content=content)]}, 
            config=config
        )
        
        if response and "messages" in response:
            last_msg = response["messages"][-1]
            last_content = last_msg.content
            
            if "Calories" in last_content or "calories" in last_content:
                structured_llm = llm.with_structured_output(NutritionAnalysis)
                result = structured_llm.invoke(last_content)
            else:
                result = {
                    "meal_name": "Search/Info Result",
                    "calories": "N/A",
                    "macros": "Check summary below",
                    "summary": last_content
                }

    return render(request, "chef_app/nutrition.html", {"result": result})
