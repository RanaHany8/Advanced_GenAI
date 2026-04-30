from django.shortcuts import render
from django.http import JsonResponse
from .agent import agent 
from langchain.messages import HumanMessage

def chat_home(request):
    return render(request, "chat.html")

def ask_agent(request):
    query = request.GET.get("q")
    if not query:
        return JsonResponse({"error": "No query provided"})

    config = {"configurable": {"thread_id": "1"}} 
    
    try:
        result = agent.invoke(
            {"messages": [("user", query)]}, 
            config=config 
        )
        answer = result["messages"][-1].content
        return JsonResponse({"query": query, "answer": answer})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)