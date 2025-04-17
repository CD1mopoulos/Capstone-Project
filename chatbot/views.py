import numpy as np
import re,os, json,random
from textblob import Word
from sklearn.naive_bayes import MultinomialNB
from rapidfuzz import fuzz, process
from sklearn.feature_extraction.text import CountVectorizer
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from platform_db.models import Dish, Restaurant
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.conf import settings

# Get the absolute path to the intents.json file located in static/json/
intents_path = os.path.join(settings.BASE_DIR, 'static', 'json', 'intents.json')

# Load intents
with open(intents_path, 'r', encoding='utf-8') as file:
    intents = json.load(file)

# Process and clean the text using TextBlob
def clean_text(text):
    tokens = text.lower().split()
    lemmatized_tokens = [Word(token).lemmatize() for token in tokens]
    return " ".join(lemmatized_tokens)

# Prepare data for training the model
texts = []
labels = []

for intent in intents['intents']:
    for pattern in intent['patterns']:
        texts.append(clean_text(pattern))
        labels.append(intent['tag'])

# Use CountVectorizer to convert text into a bag of words
vectorizer = CountVectorizer()
X_train = vectorizer.fit_transform(texts)
y_train = np.array(labels)

# Train a Naive Bayes classifier
model = MultinomialNB()
model.fit(X_train, y_train)

# Extended nickname/typo mapping
nickname_map = {
    "canton": "CANTON Chinese Restaurant",
    "kanthon": "CANTON Chinese Restaurant",
    "kanton": "CANTON Chinese Restaurant",
    "taiyo": "Taiyo Sushi & Noodles",
    "tayio": "Taiyo Sushi & Noodles",
    "tayo": "Taiyo Sushi & Noodles",
    "taio": "Taiyo Sushi & Noodles",
    "napoli": "Pizzeria Napoli",
    "pizza nap": "Pizzeria Napoli",
    "napoly": "Pizzeria Napoli",
    "roma": "Trattoria Roma",
    "tratoria": "Trattoria Roma",
    "trattoria": "Trattoria Roma",
    "juan": "Juan's Cantina",
    "cantina": "Juan's Cantina",
    "juans": "Juan's Cantina",
    "toscana": "Osteria Toscana",
    "osteria": "Osteria Toscana",
    "epirus": "Epirus Tavern",
    "epiros": "Epirus Tavern",
    "gyro": "The Gyro House",
    "gyros": "The Gyro House",
    "gyrohouse": "The Gyro House",
    "kitchen": "The Home Kitchen",
    "home kitchen": "The Home Kitchen",
    "homekitchen": "The Home Kitchen",
    "hong kong": "Hong Kong Athens",
    "hongkong": "Hong Kong Athens",
    "hong kong athens": "Hong Kong Athens",
    "taco loco": "Taco Loco Athens",
    "tacoloco": "Taco Loco Athens",
    "amigos": "Amigos",
    "friends": "Amigos"
}

def get_response(text, lang="en"):
    text_cleaned = clean_text(text)
    bow = vectorizer.transform([text_cleaned])
    probabilities = model.predict_proba(bow)[0]
    confidence = max(probabilities)
    predicted_tag = model.classes_[np.argmax(probabilities)]

    lower_text = text.lower()

    # ✅ Manual override for food recommendation requests
    if re.search(r"(recommend( me)?( something| a dish| food)?|suggest( me)?( something)?|what( should| can).*eat|give me.*recommendation|your fav|top pick|what's tasty|what's good)", lower_text):
        return get_food_recommendation()

    # 🔍 Manual override for common greetings
    if any(word in lower_text for word in ["hi", "hello", "hey", "yo", "sup", "hola", "hl", "hii", "helo", "hlo"]):
        responses = next((i["responses"] for i in intents["intents"] if i["tag"] == "greeting"), [])
        return np.random.choice(responses) if responses else "Hello there!"

    # 🔍 Manual override for restaurant mentions
    for nick, full_name in nickname_map.items():
        if nick in lower_text:
            return get_dishes_by_restaurant(text)

    # ✅ High-confidence intent handling
    if confidence >= 0.25:
        if predicted_tag == "menu_all":
            return get_all_dishes_response()
        elif predicted_tag == "menu_by_restaurant":
            return get_dishes_by_restaurant(text)
        elif predicted_tag == "dish_price":
            return get_dish_price(text)
        elif predicted_tag == "food_recommendation":
            return get_food_recommendation()
        elif predicted_tag == "dish_description":
            desc = get_dish_description(text)
            return desc if desc else "I couldn't find a description for that dish."
        elif predicted_tag == "list_restaurants":
            return list_restaurants_response()
        elif predicted_tag in ["bot_intro", "confused_filler"]:
            responses = next((i["responses"] for i in intents["intents"] if i["tag"] == predicted_tag), [])
            return np.random.choice(responses) if responses else ""

        # 🔁 Default static match
        for intent in intents["intents"]:
            if intent["tag"] == predicted_tag:
                return np.random.choice(intent["responses"])

    # 🔍 Low-confidence fallback: check for possible dish description
    manual_desc = get_dish_description(text)
    if manual_desc:
        return manual_desc

    # ❌ Fallback if nothing else matches
    fallback_responses = next((i["responses"] for i in intents["intents"] if i["tag"] == "fallback"), [])
    return np.random.choice(fallback_responses) if fallback_responses else "I'm not sure I understood that. Could you rephrase?"


@csrf_exempt
def chatbot_response(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")
        language = data.get("lang", "en")
        response = get_response(user_message, lang=language)
        return JsonResponse({"response": response})

def chatbot_widget(request):
    return render(request, "chatbot/chatbot.html")

def get_all_dishes_response():
    restaurants = Restaurant.objects.prefetch_related('dishes').all()
    if not restaurants:
        return "No restaurants found."

    response = "🍽️ Here's everything we offer:\n\n"

    for rest in restaurants:
        dishes = rest.dishes.all()
        if dishes:
            response += f"🔸 {rest.name}\n"
            for dish in dishes:
                desc = dish.description or "No description"
                response += (
                    f"   • {dish.dish_name}\n"
                    f"     📖 {desc}\n"
                    f"     💰 {dish.price:.2f}€\n"
                )
            response += "\n"  # add space between restaurants

    return response.strip()


def get_dishes_by_restaurant(text):
    all_restaurants = Restaurant.objects.all()
    name_map = {r.name: r for r in all_restaurants}
    restaurant_names = list(name_map.keys())

    restaurant_names_normalized = [re.sub(r"[^a-zA-Z0-9\s]", "", name.lower()) for name in restaurant_names]
    name_map_normalized = {re.sub(r"[^a-zA-Z0-9\s]", "", name.lower()): name_map[name] for name in name_map}

    cleaned_input = re.sub(r"[^a-zA-Z0-9\s]", "", text.lower())

    for nick, full_name in nickname_map.items():
        if nick in cleaned_input:
            restaurant = name_map.get(full_name)
            if restaurant:
                dishes = restaurant.dishes.all()
                if not dishes:
                    return "No dishes found for this restaurant."
                response = f"<strong>📍 {escape(restaurant.name)}</strong> offers:<br>"
                for dish in dishes:
                    response += f"- {escape(dish.dish_name)} ({escape(dish.description or 'No description')}): {dish.price:.2f}€<br>"
                return mark_safe(response.strip())

    match = process.extractOne(cleaned_input, restaurant_names_normalized, scorer=fuzz.token_sort_ratio)

    if match and match[1] > 60:
        restaurant = name_map_normalized[match[0]]
        dishes = restaurant.dishes.all()
        if not dishes:
            return "No dishes found for this restaurant."

        response = f"<strong>📍 {escape(restaurant.name)}</strong> offers:<br>"
        for dish in dishes:
            response += f"- {escape(dish.dish_name)} ({escape(dish.description or 'No description')}): {dish.price:.2f}€<br>"
        return mark_safe(response.strip())
    else:
        return "Restaurant not found."


def get_dish_price(user_input):
    all_dishes = Dish.objects.all()
    best_match = None
    highest_score = 0

    for dish in all_dishes:
        score = fuzz.token_sort_ratio(dish.dish_name.lower(), user_input.lower())
        if score > highest_score:
            highest_score = score
            best_match = dish

    if best_match and highest_score >= 60:
        rest_names = ", ".join([r.name for r in best_match.restaurants.all()])
        return f"💶 {best_match.dish_name} is served at {rest_names} and costs {best_match.price}€."

    return "Dish not found."

def get_dish_description(user_input):
    all_dishes = Dish.objects.all()
    best_match = None
    highest_score = 0

    for dish in all_dishes:
        score = fuzz.token_set_ratio(dish.dish_name.lower(), user_input.lower())
        if score > highest_score:
            highest_score = score
            best_match = dish

    if best_match and highest_score >= 60:
        description = best_match.description or "No description available."
        return f"📝 {best_match.dish_name}: {description}"

    return None

def list_restaurants_response():
    restaurants = Restaurant.objects.all()
    if not restaurants:
        return "⚠️ No restaurants found."

    response = "🏢 Here are the restaurants on our platform:<br><br>"
    for r in restaurants:
        response += f"🔹 {escape(r.name)}<br>"

    return mark_safe(response.strip())

def get_food_recommendation():
    dishes = Dish.objects.prefetch_related("restaurants").all()
    if not dishes:
        return "Sorry, I don't have any dishes to recommend at the moment."

    recommended = random.choice(dishes)
    desc = recommended.description or "No description available"
    restaurants = recommended.restaurants.all()
    rest_names = ", ".join([r.name for r in restaurants]) if restaurants else "an unknown restaurant"

    return (
        f"🍽️ Here's something you might like:\n\n"
        f"   • {recommended.dish_name}\n"
        f"     📖 {desc}\n"
        f"     💰 {recommended.price:.2f}€\n"
        f"     🏢 Available at: {rest_names}"
    )

