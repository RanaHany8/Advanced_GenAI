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
# llm = ChatOllama(model="llama3", format="json", temperature=0.7)

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