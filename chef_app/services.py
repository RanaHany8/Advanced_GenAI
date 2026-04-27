import os
import base64
from dotenv import load_dotenv
from typing import List
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver


# from langchain_community.chat_models import ChatOllama
load_dotenv()
print("Environment Loaded! ")

# schema
class Ingredient(BaseModel):
    name: str = Field(description="The name of the food ingredient")
    status: str = Field(description="Ingredient status: 'available' or 'not available'")

class Meal(BaseModel):
    meal_name: str = Field(description="The name of the suggested meal")
    cooking_time: str = Field(description="Approximate preparation and cooking time")
    number_of_individuals: int = Field(description="Number of people the meal serves")
    instructions: List[str] = Field(description="Detailed step-by-step cooking instructions")
    ingredients: List[Ingredient] = Field(description="List of required ingredients and their availability")

class ChefResponse(BaseModel):
    meals: List[Meal] = Field(description="A list containing one or more suggested meals")

print("Schema Defined Successfully!")


llm = init_chat_model(model="gpt-4o-mini", temperature=0.7)

chef_llm = llm.with_structured_output(ChefResponse)
memory = InMemorySaver()

system_prompt = """You are a professional AI Chef . 
- You speak like a real chef (enthusiastic and helpful).
- Suggest meals based on available ingredients provided by the user.
- For each meal, list all ingredients needed and mark them as 'available' or 'not available' based on the user's input or the photo.
- NEVER skip any cooking steps. Provide very detailed instructions."""

print("Chef is ready to take orders!")


def get_chef_suggestions(user_input=None, image_path=None, thread_id="1"):
    config = {"configurable": {"thread_id": thread_id}}

    if image_path:
        if not os.path.exists(image_path):
            return "Error: Image file not found!"
            
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")
        
        msg = HumanMessage(content=[
            {"type": "text", "text": user_input or "What meals can I cook with the ingredients in this photo?"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
        ])
    else:
       
        msg = HumanMessage(content=user_input or "Suggest a creative meal for me.")

    response = chef_llm.invoke([
        SystemMessage(content=system_prompt),
        msg
    ], config=config)
    
    return response


if __name__ == "__main__":
    image_to_test = "fridge.jpeg" 

    if os.path.exists(image_to_test):
        print("\n---  Analyzing Image and Generating Recipes ---")
        result = get_chef_suggestions(image_path=image_to_test)
    else:
        print("\n---  Generating Recipes from Text Input ---")
        result = get_chef_suggestions(user_input="I have chicken, cream, and mushrooms.")

    print("\n" + "="*50)
    print("CHEF SUGGESTIONS")
    print("="*50)

    for meal in result.meals:
        print(f"\n Meal: {meal.meal_name}")
        print(f" Time: {meal.cooking_time} |  Serves: {meal.number_of_individuals} persons")
        print("\n Ingredients Checklist:")
        for ing in meal.ingredients:
            status_icon = "available" if ing.status.lower() == "available" else "not available"
            print(f"   {status_icon} {ing.name:<20} | Status: {ing.status}")
        
        print("\n Cooking Instructions:")
        for i, step in enumerate(meal.instructions, 1):
            print(f"   {i}. {step}")
        print("\n" + "-" * 50) 
        
        
        
        
        #LAB2 
import csv
import base64
import os  
from dotenv import load_dotenv 
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from tavily import TavilyClient
from pydantic import BaseModel, Field

load_dotenv() 

class NutritionAnalysis(BaseModel):
    meal_name: str = Field(description="Name of the food")
    calories: int = Field(description="Estimated calories")
    macros: str = Field(description="Protein, Carbs, and Fats summary")
    summary: str = Field(description="Brief nutritional summary")

@tool
def search_nutrition_info(query: str) -> str:
    """Search for healthy restaurants, grocery stores, or detailed nutrition info."""
    api_key = os.getenv("TAVILY_API_KEY") 
    client = TavilyClient(api_key=api_key)
    return str(client.search(query))

@tool
def store_nutrition_csv(meal_name: str, calories: int, summary: str):
    """Store meal data into a CSV file for tracking."""
    file_path = 'nutrition_log.csv'
    with open(file_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([meal_name, calories, summary])
    return f"Successfully saved {meal_name} to nutrition_log.csv"

llm = ChatOpenAI(model="gpt-4o-mini")
memory = InMemorySaver()
tools = [search_nutrition_info, store_nutrition_csv]

nutrition_agent = create_react_agent(
    model=llm,
    tools=tools,
    checkpointer=memory,
    prompt="""You are a strict Nutrition Assistant. 
    STRATEGY:
    1. For ANY question about restaurants, locations, or menus, you MUST call 'search_nutrition_info' tool. DO NOT answer from your memory.
    2. For ANY request to save or log data, you MUST call 'store_nutrition_csv'.
    3. Always include the medical disclaimer: 'This is not medical or dietary advice.'"""
)