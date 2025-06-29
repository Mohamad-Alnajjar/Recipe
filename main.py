from random import randrange
from fastapi import FastAPI, Request, Response, status, HTTPException, Depends
from fastapi import Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import psycopg2

# Initialize FastAPI app
app = FastAPI()


#Classes for data validation using Pydantic
class Recipe(BaseModel):
    title: str
    making_time: str
    serves: str
    ingredients: str
    cost: int
    
 
# Database connection setup
try:
    conn = psycopg2.connect(
        host="localhost",
        database="fastapi",
        user="postgres",
        password="postgres24Feb2000",
        # cursor_factory=psycopg2.extras.RealDictCursor
    )
    cursor = conn.cursor()
    print("Database connection successful")
except Exception as e:
    print("Database connection failed, error:", e)
    


@app.post("/recipes")
def create_recipe(new_recipe: Recipe):
    if new_recipe.title or new_recipe.making_time or new_recipe.serves or new_recipe.ingredients or new_recipe.cost not in new_recipe:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Recipe creation failed!",
                        "required": "title, making_time, serves, ingredients, cost"}) 
    
    cursor.execute(
        "INSERT INTO recipes (title, making_time, serves, ingredients, cost) VALUES (%s, %s, %s, %s, %s) RETURNING *",
        (new_recipe.title, new_recipe.making_time, new_recipe.serves, new_recipe.ingredients, new_recipe.cost)
    )

    new_recipe_data = cursor.fetchone()

    conn.commit()
    return [{
        "message": "Recipe successfully created!",
        "recipe": {"id": new_recipe_data[0], "title": new_recipe_data[1], "making_time": new_recipe_data[2], "serves": new_recipe_data[3],
                    "ingredients": new_recipe_data[4], "cost": new_recipe_data[5], "created_at": new_recipe_data[6], "updated_at": new_recipe_data[7]}
    }]



@app.get("/recipes")
def get_all_recipes():
    cursor.execute("SELECT * FROM recipes ")
    recipe = cursor.fetchall()
    return recipe



@app.get("/recipes/{id}")
def get_one_recipe(id: int):
    cursor.execute("SELECT * FROM recipes WHERE id = %s ", (id,))
    recipe = cursor.fetchone()
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"recipe with id {id} not found")
    
    return {
            "message": "Recipe details by id",
            "recipe": [{"title": recipe[1], "making_time": recipe[2], "serves": recipe[3],
                        "ingredients": recipe[4], "cost": recipe[5]}]
        }



@app.patch("/recipes/{id}")
def update_recipe(id: int, updated_recipe: Recipe):
    cursor.execute(
        "UPDATE recipes SET title = %s, making_time = %s, serves = %s, ingredients = %s, cost = %s WHERE id = %s RETURNING *",
        (updated_recipe.title, updated_recipe.making_time, updated_recipe.serves, updated_recipe.ingredients, updated_recipe.cost, id)
    )
    updated_recipe_data = cursor.fetchone()
    conn.commit()
    
    if not updated_recipe_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"recipe with id {id} not found")
    
    return {
            "message": "Recipe successfully updated!",
            "recipe": [{"title": updated_recipe_data[1], "making_time": updated_recipe_data[2], "serves": updated_recipe_data[3],
                        "ingredients": updated_recipe_data[4], "cost": updated_recipe_data[5]}]
        }



@app.delete("/recipes/{id}")
def delete_recipe(id: int):
    cursor.execute("DELETE FROM recipes WHERE id = %s RETURNING *", (id,))
    deleted_recipe = cursor.fetchone()
    conn.commit()
    
    if not deleted_recipe:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "No recipe found"}
        )
    return {"message": "Recipe successfully removed!"}






