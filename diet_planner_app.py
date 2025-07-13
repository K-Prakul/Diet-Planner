import streamlit as st
from datetime import date, timedelta
import requests

API_KEY = "2ef862a8e7eb4d0ab6fc5b250f3193d1"

def calculate_bmr(gender: str, weight: float, height: float, age: int) -> float:
    """Return Basal Metabolic Rate (Mifflin‑St Jeor)."""
    if gender == "Male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    return 10 * weight + 6.25 * height - 5 * age - 161

import requests
import streamlit as st  

def fetch_recipe(meal_type: str, diet: str, allergies: list[str]) -> str:
    def _query(diet_val, allergy_val):
        url = "https://api.spoonacular.com/recipes/complexSearch"
        params = {
            "apiKey": API_KEY,
            "number": 1,
            "type": meal_type,
            "diet": diet_val.lower() if diet_val and diet_val != "Non‑Vegetarian" else None,
            "intolerances": ",".join(allergy_val).lower() if allergy_val else None,
            "addRecipeInformation": True,
            "sort": "random",
        }
        try:
            res = requests.get(url, params=params, timeout=10)
            if res.status_code != 200:
                st.error(f"Spoonacular API error {res.status_code}: {res.text[:120]}")
                return []                       # treat as “no result”
            return res.json().get("results", [])
        except requests.exceptions.JSONDecodeError:
            st.error("Spoonacular response was not JSON. Check API key or daily quota.")
            return []
        except requests.exceptions.RequestException as e:
            st.error(f"Network error contacting Spoonacular: {e}")
            return []


    results = _query(diet, allergies)

    if not results:
        results = _query(diet, [])
 
    if not results:
        results = _query(None, [])

    if results:
        recipe = results[0]
        return f"{recipe['title']} — [View Recipe]({recipe['sourceUrl']})"

    return "⚠️ No suitable recipe found after retries."


def generate_weekly_meal_plan(diet: str, allergies: list[str]) -> dict:
    weekly = {}
    for i in range(7):
        day_name = (date.today() + timedelta(days=i)).strftime("%A")
        daily_plan = {
            "Breakfast": fetch_recipe("breakfast", diet, allergies),
            "Lunch": fetch_recipe("lunch", diet, allergies),
            "Dinner": fetch_recipe("dinner", diet, allergies),
        }
        weekly[day_name] = daily_plan
    return weekly

st.title("🥗 Personalized Diet Planner (7‑Day)")
st.write("Generate a **weekly** meal plan based on your health profile and allergies.")
st.sidebar.header("Enter Your Details")
age = st.sidebar.number_input("Age", min_value=10, max_value=100, value=25)
gender = st.sidebar.selectbox("Gender", ["Male", "Female"])
weight = st.sidebar.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0)
height = st.sidebar.number_input("Height (cm)", min_value=120.0, max_value=220.0, value=175.0)
goal = st.sidebar.selectbox("Goal", ["Lose Weight", "Maintain Weight", "Gain Weight"])
diet_type = st.sidebar.selectbox(
    "Diet Preference", ["Vegetarian", "Vegan", "Non‑Vegetarian"]
)
allergy_options = ["Nuts", "Dairy", "Gluten", "Soy", "Eggs", "Seafood"]
allergies = st.sidebar.multiselect("Allergies (optional)", allergy_options)

bmr = calculate_bmr(gender, weight, height, age)
_goal_adj = {"Lose Weight": -500, "Maintain Weight": 0, "Gain Weight": 500}
cal_target = bmr + _goal_adj[goal]

st.subheader("🔢 Your Daily Caloric Needs")
st.metric("BMR (Calories/day)", f"{bmr:.0f}")
st.metric("Target Calories (based on goal)", f"{cal_target:.0f}")

st.subheader("📅 7‑Day Meal Plan (Allergy‑Aware)")
weekly_plan = generate_weekly_meal_plan(diet_type, allergies)

for day_name, day_plan in weekly_plan.items():
    with st.expander(day_name):
        for meal, desc in day_plan.items():
            st.write(f"**{meal}**: {desc}")

st.caption(
    f"Plan generated on {date.today()} • Allergies excluded: {', '.join(allergies) if allergies else 'None'}"
)
