from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os
import random

app = FastAPI()

# File names
CHARACTER_FILE = "Suits_Characters.csv"
QUOTE_FILE = "quotes.csv"

class CreateCharacters(BaseModel):
    character: str

@app.post("/create_characters")
async def create_character(character_data: CreateCharacters):
    character = character_data.character.strip()

    if os.path.exists(CHARACTER_FILE) and os.path.getsize(CHARACTER_FILE) > 0:
        df = pd.read_csv(CHARACTER_FILE, on_bad_lines='skip')
    else:
        df = pd.DataFrame(columns=["character"])

    if character in df["character"].values:
        raise HTTPException(status_code=400, detail="Character already exists.")

    new_character = pd.DataFrame([{"character": character}])
    df = pd.concat([df, new_character], ignore_index=True)

    df.drop_duplicates(subset=["character"], keep="first", inplace=True)
    df.to_csv(CHARACTER_FILE, index=False, mode='w')

    return {"msg": "Character Created!", "character": character}

@app.get("/characters")
async def get_characters():
    if not os.path.exists(CHARACTER_FILE) or os.path.getsize(CHARACTER_FILE) == 0:
        return {"msg": "No characters found."}

    try:
        df = pd.read_csv(CHARACTER_FILE, on_bad_lines='skip', dtype=str)

        if "character" not in df.columns:
            return {"msg": "Invalid CSV format. Missing 'character' column."}

        # Remove duplicates properly
        character_list = df["character"].str.strip().str.title().drop_duplicates().tolist()
        
        return {"characters": character_list} if character_list else {"msg": "No characters found."}

    except Exception as e:
        return {"msg": f"Error reading CSV: {str(e)}"}


@app.get("/characters/{name}")
async def get_character(name: str):
    if os.path.exists(CHARACTER_FILE) and os.path.getsize(CHARACTER_FILE) > 0:
        df = pd.read_csv(CHARACTER_FILE, on_bad_lines='skip')
        if name in df["character"].values:
            return {"character": name}
        return {"msg": f"Character '{name}' not found."}
    return {"msg": "No characters found."}

@app.get("/quote")
async def get_quote():
    if os.path.exists(QUOTE_FILE) and os.path.getsize(QUOTE_FILE) > 0:
        df = pd.read_csv(QUOTE_FILE, on_bad_lines='skip', encoding="ISO-8859-1")

        df.columns = df.columns.str.strip()
        print(df.head())
        column_name = "quotes" if "quotes" in df.columns else "quote"
        
        if not df.empty and column_name in df.columns:
            quotes_list = df[column_name].dropna().tolist()
            if quotes_list:
                return {"quote": random.choice(quotes_list)}

    return {"msg": "No quotes available."}
