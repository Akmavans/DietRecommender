import numpy as np
import re
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer


def scaling(dataframe):
    scaler=StandardScaler()
    prep_data=scaler.fit_transform(dataframe.iloc[:,6:15].to_numpy())
    return prep_data,scaler

def nn_predictor(prep_data):
    neigh = NearestNeighbors(metric='cosine',algorithm='brute')
    neigh.fit(prep_data)
    return neigh

def build_pipeline(neigh,scaler,params):
    transformer = FunctionTransformer(neigh.kneighbors,kw_args=params)
    pipeline=Pipeline([('std_scaler',scaler),('NN',transformer)])
    return pipeline

def extract_data(dataframe,ingredients):
    extracted_data=dataframe.copy()
    extracted_data=extract_ingredient_filtered_data(extracted_data,ingredients)
    return extracted_data
    
def extract_ingredient_filtered_data(dataframe,ingredients):
    extracted_data=dataframe.copy()
    regex_string=''.join(map(lambda x:f'(?=.*{x})',ingredients))
    extracted_data=extracted_data[extracted_data['RecipeIngredientParts'].str.contains(regex_string,regex=True,flags=re.IGNORECASE)]
    return extracted_data

def apply_pipeline(pipeline,_input,extracted_data):
    _input=np.array(_input).reshape(1,-1)
    return extracted_data.iloc[pipeline.transform(_input)[0]]

def recommend(dataframe,_input,ingredients=[],params={'n_neighbors':5,'return_distance':False}):
        extracted_data=extract_data(dataframe,ingredients)
        if extracted_data.shape[0]>=params['n_neighbors']:
            prep_data,scaler=scaling(extracted_data)
            neigh=nn_predictor(prep_data)
            pipeline=build_pipeline(neigh,scaler,params)
            return apply_pipeline(pipeline,_input,extracted_data)
        else:
            return None

def extract_quoted_strings(s):
    # Find all the strings inside double quotes
    strings = re.findall(r'"([^"]*)"', s)
    # Join the strings with 'and'
    return strings

def output_recommended_recipes(dataframe):
    if dataframe is not None:
        output=dataframe.copy()
        output=output.to_dict("records")
        for recipe in output:
            recipe['RecipeIngredientParts']=extract_quoted_strings(recipe['RecipeIngredientParts'])
            recipe['RecipeInstructions']=extract_quoted_strings(recipe['RecipeInstructions'])
    else:
        output=None
    return output

def calculate_nutrition(gender, weight, height, age):
    # Define basal metabolic rate (BMR) equations based on gender
    if gender.lower() == 'male':
        bmr = 10 * int(weight) + 6.25 *int(height) - 5 * int(age) + 5
    elif gender.lower() == 'female':
        bmr = 10 * int(weight) + 6.25 * height - 5 * int(age) - 161
    else:
        return "Invalid gender specified. Please specify 'male' or 'female'."

    # Calculate Total Daily Energy Expenditure (TDEE) using BMR and activity level
    activity_level = 1.55  # Assuming moderate activity level
    tdee = bmr * activity_level

    # Calculate macronutrient requirements based on TDEE
    protein = 0.8 * int(weight)  # Protein requirement: 0.8 grams per kg of body weight
    fat = 0.25 * tdee / 9  # Fat requirement: 25% of total calorie intake, 1 gram of fat = 9 calories
    carbohydrates = (tdee - (protein * 4) - (fat * 9)) / 4  # Carbohydrate requirement: remaining calories from TDEE

    # Calculate additional nutritional contents
    saturated_fat = 0.1 * tdee / 9  # Saturated Fat Content: 10% of total calorie intake
    cholesterol = 300  # Cholesterol Content: Assuming 300mg per day
    sodium = 2300  # Sodium Content: Assuming 2300mg per day
    fiber = 25  # Fiber Content: Assuming 25 grams per day
    sugar = 0.1 * tdee / 4  # Sugar Content: 10% of total calorie intake

    # Return the calculated nutritional values
    return {
        'total_calories': round(tdee, 2),
        'fat': round(fat, 2),
        'saturated_fat': round(saturated_fat, 2),
        'cholesterol': cholesterol,
        'sodium': sodium,
        'carbohydrates': round(carbohydrates, 2),
        'fiber': fiber,
        'sugar': round(sugar, 2),
        'protein': round(protein, 2)
    }
#nutrition = calculate_nutrition('male', 72, 170, 23)
#values_list = list(nutrition.values())


def calculate_meals_nutrients(total_nutrients):
    # Extracting total daily nutritional requirements
    total_calories = total_nutrients['total_calories']
    total_protein = total_nutrients['protein']
    total_carbohydrates = total_nutrients['carbohydrates']
    total_fat = total_nutrients['fat']
    total_saturated_fat = total_nutrients['saturated_fat']
    total_fiber = total_nutrients['fiber']
    total_sugar = total_nutrients['sugar']

    # Calculate calories for each meal
    breakfast_calories = total_calories * 0.25
    lunch_calories = total_calories * 0.35
    dinner_calories = total_calories * 0.4

    # Calculate nutrient distribution for each meal
    # Breakfast
    breakfast_protein = total_protein * 0.175
    breakfast_carbohydrates = total_carbohydrates * 0.45
    breakfast_fat = total_fat * 0.275
    breakfast_saturated_fat = total_saturated_fat * 0.275
    breakfast_sugar = total_sugar * 0.45

    # Lunch
    lunch_protein = total_protein * 0.225
    lunch_carbohydrates = total_carbohydrates * 0.4
    lunch_fat = total_fat * 0.275
    lunch_saturated_fat = total_saturated_fat * 0.275
    lunch_fiber = total_fiber * 0.4  # Increased fiber content for lunch
    lunch_sugar = total_sugar * 0.4

    # Dinner
    dinner_protein = total_protein * 0.275
    dinner_carbohydrates = total_carbohydrates * 0.25
    dinner_fat = total_fat * 0.325
    dinner_saturated_fat = total_saturated_fat * 0.325
    dinner_sugar = total_sugar * 0.25

    # Calculate other nutrients (cholesterol, sodium)
    # These nutrients will be evenly distributed across meals

    # Cholesterol
    cholesterol_per_meal = total_nutrients['cholesterol'] / 3

    # Sodium
    sodium_per_meal = total_nutrients['sodium'] / 3

    # Create dictionaries to store the nutrient distribution for each meal
    breakfast = {
        'calories': breakfast_calories,
        'fat': breakfast_fat,
        'saturated_fat': breakfast_saturated_fat,
        'cholesterol': cholesterol_per_meal,
        'sodium': sodium_per_meal,
        'carbohydrates': breakfast_carbohydrates,
        'fiber': total_fiber / 3,  # Fiber distributed evenly across all meals
        'sugar': breakfast_sugar,
        'protein': breakfast_protein,
        
        
        
    }

    lunch = {
        'calories': lunch_calories,
        'fat': lunch_fat,
        'saturated_fat': lunch_saturated_fat,
        'cholesterol': cholesterol_per_meal,
        'sodium': sodium_per_meal,
        'carbohydrates': lunch_carbohydrates,
        'fiber': lunch_fiber,
        'sugar': lunch_sugar,
        'protein': lunch_protein,
        
    }

    dinner = {
        'calories': dinner_calories,
        'fat': dinner_fat,
        'saturated_fat': dinner_saturated_fat,
        'cholesterol': cholesterol_per_meal,
        'sodium': sodium_per_meal,
        'carbohydrates': dinner_carbohydrates,
        'fiber': total_fiber / 3,  # Fiber distributed evenly across all meals
        'sugar': dinner_sugar,
        'protein': dinner_protein,
        
    }

    return [round_values(breakfast),round_values(lunch),round_values(dinner)]

def round_values(nutrient_dict):
    rounded_dict = {}
    for key, value in nutrient_dict.items():
        rounded_dict[key] = round(value, 2)
    return rounded_dict
    
#breakfast, lunch, dinner = calculate_meals_nutrients(nutrition)