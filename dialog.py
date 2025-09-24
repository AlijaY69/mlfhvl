import textdistance
import random
import preference_extraction
import suggest_restaurant

def statetransition(currentstate, userinput, ml_dialog, keywords_dict, filename, preferences_memory={"pricerange": None, "area": None, "food": None}, restaurant_info=[], speech):
    vectorizer = ml_dialog[1]
    user_input_vect = vectorizer.transform([userinput])
    dialog_act = ml_dialog[0].predict(user_input_vect)[0]
    confuse = False
    current_pref = ""


    if dialog_act == "inform":
        preferences_memory = preference_extraction.preference_extraction(userinput, keywords_dict, preferences_memory)
    # print(currentstate)
    # print(f"New prefs: {preferences_memory}")
    # print(f"Old prefs: {current_pref}")
   
    # This current diagram is working off of Ali's diagram sent on 18/9 in the groupchat
    if currentstate in (1,2,3,4):
        if preferences_memory['area'] is None:
            nextstate = 2
        elif preferences_memory['food'] is None:
            nextstate = 3
        elif preferences_memory['pricerange'] is None:
            nextstate = 4
        else:
            restaurant_info = suggest_restaurant.suggest_restaurant(filename, preferences_memory)
            if len(restaurant_info) > 0:
                nextstate = 5
            else: nextstate = 6


    elif currentstate == 5:
        if dialog_act in ("ack", "affirm", "thankyou"):
            nextstate = 9
        elif dialog_act in ("deny", "negate"):
            nextstate = 7
## if the preference is changed without answering question, continue         
        elif preferences_memory != current_pref:
            restaurant_info = suggest_restaurant.suggest_restaurant(filename, preferences_memory)
            if len(restaurant_info) > 0:
                nextstate = 5
            else: nextstate = 6
        else:
            confuse = True
            nextstate = currentstate


    elif currentstate in (6,8):
        if "area" in userinput or textdistance.levenshtein.distance("area", userinput) < 4:
            nextstate = 2
        elif "price" in userinput or textdistance.levenshtein.distance("price", userinput) < 4:
            nextstate = 4
        elif "food" in userinput or textdistance.levenshtein.distance("food", userinput) < 4:
            nextstate = 3
## if the preference is changed without answering question, continue
        elif preferences_memory != current_pref:
            restaurant_info = suggest_restaurant.suggest_restaurant(filename, preferences_memory)
            if len(restaurant_info) > 0:
                nextstate = 5
            else: nextstate = 6
        else:
            nextstate = currentstate
            confuse = True
   
    elif currentstate == 7:
        if dialog_act in ("ack", "affirm", "thankyou", "reqmore", "reqalts"):
            if restaurant_info == suggest_restaurant.suggest_restaurant(filename, preferences_memory):
                # Either we randomly sampled the same one twice or there is no new one
                nextstate = 6
            else:
                restaurant_info = suggest_restaurant.suggest_restaurant(filename, preferences_memory)
                nextstate = 5
        elif dialog_act in ("deny", "negate"):
            nextstate = 8
## if the preference is changed without answering question, continue        
        elif preferences_memory != current_pref:
            restaurant_info = suggest_restaurant.suggest_restaurant(filename, preferences_memory)
            if len(restaurant_info) > 0:
                nextstate = 5
            else: nextstate = 6
        else:
            confuse = True
            nextstate = currentstate
   
    if nextstate == 2:
        if speech == "formal":
            print(random.choice(["Which area would you like to find a restaurant in?",
                                 "Could you specify the area you want me to check for restaurants?",
                                 "What area should I search in?"]))
        else:  # informal
            print(random.choice(["Where do you want to eat?",
                                 "What area are you looking at?",
                                 "Which part of town?"]))
    elif nextstate == 4:
        if speech == "formal":
            print(random.choice(["Are you looking for a cheap, moderate or expensive restaurant?",
                                 "Could you specify your budget level: cheap, moderate, or expensive?",
                                 "Please tell me your price range: is it cheap, moderate, or expensive?"]))
        else:  # informal
            print(random.choice(["How much do you want to spend?",
                                 "What's your budget like?",
                                 "Cheap, moderate, or expensive?"]))
    elif nextstate == 3:
        if speech == "formal":
            print(random.choice(["What kind of food are you looking for?",
                                 "What cuisine would you like to have?",
                                 "What types of food do you want me to look for?"]))
        else:  # informal
            print(random.choice(["What do you feel like eating?",
                                 "What kind of food are you in the mood for?",
                                 "What's your craving?"]))
    elif nextstate == 5:
        if confuse:
            if speech == "formal":
                print(random.choice([f"Sorry, I couldn't quite get that. Please confirm or deny the option of {restaurant_info[0]}",
                                     f"I can't quite process that answer. Could you please confirm or deny the {restaurant_info[0]} option?"]))
            else:  # informal
                print(random.choice([f"Sorry, didn't catch that. Yes or no for {restaurant_info[0]}?",
                                     f"Huh? Did you want {restaurant_info[0]} or not?"]))
        else:
            if speech == "formal":
                print(random.choice([f"{restaurant_info[0]} is a great {preferences_memory['food']} place. ",
                                     f"For a {preferences_memory['pricerange']} price, {restaurant_info[0]} is a good place. ",
                                     f"A good restaurant near {preferences_memory['area']} is {restaurant_info[0]}. "])
                    + random.choice(["Is this where you want to go?",
                                     "Does that sound like a good option?",
                                     "Would that be to your liking?"]))
            else:  # informal
                print(random.choice([f"{restaurant_info[0]} is a great {preferences_memory['food']} place. ",
                                     f"For {preferences_memory['pricerange']} prices, {restaurant_info[0]} is pretty good. ",
                                     f"Near {preferences_memory['area']}, {restaurant_info[0]} is solid. "])
                    + random.choice(["Sound good?",
                                     "Want to try it?",
                                     "What do you think?"]))
           
    elif nextstate == 6:
        if confuse:
            if speech == "formal":
                print(random.choice(["Sorry, I didn't understand that. Please mention the preference you want to change.",
                                     "Unfortunately I couldn't understand that. Please mention the preference you wish to change (food, price or area)."]))
            else:  # informal
                print(random.choice(["Sorry, didn't get that. What do you want to change?",
                                     "Huh? Just tell me what to change - food, price, or area."]))
        else:
            if speech == "formal":
                print(random.choice(["Unfortunately no restaurant matches your preferences. Please mention a preference to change.",
                                     "Apologies, a restaurant with those characteristics does not appear in our database, please mention a preference to change."]))
            else:  # informal
                print(random.choice(["Sorry, nothing matches what you want. What should I change?",
                                     "No luck with those preferences. What do you want to switch up?"]))

# Suggest price alternatives to make it easier for user             
            if preferences_memory['pricerange'] == 'cheap':
                preferences_memory['pricerange'] = 'moderate'
                restaurant_info = suggest_restaurant.suggest_restaurant(filename, preferences_memory)
                if len(restaurant_info) > 0:
                    if speech == "formal":
                        print(f"Alternatively, there is a {preferences_memory['pricerange']} priced {preferences_memory['food']} restaurant in the {preferences_memory['area']}, if you'd like. It is called {restaurant_info[0]}. "
                        + random.choice(["Is this where you want to go?",
                                         "Does that sound like a good option?",
                                         "Would that be to your liking?"]))
                    else:  # informal
                        print(f"Or there's a {preferences_memory['pricerange']} {preferences_memory['food']} place in {preferences_memory['area']} called {restaurant_info[0]}. "
                        + random.choice(["Sound good?",
                                         "Want to try it?",
                                         "What do you think?"]))
                    nextstate = 5
                else:
                    preferences_memory['pricerange'] = 'expensive'
                    restaurant_info = suggest_restaurant.suggest_restaurant(filename, preferences_memory)
                    if len(restaurant_info) > 0:
                        if speech == "formal":
                            print(f"Alternatively, there is a {preferences_memory['pricerange']} priced {preferences_memory['food']} restaurant in the {preferences_memory['area']}, if you'd like. It is called {restaurant_info[0]}. "
                            + random.choice(["Is this where you want to go?",
                                             "Does that sound like a good option?",
                                             "Would that be to your liking?"]))
                        else:  # informal
                            print(f"Or there's a {preferences_memory['pricerange']} {preferences_memory['food']} place in {preferences_memory['area']} called {restaurant_info[0]}. "
                            + random.choice(["Sound good?",
                                             "Want to try it?",
                                             "What do you think?"]))
                        nextstate = 5
                    else:
                        preferences_memory['pricerange'] = 'cheap'

            elif preferences_memory['pricerange'] == 'moderate':
                preferences_memory['pricerange'] = 'cheap'
                restaurant_info = suggest_restaurant.suggest_restaurant(filename, preferences_memory)
                if len(restaurant_info) > 0:
                    if speech == "formal":
                        print(f"Alternatively, there is a {preferences_memory['pricerange']} priced {preferences_memory['food']} restaurant in the {preferences_memory['area']}, if you'd like. It is called {restaurant_info[0]}. "
                        + random.choice(["Is this where you want to go?",
                                         "Does that sound like a good option?",
                                         "Would that be to your liking?"]))
                    else:  # informal
                        print(f"Or there's a {preferences_memory['pricerange']} {preferences_memory['food']} place in {preferences_memory['area']} called {restaurant_info[0]}. "
                        + random.choice(["Sound good?",
                                         "Want to try it?",
                                         "What do you think?"]))
                    nextstate = 5
                else:
                    preferences_memory['pricerange'] = 'expensive'
                    restaurant_info = suggest_restaurant.suggest_restaurant(filename, preferences_memory)
                    if len(restaurant_info) > 0:
                        if speech == "formal":
                            print(f"Alternatively, there is a {preferences_memory['pricerange']} priced {preferences_memory['food']} restaurant in the {preferences_memory['area']}, if you'd like. It is called {restaurant_info[0]}. "
                            + random.choice(["Is this where you want to go?",
                                             "Does that sound like a good option?",
                                             "Would that be to your liking?"]))
                        else:  # informal
                            print(f"Or there's a {preferences_memory['pricerange']} {preferences_memory['food']} place in {preferences_memory['area']} called {restaurant_info[0]}. "
                            + random.choice(["Sound good?",
                                             "Want to try it?",
                                             "What do you think?"]))
                        nextstate = 5
                    else:
                        preferences_memory['pricerange'] = 'moderate'
            
            elif preferences_memory['pricerange'] == 'expensive':
                preferences_memory['pricerange'] = 'moderate'
                restaurant_info = suggest_restaurant.suggest_restaurant(filename, preferences_memory)
                if len(restaurant_info) > 0:
                    if speech == "formal":
                        print(f"Alternatively, there is a {preferences_memory['pricerange']} priced {preferences_memory['food']} restaurant in the {preferences_memory['area']}, if you'd like. It is called {restaurant_info[0]}. "
                        + random.choice(["Is this where you want to go?",
                                         "Does that sound like a good option?",
                                         "Would that be to your liking?"]))
                    else:  # informal
                        print(f"Or there's a {preferences_memory['pricerange']} {preferences_memory['food']} place in {preferences_memory['area']} called {restaurant_info[0]}. "
                        + random.choice(["Sound good?",
                                         "Want to try it?",
                                         "What do you think?"]))
                    nextstate = 5
                else:
                    preferences_memory['pricerange'] = 'cheap'
                    restaurant_info = suggest_restaurant.suggest_restaurant(filename, preferences_memory)
                    if len(restaurant_info) > 0:
                        if speech == "formal":
                            print(f"Alternatively, there is a {preferences_memory['pricerange']} priced {preferences_memory['food']} restaurant in the {preferences_memory['area']}, if you'd like. It is called {restaurant_info[0]}. "
                            + random.choice(["Is this where you want to go?",
                                             "Does that sound like a good option?",
                                             "Would that be to your liking?"]))
                        else:  # informal
                            print(f"Or there's a {preferences_memory['pricerange']} {preferences_memory['food']} place in {preferences_memory['area']} called {restaurant_info[0]}. "
                            + random.choice(["Sound good?",
                                             "Want to try it?",
                                             "What do you think?"]))
                        nextstate = 5
                    else:
                        preferences_memory['pricerange'] = 'expensive'

    elif nextstate == 7:
        if confuse:
            if speech == "formal":
                print(random.choice([f"Sorry, I couldn't quite get that. Please confirm or deny if you want a new restaurant or change your preferences.",
                                     f"I can't quite process that answer. Could you please confirm or deny whether you want a new restaurant or change your preferences.?"]))
            else:  # informal
                print(random.choice([f"Sorry, didn't catch that. Want a new place or change what you want?",
                                     f"Huh? New restaurant or different preferences?"]))
        else:
            if speech == "formal":
                print(random.choice(["Would you like a new restaurant with the same parameters or not?",
                                     "Do you want a different restaurant with the same preferences?"]))
            else:  # informal
                print(random.choice(["Want a different place with the same stuff?",
                                     "Try another restaurant or change what you want?"]))
   
    elif nextstate == 8:
        if confuse:
            if speech == "formal":
                print(random.choice(["Sorry, I didn't understand that. Please mention the preference you want to change.",
                                     "Unfortunately I couldn't understand that. Please mention the preference you wish to change (food, price or area)."]))
            else:  # informal
                print(random.choice(["Sorry, didn't get that. What do you want to change?",
                                     "Huh? Just tell me what to change - food, price, or area."]))
        else:
            if speech == "formal":
                print(random.choice(["Please mention a preference to change.",
                                     "Could you please mention a preference to change? Either food, price or area."]))
            else:  # informal
                print(random.choice(["What do you want to change?",
                                     "Just tell me what to switch - food, price, or area."]))
   
    elif nextstate == 9:
        if speech == "formal":
            print(f"You have chosen {restaurant_info[0]} of {preferences_memory['food']} cuisine, {preferences_memory['pricerange']} priced and in {preferences_memory['area']}.")
            print(f"The address for {restaurant_info[0]} is {restaurant_info[2]}, phone number is {restaurant_info[1]}, and postcode is {restaurant_info[3]}")
            print("Enjoy your meal!")
        else:  # informal
            print(f"So you picked {restaurant_info[0]} - it's {preferences_memory['food']}, {preferences_memory['pricerange']} priced, and in {preferences_memory['area']}.")
            print(f"{restaurant_info[0]} is at {restaurant_info[2]}, call them at {restaurant_info[1]}, postcode {restaurant_info[3]}")
            print("Have a good meal!")
        return None
   
    new_input = input("\n").lower()
    current_pref = preferences_memory
    statetransition(nextstate, new_input, ml_dialog, keywords_dict, filename, preferences_memory, restaurant_info, speech)