# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import sqlite3
import os

cousine=""
city=""

class ActionCusine(Action):
    def name(self) -> Text:
        return "action_cusine"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        cousine=tracker.get_slot('cuisine')
        
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "prod.db")

        with sqlite3.connect(db_path) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM 'restaurants' WHERE Cuisines LIKE UPPER('%"+str(cousine)+"%')")
            r = [dict((cur.description[i][0], value) \
                    for i, value in enumerate(row)) for row in cur.fetchall()]    
            row = (r[0] if r else None) if False else r   
        if len(row) == 0:
            dispatcher.utter_message(text="Did not get you, can you re enter the cuisine.")
        else:            
            dispatcher.utter_message(text="Your have selected *"+cousine+"*")
        return []

class ActionCity(Action):
    def name(self) -> Text:
        return "action_city"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        city=tracker.get_slot('location')

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "prod.db")

        buttons = []

        unique_list = []
        cuiseineList = ""
        cuisines = []

        buttons.append({"title": "Yes", "payload": "yes_intent"})
        buttons.append({"title": "No", "payload": "no_intent"})

        with sqlite3.connect(db_path) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM 'restaurants' WHERE UPPER(City) LIKE UPPER('%"+str(city)+"%')")
            r = [dict((cur.description[i][0], value) \
                    for i, value in enumerate(row)) for row in cur.fetchall()]    
            row = (r[0] if r else None) if False else r

        for res in row:
            if "," in res['Cuisines']:
                cuisines.append(res['Cuisines'])
            else:
                cuisines.extend(res['Cuisines'].split(","))        

        for x in cuisines:
            temp = x.split(",")
            if len(temp) > 1:
                for it in temp:
                    if it.strip() not in unique_list:
                        cuiseineList = cuiseineList+"- "+it.strip()
                        unique_list.append(it.strip())
            else:
                if x.strip() not in unique_list:
                    cuiseineList = cuiseineList+"- "+x.strip()+"\n"
                    unique_list.append(x.strip())
                            
        if len(row) == 0:
            dispatcher.utter_message(text="City not found in database do you want to re-enter.", buttons=buttons)
        else:
            dispatcher.utter_message(text="Your have selected *"+city+"*")
            dispatcher.utter_message(text="Which cuisine you like to have ? "+cuiseineList)
        return []

class ActionRestaurant(Action):
    def name(self) -> Text:
        return "action_restaurant"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
        city=tracker.get_slot('location')
        cousine=tracker.get_slot('cuisine')

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "prod.db")

        buttons = []
        res = []
        tag = ["A","B","C","D"]
        mcount = 5

        with sqlite3.connect(db_path) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM 'restaurants' WHERE UPPER(City) LIKE UPPER('%"+str(city)+"%') AND UPPER(Cuisines) LIKE UPPER('%"+str(cousine)+"%')")
            r = [dict((cur.description[i][0], value) \
                    for i, value in enumerate(row)) for row in cur.fetchall()]    
            row = (r[0] if r else None) if False else r        

        if len(row) == 0:
            reply = "No restaurant found with such a combinations"

        if len(row) < 5:
            for item in row:
                buttons.append({"title": item['Restaurant Name'], "payload": item['Restaurant Name']})
                res.append(item['Restaurant Name']+","+item['Address'])
            reply = "Which restaurant you like to have food from ? \n"
            c = 0
            for n in res:
                reply = "- "+tag[c]+" : "+res[c]+"\n"
                c = c+1
        else:
            for item in row:
                mcount = mcount - 1
                buttons.append({"title": item['Restaurant Name'], "payload": item['Restaurant Name']})
                res.append(item['Restaurant Name']+","+item['Address'])
                if mcount == 0:
                    break
            reply = "Which restaurant you like to have food from ? \n- A : "+res[0]+"\n- B : "+res[1]+"\n- C : "+res[2]+"\n- D : "+res[3]+"\n- E : "+res[4]+""        
        dispatcher.utter_message(text=reply, buttons=buttons)
        return []

class ActionMenu(Action):
    def name(self) -> Text:
        return "action_menu"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        

        cousine=tracker.get_slot('cuisine')

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "prod.db")

        with sqlite3.connect(db_path) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM 'menu' WHERE UPPER(cusine) LIKE UPPER('%"+str(cousine)+"%')")
            r = [dict((cur.description[i][0], value) \
                       for i, value in enumerate(row)) for row in cur.fetchall()]    
            row = (r[0] if r else None) if False else r    

        count = 1
        if len(row) == 0:
            reply = "No menu item found for this restaurant."
        else:
            reply = "What you like to order ?\n"
            for item in row:            
                reply = reply + "- "+str(count)+": "+item['name']+","+str(item['price'])+" ₹ \n"
                count = count+1        
        dispatcher.utter_message(text=reply)
        return []

class ActionOrder(Action):
    def name(self) -> Text:
        return "action_order"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:         
        msg = tracker.latest_message['text']
        cousine=tracker.get_slot('cuisine')

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "prod.db")

        total = 0
        order = []
        if "," in msg:
            order = msg.split(",")
        else:
            order.append(msg)
        with sqlite3.connect(db_path) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM 'menu' WHERE UPPER(cusine) LIKE UPPER('%"+str(cousine)+"%')")
            r = [dict((cur.description[i][0], value) \
                        for i, value in enumerate(row)) for row in cur.fetchall()]    
            row = (r[0] if r else None) if False else r    

        count = 1
        isMenu = False

        buttons = []

        buttons.append({"title": "Yes", "payload": "yes_intent"})
        buttons.append({"title": "No", "payload": "no_intent"})

        if len(row) == 0:
            reply = "No menu item found for this restaurant."
        else:    
            if len(order) > 1:        
                for item in row:
                    print(str(count))
                    if (str(count) in order):
                        total = total+item['price']
                    count = count+1
                    isMenu = True
            else:
                if int(order[0]) > len(row):
                    isMenu = False
                else:
                    for item in row:
                        if (str(count) in order):
                            total = total+item['price']
                            count = count+1
                        isMenu = True
        if isMenu == True:
            reply = "Your Final Order Total is : "+str(total)+" ₹"
            buttons = []
        else:
            reply = "Your item not found in menu do you want to continue."

        dispatcher.utter_message(text=reply, buttons=buttons)
        return []