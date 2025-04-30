import requests
import json
import os
import difflib
from colorthief import ColorThief
from PIL import Image
import random

API_URL = "https://www.thecocktaildb.com/api/json/v1/1/list.php?i=list"
CHAMPION_DATA_URL = "https://ddragon.leagueoflegends.com/cdn/14.6.1/data/en_US/champion.json"
IMG_BASE_URL = "https://ddragon.leagueoflegends.com/cdn/14.6.1/img/champion/"
IMAGE_DIR = "./images"
os.makedirs(IMAGE_DIR, exist_ok=True)

action_templates = [
    "Add {quantity} {unit} of {ingredient} to a shaker and let it rest briefly.",
    "Pour {quantity} {unit} of {ingredient} into a chilled glass for an elegant start.",
    "Shake {quantity} {unit} of {ingredient} vigorously with ice until well mixed.",
    "Mix {quantity} {unit} of {ingredient} slowly to preserve its delicate aroma.",
    "Top off with {quantity} {unit} of {ingredient} to enhance the final flavor.",
    "Gently fold {quantity} {unit} of {ingredient} into the mixture until fully blended.",
    "Garnish with {quantity} {unit} of {ingredient} for a visually appealing finish.",
    "Stir {quantity} {unit} of {ingredient} with a bar spoon in a circular motion.",
    "Layer {quantity} {unit} of {ingredient} using the back of a spoon for a dramatic effect.",
    "Muddle {quantity} {unit} of {ingredient} at the bottom of the glass to release its essence.",
    "Strain {quantity} {unit} of {ingredient} into the glass for a smooth texture.",
    "Float {quantity} {unit} of {ingredient} on top for a layered presentation.",
    "Combine {quantity} {unit} of {ingredient} with crushed ice for an instant chill.",
    "Blend {quantity} {unit} of {ingredient} until smooth and creamy.",
    "Rim the glass with {ingredient} for a flavorful first sip.",
    "Infuse {quantity} {unit} of {ingredient} into the base for a deep, complex taste.",
    "Sprinkle {quantity} {unit} of {ingredient} lightly for a touch of flair.",
    "Drizzle {quantity} {unit} of {ingredient} delicately across the surface.",
    "Warm {quantity} {unit} of {ingredient} gently to unlock hidden aromas.",
    "Chill {quantity} {unit} of {ingredient} beforehand for maximum freshness.",
    "Serve {quantity} {unit} of {ingredient} on the side for optional customization.",
    "Squeeze {quantity} {unit} of {ingredient} for a burst of freshness.",
    "Smoke {quantity} {unit} of {ingredient} briefly for a rich, complex note.",
    "Flambé {quantity} {unit} of {ingredient} to impress your guests.",
    "Drop {quantity} {unit} of {ingredient} into the center for a dramatic reveal.",
    "Grate {quantity} {unit} of {ingredient} on top for a final touch.",
    "Use {quantity} {unit} of {ingredient} as a striking decorative element.",
    "Shake {quantity} {unit} of {ingredient} vigorously for {time} seconds.",
    "Stir {quantity} {unit} of {ingredient} with precision for {time} seconds.",
    "Let {quantity} {unit} of {ingredient} infuse for {time} seconds.",
    "Muddle {quantity} {unit} of {ingredient} intensely for {time} seconds.",
    "Cool {quantity} {unit} of {ingredient} in the freezer for about {time} seconds.",
    "Whisk {quantity} {unit} of {ingredient} briskly for {time} seconds.",
    "Pour {quantity} {unit} of {ingredient} slowly over {time} seconds for dramatic effect.",
    "Let {quantity} {unit} of {ingredient} settle at the bottom for {time} seconds.",
    "Gently incorporate {quantity} {unit} of {ingredient} over {time} seconds.",
    "Rim the glass with {ingredient}, taking {time} seconds for perfection.",
    "Sprinkle {quantity} {unit} of {ingredient} carefully, spending {time} seconds for balance.",
    "Infuse the drink with {quantity} {unit} of {ingredient} aroma for {time} seconds.",
    "Blend {quantity} {unit} of {ingredient} with ice until smooth – roughly {time} seconds.",
    "Let {quantity} {unit} of {ingredient} breathe for {time} seconds before mixing.",
    "Add {quantity} {unit} of {ingredient} and count to {time} as you stir.",
    "Caramelize {quantity} {unit} of {ingredient} for {time} seconds before incorporating.",
    "Sear {quantity} {unit} of {ingredient} lightly for {time} seconds to deepen the flavor.",
    "Watch {quantity} {unit} of {ingredient} dissolve slowly over {time} seconds.",
    "Let {quantity} {unit} of {ingredient} dance in the glass for {time} seconds before serving.",
    "Layer {quantity} {unit} of {ingredient} carefully, taking about {time} seconds per layer."
]

final_steps = [
    "Serve chilled and enjoy immediately.",
    "Admire your creation for {time} seconds before sipping.",
    "Cheers! Take a moment to savor your masterpiece.",
    "Enjoy your drink with good company.",
    "Toast to the moment and enjoy!",
    "Relax and let the flavors speak for themselves.",
    "Pair with your favorite music and unwind.",
    "Serve with a smile and enjoy the result of your craft.",
    "Let the aroma fill the room for {time} seconds before tasting."
]

def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)

def color_distance(c1, c2):
    return sum(abs(a - b) for a, b in zip(c1, c2))

def is_background_color(color, tolerance=30):
    backgrounds = [(0, 0, 0), (255, 255, 255), (245, 245, 245), (10, 10, 10)]
    return any(color_distance(color, bg) < tolerance for bg in backgrounds)

def extract_significant_colors(image_path, top_n=3):
    img = Image.open(image_path).convert("RGB")
    pixels = img.getcolors(maxcolors=100000)
    if not pixels:
        return [(100, 100, 100)]
    filtered_colors = [(count, col) for count, col in pixels if not is_background_color(col)]
    if not filtered_colors:
        filtered_colors = pixels
    max_count = max(count for count, _ in filtered_colors)
    scored = [(max_count - count, col) for count, col in filtered_colors]
    scored.sort(reverse=True)
    significant_colors = [col for _, col in scored[:top_n]]
    return significant_colors

def color_similarity(hex1, hex2):
    r1, g1, b1 = [int(hex1[i:i+2], 16) for i in (1, 3, 5)]
    r2, g2, b2 = [int(hex2[i:i+2], 16) for i in (1, 3, 5)]
    return abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)

def string_similarity(str1, str2):
    return len(set(str1.lower().split()) & set(str2.lower().split()))

def generate_complex_random_name(champion_name, ingredients_list):
    if ingredients_list:
        ingredient = random.choice(ingredients_list)
    else:
        ingredient = random.choice(ingredient_data)["ingredient"]
        ingredients_list.append(ingredient)
    name_parts = [
        champion_name[:5],
        ingredient[:5]
    ]
    separators = [" ", "'", " with ", "-", "_"]
    separator = random.choice(separators) if random.random() < 0.7 else ""
    suffixes = [" infused", " blend", " mix", " fusion", " twist"]
    suffix = random.choice(suffixes) if random.random() < 0.4 else ""
    name = f"{name_parts[0]}{separator}{name_parts[1]}{suffix}".strip()
    replacements = {'a': '@', 'e': '3', 'i': '1', 'o': '0', 's': '$'}
    unique_name = ''.join(c if random.random() > 0.1 else replacements.get(c, c) for c in name)
    return unique_name, ingredient

def find_similar_ingredients(champion_name, ingredients, threshold=0.6):
    matches = []
    for item in ingredients:
        ing_name = item["ingredient"]
        ratio = difflib.SequenceMatcher(None, champion_name.lower(), ing_name.lower()).ratio()
        if ratio >= threshold or ing_name.lower() in champion_name.lower():
            matches.append(item)
    return matches

def generate_complex_random_name(champion_name, ingredients_list):
    matching_ingredients = find_similar_ingredients(champion_name, ingredient_data, threshold=0.5)
    if matching_ingredients:
        ingredient = random.choice(matching_ingredients)
    else:
        ingredient = random.choice(ingredient_data)
    if ingredient["ingredient"] not in ingredients_list:
        ingredients_list.append(ingredient["ingredient"])
    name_parts = [
        champion_name[:5],
        ingredient["ingredient"][:5]
    ]
    separators = [" ", "'", " with ", "-", "_"]
    separator = random.choice(separators) if random.random() < 0.7 else ""
    suffixes = [" infused", " blend", " mix", " fusion", " twist"]
    suffix = random.choice(suffixes) if random.random() < 0.4 else ""
    name = f"{name_parts[0]}{separator}{name_parts[1]}{suffix}".strip()
    replacements = {'a': '@', 'e': '3', 'i': '1', 'o': '0', 's': '$'}
    unique_name = ''.join(c if random.random() > 0.1 else replacements.get(c.lower(), c) for c in name)
    return unique_name, ingredient["ingredient"]

print("Fetching ingredients...")
resp = requests.get(API_URL)
ingredient_data = []
if resp.ok:
    data = resp.json()
    for ing in data.get("drinks", []):
        name = ing["strIngredient1"]
        colors = {
            "vodka": ["#D1D1D1"],
            "rum": ["#C98A4A"],
            "gin": ["#B8D1D1"],
            "lime": ["#A8E04E"],
            "lemon": ["#F5E200"]
        }.get(name.lower(), ["#FF5733", "#F1E1B3"])
        ingredient_data.append({"ingredient": name, "colors": colors})
else:
    print("Failed to get ingredients.")
    exit()

print("Fetching champion data...")
resp = requests.get(CHAMPION_DATA_URL)
if not resp.ok:
    print("Error fetching champions.")
    exit()

champions = resp.json()["data"]
champion_colors = {}
final_character_data = []

print("Processing champion images...")
for champ_name, champ_info in champions.items():
    filename = champ_info['image']['full']
    img_url = f"{IMG_BASE_URL}{filename}"
    img_path = os.path.join(IMAGE_DIR, filename)
    if not os.path.exists(img_path):
        r = requests.get(img_url)
        if r.ok:
            with open(img_path, "wb") as f:
                f.write(r.content)
    try:
        colors = extract_significant_colors(img_path, top_n=5)
        hex_colors = [rgb_to_hex(c) for c in colors]
        dominant = rgb_to_hex(colors[0])
        champion_colors[champ_name] = dominant
        final_character_data.append({
            "Name": champ_name,
            "Image": img_url,
            "Palette": hex_colors,
            "Mixed": dominant,
            "Ingredients": [],
            "Cocktail Name": ""
        })
        print(f"{champ_name} => {hex_colors}")
    except Exception as e:
        print(f"{champ_name}: {e}")

def match_ingredient_to_champion(ingredient, champion_colors):
    matched = set()
    for champ, color in champion_colors.items():
        for ref in ingredient["colors"]:
            if color_similarity(color, ref) <= 100:
                matched.add(champ)
    return list(matched)

final_cocktail_data = []
for ing in ingredient_data:
    matches = match_ingredient_to_champion(ing, champion_colors)
    final_cocktail_data.append({
        "Ingredient": ing["ingredient"],
        "Colors": ing["colors"],
        "Champions": matches
    })

for champ in final_character_data:
    similar_ings = find_similar_ingredients(champ["Name"], ingredient_data)
    base_ings = random.sample(ingredient_data, random.randint(2, 5))
    selected = list({i["ingredient"] for i in (similar_ings + base_ings)})
    champ["Ingredients"] = selected
    name, ingr = generate_complex_random_name(champ["Name"], champ["Ingredients"])
    if ingr not in champ["Ingredients"]:
        champ["Ingredients"].append(ingr)
    champ["Cocktail Name"] = name

def generate_preparation_steps(ingredients):
    steps = []
    random.shuffle(ingredients)
    used_templates = set()
    for ing in ingredients:
        available_templates = [t for t in action_templates if t not in used_templates]
        if not available_templates:
            used_templates.clear()
            available_templates = action_templates
        template = random.choice(available_templates)
        used_templates.add(template)
        quantity = round(random.uniform(0.2, 5.0), 1)
        unit = random.choice(["ml", "cl", "oz"])
        if "{time}" in template:
            time = random.randint(5, 30)
            step = template.format(ingredient=ing, time=time, quantity=quantity, unit=unit)
        else:
            step = template.format(ingredient=ing, quantity=quantity, unit=unit)
        steps.append(step)
    final = random.choice(final_steps)
    if "{time}" in final:
        steps.append(final.format(time=random.randint(5, 15)))
    else:
        steps.append(final)
    return steps

for champ in final_character_data:
    random.shuffle(champ["Ingredients"])
    champ["Preparation"] = generate_preparation_steps(champ["Ingredients"])

print("Saving JSON data...")
with open("character.json", "w", encoding="utf-8") as f:
    json.dump(final_character_data, f, indent=4, ensure_ascii=False)

with open("cocktail.json", "w", encoding="utf-8") as f:
    json.dump(final_cocktail_data, f, indent=4, ensure_ascii=False)

print("Done. Files saved: character.json & cocktail.json")
