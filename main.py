import requests
import json
import os
from colorthief import ColorThief
import random

API_URL = "https://www.thecocktaildb.com/api/json/v1/1/list.php?i=list"
CHAMPION_DATA_URL = "https://ddragon.leagueoflegends.com/cdn/14.6.1/data/en_US/champion.json"
IMG_BASE_URL = "https://ddragon.leagueoflegends.com/cdn/14.6.1/img/champion/"

IMAGE_DIR = "./images"
os.makedirs(IMAGE_DIR, exist_ok=True)

def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])

def average_color(palette):
    avg_r = sum(rgb[0] for rgb in palette) // len(palette)
    avg_g = sum(rgb[1] for rgb in palette) // len(palette)
    avg_b = sum(rgb[2] for rgb in palette) // len(palette)
    return (avg_r, avg_g, avg_b)

def color_similarity(hex1, hex2):
    r1, g1, b1 = [int(hex1[i:i+2], 16) for i in (1, 3, 5)]
    r2, g2, b2 = [int(hex2[i:i+2], 16) for i in (1, 3, 5)]
    return abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)

def string_similarity(str1, str2):
    return len(set(str1.lower().split()) & set(str2.lower().split()))

def generate_complex_random_name(character_data, ingredient_data):
    random_character = random.choice(character_data)
    random_ingredient = random.choice(ingredient_data)
    
    if string_similarity(random_character['Name'], random_ingredient['ingredient']) > 0:
        name_parts = [
            random_character['Name'],
            random_ingredient['ingredient']
        ]
    else:
        name_parts = [
            random_character['Name'][:5],
            random_ingredient['ingredient'][:5]
        ]
    
    separators = [" ", "'", " with ", "-", "_"]
    separator = random.choice(separators) if random.random() < 0.7 else ""

    suffixes = [" infused", " blend", " mix", " fusion", " twist"]
    suffix = random.choice(suffixes) if random.random() < 0.4 else ""

    name = f"{name_parts[0]}{separator}{name_parts[1]}{suffix}".strip()

    replacements = {'a': '@', 'e': '3', 'i': '1', 'o': '0', 's': '$'}
    unique_name = ''.join(c if random.random() > 0.1 else replacements.get(c, c) for c in name)

    return unique_name

print("Fetching ingredients data...")
response = requests.get(API_URL)
if response.status_code != 200:
    print("Error fetching ingredients.")
    exit()

data = response.json()
if "drinks" not in data:
    print("No ingredient data found in the response.")
    exit()

ingredient_data = []
for ingredient in data["drinks"]:
    ingredient_name = ingredient["strIngredient1"]
    if ingredient_name.lower() in ["vodka", "rum", "gin"]:
        colors = ["#D1D1D1", "#C98A4A", "#B8D1D1"]
    elif ingredient_name.lower() in ["lime", "lemon"]:
        colors = ["#A8E04E", "#F5E200"]
    else:
        colors = ["#FF5733", "#F1E1B3"]

    ingredient_data.append({
        "ingredient": ingredient_name,
        "colors": colors
    })

print(f"Ingredient data: {ingredient_data[:5]}")

print("Fetching champion data...")
response = requests.get(CHAMPION_DATA_URL)
if response.status_code != 200:
    print("Error fetching champions.")
    exit()

champions = response.json()["data"]
champion_colors = {}

print("Processing champions images...")
for champ_name, champ_info in champions.items():
    img_filename = champ_info['image']['full']
    img_url = f"{IMG_BASE_URL}{img_filename}"
    img_path = os.path.join(IMAGE_DIR, img_filename)

    if not os.path.exists(img_path):
        print(f"Downloading image for {champ_name}...")
        img_response = requests.get(img_url)
        if img_response.status_code == 200:
            with open(img_path, "wb") as img_file:
                img_file.write(img_response.content)
        else:
            print(f"Failed to download image for {champ_name}")

    try:
        print(f"Analyzing colors for {champ_name}...")
        color_thief = ColorThief(img_path)
        palette = color_thief.get_palette(color_count=3)
        avg_rgb = average_color(palette)
        avg_hex = rgb_to_hex(avg_rgb)
        champion_colors[champ_name] = avg_hex
        print(f"Color for {champ_name}: {avg_hex}")
    except Exception as e:
        print(f"Error analyzing colors for {champ_name}: {e}")

def match_ingredient_to_champion(ingredient, champions, champion_colors):
    matching_champions = []

    for champ_name in champions.keys():
        name_similarity = string_similarity(ingredient["ingredient"], champ_name)
        if name_similarity > 0:
            matching_champions.append(champ_name)

    for color in ingredient["colors"]:
        for champ_name, champ_color in champion_colors.items():
            color_sim = color_similarity(color, champ_color)
            if color_sim <= 100:
                matching_champions.append(champ_name)

    return list(set(matching_champions))

final_character_data = []
final_cocktail_data = []

print("Matching ingredients with champions...")
for ingredient in ingredient_data:
    ingredient_name = ingredient["ingredient"]
    ingredient_colors = ingredient["colors"]
    
    matching_champions = match_ingredient_to_champion(ingredient, champions, champion_colors)

    ingredient["mixed"] = {
        "ingredient": ingredient_name,
        "champions": matching_champions
    }

    final_cocktail_data.append({
        "Ingredient": ingredient_name,
        "Colors": ingredient_colors
    })

print(f"Final cocktail data: {final_cocktail_data[:5]}")

print("Creating final character data...")
for champ_name in champions.keys():
    random_ingredients = random.sample(ingredient_data, random.randint(3, 10))
    ingredients_for_character = [ing["ingredient"] for ing in random_ingredients]
    cocktail_name = generate_complex_random_name([{"Name": champ_name}], ingredient_data)

    final_character_data.append({
        "Name": champ_name,
        "Image": f"{IMG_BASE_URL}{champions[champ_name]['image']['full']}",
        "Palette": [rgb_to_hex(rgb) for rgb in ColorThief(os.path.join(IMAGE_DIR, champions[champ_name]['image']['full'])).get_palette(color_count=3)],
        "Mixed": champion_colors[champ_name],
        "Ingredients": ingredients_for_character,
        "Cocktail Name": cocktail_name
    })

print(f"Final character data: {final_character_data[:5]}")

print("Writing data to JSON files...")
with open("character.json", "w", encoding="utf-8") as json_file:
    json.dump(final_character_data, json_file, indent=4, ensure_ascii=False)

with open("cocktail.json", "w", encoding="utf-8") as json_file:
    json.dump(final_cocktail_data, json_file, indent=4, ensure_ascii=False)

print("The character.json and cocktail.json files have been successfully created!")
