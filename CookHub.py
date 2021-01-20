from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.uix.button import ButtonBehavior, Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
import sqlite3
import random

db = sqlite3.connect("RAW_recipes.db")  # The DataSet
curs = db.cursor()  # Cursor for execution

info_list = open("info_list.txt", "r").read().split("|")  # List as memory
favourite_list = info_list[0].split(",")[:-1]  # Contains FavouriteRecipes
fridge_list = info_list[1].split(",")[:-1]  # Contains FridgeIngredients
shopping_list = info_list[2].split(",")[:-1]  # Contains ShoppingLists

sm = ScreenManager()
sm.transition.direction = 'down'

logo = """
Label:
    text: "CookHub"
    font_size: root.height//1.4
    color: (224/255,10/255,20/255,1)
    canvas.before:
        Color:
            rgba: (1,1,1,1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [17,17,17,17]
    size_hint: 0.8,0.1
    pos_hint: {"x":0.1, "top":0.9}
"""  # Will present on each page.


height = Window.height


class ShowingList(FloatLayout):
    f_s = (Window.width + Window.height)//115  # Static font_size for dynamic layout
    t_s = (Window.width//7, None)  # Static text_size for dynamic layout

    def __init__(self, recipe_name="None"):
        super(ShowingList, self).__init__()
        self.list_logo = Builder.load_string("""
Label:        
    text:"I need to buy:"
    size_hint: (0.9, 0.1)
    pos_hint: {"x":0.05, "top":0.95}
    font_size:(root.width+root.height)//12
    color: (0.8, 0.1, 0.4, 1)
    canvas.before:
        Color:
            rgba: (179/255, 220/255, 111/255, 1)
        Rectangle:
            size: self.size
            pos: self.pos
        """)
        self.add_widget(self.list_logo)
        self.to_buy_list = Builder.load_string("""
ScrollView:
    size_hint: (0.9, 0.6)
    pos_hint: {"x": 0.05, "top": 0.81} 
    s_gl: s_gl
    s_gl1: s_gl1
    s_gl2: s_gl2
    
    GridLayout:
        id: s_gl
        cols: 2
        size_hint_y: None
        spacing: root.width//25, 0
        GridLayout:
            id: s_gl1
            spacing: 0, root.width//15
            cols: 1
            size_hint: 0.2, None
        GridLayout:
            id: s_gl2
            spacing: 0, root.width//15
            cols: 1
            size_hint: 0.8, None        
        """)

        self.add_widget(self.to_buy_list)
        required_ingredients = str(curs.execute(f'SELECT ingredients FROM '
                                                f'CookHub WHERE '
                                                f'name="{recipe_name.lower()}"').fetchall())
        required_ingredients = required_ingredients[4:-5].split(",")
        z = []
        for i in required_ingredients:
            i = i.strip(" ' ").capitalize()
            if i not in fridge_list:
                z.append(i)
        self.to_buy_list.s_gl.height = len(z)*50
        self.to_buy_list.s_gl1.height = len(z)*50
        self.to_buy_list.s_gl2.height = len(z)*50

        for i in sorted(z):
            if_bought = CheckBox(id=f"{i}", color=(1, 1, 120/255, 1))
            self.to_buy_list.s_gl1.add_widget(if_bought)
            lists_btn = Button(text=f"{i}",
                               font_size=self.f_s, text_size=self.t_s,
                               background_color=(63/255, 135/255, 232/255, 1))
            self.to_buy_list.s_gl2.add_widget(lists_btn)
        # self.add_widget(self.close)


class AddingIngredients(FloatLayout):  # A popup content for VirtualFridge
    def __init__(self):
        super(AddingIngredients, self).__init__()
        self.ingredients_input = TextInput(padding=(10, 10),
                                           size_hint=(0.8, 0.5), pos_hint={"x": .1, "top": .8})  # List of addings
        self.add_widget(self.ingredients_input)
        self.dd = DropDown(max_height=Window.height*0.4)  # Will Display All Possible Ingredients
        self.mainbutton = Button(text="Select Ingredients:",
                                 size_hint=(.9, .1), pos_hint={"x": .05, "top": .25},
                                 background_normal="selection.png")
        self.mainbutton.bind(on_release=self.dd.open)
        self.add_widget(self.mainbutton)

        self.submition = Button(text="Add Ingredients",  # Press to expand Fridge
                                size_hint=(0.9, 0.1), pos_hint={"x": .05, "top": 0.13},
                                background_color=(179/255, 220/255, 111/255, 1),
                                on_press=self.add_to_fridge)
        self.add_widget(self.submition)

        unique_ingredients = curs.execute("SELECT ingredients FROM UNIQUES").fetchall()
        for i in sorted(unique_ingredients[0][0].strip("[]").split(",")):
            i = i.strip(" ' ")
            if i[0] == " ":
                i = i[2:]
            btn = Button(text=f"{i.capitalize()}", text_size=(self.width, None),
                         size_hint_y=None,
                         on_release=lambda buttn: self.dd.select(buttn.text),
                         background_color=(12/255, 63/255, 82/255, 1))
            self.dd.add_widget(btn)
        self.dd.bind(on_select=lambda intance, x: self.add_to_input(x))

    def add_to_input(self, x):  # Chosen ingredients will be Added to INgredientsInput
        try:
            if self.ingredients_input.text[-1] == ",":
                self.ingredients_input.text += f"{x},"
            else:
                self.ingredients_input.text += f",{x},"
        except:
            self.ingredients_input.text += f"{x},"

    def add_to_fridge(self, action):  # Ingredients From IngredientsInput getting added to Fridge
        try:
            new_ingredients = self.ingredients_input.text.split(",")
            for i in new_ingredients:
                if i != "":
                    fridge_list.append(i)
            with open("info_list.txt", "w") as file:
                for i in favourite_list:
                    print(f"{i}", end=",", file=file)
                print("|",  end="", file=file)
                for i in fridge_list:
                    print(f"{i}", end=",", file=file)
                print("|", end="", file=file)
                for i in shopping_list:
                    print(f"{i}", end=",", file=file)
            virtualfridge_screen.ingredients_listing()
            self.ingredients_input.text = ""
            virtualfridge_screen.popup_window.dismiss()
        except:
            pass


Builder.load_string("""  # Easier to add via loading
<AddingIngredients>:
    Label:        
        text:"Add Ingredients:"
        size_hint:(0.9, 0.1)
        pos_hint: {"x":0.05, "top":0.95}
        font_size:(root.width+root.height)//30
        color: (1,1,1,1)
        canvas.before:
            Color:
                rgba: (45/255, 105/255, 200/255, 1)
            Rectangle:
                size: self.size
                pos: self.pos
""")


class ImageButton(ButtonBehavior, Image):
    def __init__(self, src="add.png", **kwargs):
        super(ImageButton, self).__init__(**kwargs)
        self.source = src
        if src == "delete.png":
            self.on_press = self.delete_ingredients
        if src == "delete2.png":
            self.on_press = self.delete_shoppinglists

    def delete_ingredients(self):  # Will remove Chosen Ingredient From Virtual Fridge
        fridge_list.remove(self.id)
        with open("info_list.txt", "w") as file:
            for i in favourite_list:
                print(f"{i}", end=",", file=file)
            print("|", end="", file=file)
            for i in fridge_list:
                print(f"{i}", end=",", file=file)
            print("|", end="", file=file)
            for i in shopping_list:
                print(f"{i}", end=",", file=file)
        virtualfridge_screen.ingredients_listing()

    def delete_shoppinglists(self):  # Will remove Chosen ShoppingList
        shopping_list.remove(self.id)
        with open("info_list.txt", "w") as file:
            for i in shopping_list:
                print(f"{i}", end=",", file=file)
            print("|", end="", file=file)
            for i in fridge_list:
                print(f"{i}", end=",", file=file)
            print("|", end="", file=file)
            for i in shopping_list:
                print(f"{i}", end=",", file=file)
        shoppinglist_screen.shopping_listing()


class IconButton(ButtonBehavior, Image):  # Pressing will switch Pages
    def __init__(self, src, dest="Home"):
        super(IconButton, self).__init__()
        self.source = src
        # self.size = Window.width*0.1, 140
        self.size_hint = 0.1, None
        self.allow_stretch = True
        self.keep_ratio = False
        self.dest = dest

    def on_press(self):
        sm.transition.direction = "up"
        sm.current = self.dest


class ButtonPanel(Widget):
    def __init__(self, direct="down"):
        super(ButtonPanel, self).__init__()
        sm.transition.direction = direct
        self.icons_box = Builder.load_string("""  # Buttons' Holder
GridLayout:
    size_hint: 1,None
    height: {}
    rows:1
        """.format(height*0.12))

        self.icons_box.add_widget(IconButton(src="home.png"))
        self.icons_box.add_widget(IconButton(src="search.png",
                                  dest="Search"))
        self.icons_box.add_widget(IconButton(src="virtualfridge.png",
                                  dest="VF"))
        self.icons_box.add_widget(IconButton(src="shoppinglist.png",
                                  dest="SL"))
        self.icons_box.add_widget(IconButton(src="favourite.png", dest="F"))


class RecipeDetails(Screen, FloatLayout):  # Shows Info of chosen recipe
    if_favourite_btn = Button()
    if_favourite_cb = CheckBox()
    create_shoppingist = Button()
    listing = ""

    def __init__(self, recipe_name, minutes, tags, nutrition, n_steps,
                 steps, description, ingredients, n_ingredients, **kwargs):
        super(RecipeDetails, self).__init__(**kwargs)
        self.logo = Builder.load_string(logo)
        self.logo.pos_hint = {"x": .1, "top": .98}
        self.add_widget(self.logo)
        self.create_shoppingist = Button(text="Create Shopping List",
                                         size_hint=(0.7, 0.07),
                                         pos_hint={"top": 0.86, "x": 0.15},
                                         font_size=(Window.width+Window.height)//55,
                                         on_press=self.change_shoppinglist,
                                         background_color=(179/255, 220/255, 111/255, 1))
        self.if_favourite_btn = Button(text="Select As Favourite",
                                       size_hint=(0.7, 0.07),
                                       pos_hint={"top": 0.78, "x": 0.15},
                                       font_size=(Window.width+Window.height)//55,
                                       background_color=(179/255, 220/255, 111/255, 1))
        self.add_widget(self.create_shoppingist)
        self.if_favourite_btn.on_press = self.change_favourite
        self.add_widget(self.if_favourite_btn)

        self.if_favourite_cb = CheckBox(size_hint=(0.15, 0.3),
                                        pos_hint={"top": 0.9, "x": 0},
                                        color=(233/255, 169/255, 63/255, 1))
        self.add_widget(self.if_favourite_cb)
        if recipe_name in favourite_list:
            self.if_favourite_cb.active = True
            self.if_favourite_btn.text = "Remove from Favourite"
        self.recipe_name = recipe_name
        self.minutes = minutes
        self.tags = tags
        self.nutrition = nutrition[1:-1].split(",")
        self.n_steps = n_steps
        self.steps = steps
        self.description = description
        self.ingredients = ingredients
        self.n_ingredients = n_ingredients
        self.all_details = Builder.load_string("""  # Will display all information
GridLayout:
    cols:1
    sv:sv
    size_hint: 1, 0.7
    pos_hint: {0}
    ScrollView:
        id: sv
        gl: gl
        l:l
        l2: l2
        size_hint: 1, 1
    
        GridLayout:
            id: gl
            spacing: 0, root.height*0.03
            height: root.height*3
            size_hint_y: None
            cols: 1
            GridLayout:
                cols: 2
                spacing: root.width*0.03, 0
                GridLayout:
                    spacing: 0, root.height*0.04
                    size_hint_y: 0.2
                    cols: 1
                    Label:  
                        text: "{2}"                    
                        padding_x: root.width*0.05
                        font_size: (root.width+root.height)//35
                        size_hint: 0.5, 0.2
                        text_size: root.width//2, None
    
                        canvas.before:
                            Color:
                                rgba: (52/255,72/255,96/255,1)
                            Rectangle:
                                size: self.size
                                pos: self.pos
                    Label:  
                        text: "{3}"                    
                        padding_x: root.width*0.05
                        font_size: (root.width+root.height)//40
                        size_hint: 0.5, 0.2
                        text_size: root.width//2, None
    
                        canvas.before:
                            Color:
                                rgba: (52/255,72/255,96/255,1)
                            Rectangle:
                                size: self.size
                                pos: self.pos
                    Label:  
                        padding_x: root.width*0.05
                        font_size: (root.width+root.height)//40
                        text: "{4}"
                        size_hint: 0.5, 0.2
                        text_size: root.width//2, None
                        canvas.before:
                            Color:
                                rgba: (52/255,72/255,96/255,1)
                            Rectangle:
                                size: self.size
                                pos: self.pos
                    Label:  
                        padding_x: root.width*0.05
                        font_size: (root.width+root.height)//40
                        text: "{5}"
                        size_hint: 0.5, 0.2
                        text_size: root.width//2, None
                        canvas.before:
                            Color:
                                rgba: (52/255,72/255,96/255,1)
                            Rectangle:
                                size: self.size
                                pos: self.pos
                GridLayout:
                    size_hint: (0.9, 0.55)
    
                    cols: 1
                    ScrollView:       
                        Label:
                            size_hint_y: None
                            height: root.height*3
                            text: "{6}" 
                            padding_x: root.width*0.05
                            font_size: (root.width+root.height)//40
                            text_size: root.width//2, None
                            canvas.before: 
                                Color:
                                    rgba: (52/255,72/255,96/255,1)
                                Rectangle:
                                    size: self.size
                                    pos: self.pos  
            GridLayout:
                rows:4
                spacing: 0, root.height*0.03
                ScrollView:        
                    Label:
                        height: root.height//1.1
                        size_hint_y: None
                        padding_x: root.width*0.05
                        text: "Ingredients:{1}"
                        font_size: (root.width+root.height)//35
                        text_size: root.width, None
                        canvas.before: 
                            Color:
                                rgba: (52/255,72/255,96/255,1)
                            Rectangle:
                                size: self.size
                                pos: self.pos  
                ScrollView:
                    Label:
                        size_hint_y: None
                        padding_x: root.width*0.05
                        height: root.height//1.1
                        text: "Tags: {7}"
                        font_size: (root.width+root.height)//35
                        text_size: root.width, None
                        canvas.before: 
                            Color:
                                rgba: (52/255,72/255,96/255,1)
                            Rectangle:
                                size: self.size
                                pos: self.pos  
                ScrollView:
                    Label:
                        id: l
                        size_hint_y: None
                        padding_x: root.width*0.05
                        height: root.height//1.1
                        font_size: (root.width+root.height)//35
                        text_size: root.width, None
                        canvas.before: 
                            Color:
                                rgba: (52/255,72/255,96/255,1)
                            Rectangle:
                                size: self.size
                                pos: self.pos  
                ScrollView:        
                    Label:
                        id: l2
                        height: root.height*2
                        size_hint_y: None
                        padding_x: root.width*0.05
                        font_size: (root.width+root.height)//35
                        text_size: root.width, None
                        canvas.before: 
                            Color:
                                rgba: (52/255,72/255,96/255,1)
                            Rectangle:
                                size: self.size
                                pos: self.pos  
        """.format({"x": 0, "top": 0.69}, self.ingredients[1:-1],
                   f"{self.recipe_name}", f"Takes {self.minutes} minutes!",
                   f"Number of ingredients: {self.n_ingredients}!",
                   f"Number of steps: {self.n_steps}",
                   str(self.description.capitalize()), self.tags[1:-1]))
        self.all_details.add_widget(ButtonPanel().icons_box)

        z = "Steps:"
        j = 1
        for i in list(self.steps[1:-1].split("',")):
            i = i.strip("'")
            i = i.strip(" '")
            z += f'\n{j}){i.capitalize()}'
            j += 1
        self.all_details.sv.l2.text = z
        self.all_details.sv.l.text = f"""
Nutrition:
Total Fat(PDV):{self.nutrition[0]}
Sugar(PDV):{self.nutrition[1]}
Sodium(PDV):{self.nutrition[2]}
Protein(PDV):{self.nutrition[3]}
Saturated Fat(PDV):{self.nutrition[4]}
Carbohydrates(PDV):{self.nutrition[5]}"""
        self.add_widget(self.all_details)

    def change_favourite(self):  # Will either add or remove from favourites:
        if "Select" in self.if_favourite_btn.text:
            self.if_favourite_cb.active = True
            self.if_favourite_btn.text = "Remove from Favourite"
            if self.recipe_name not in favourite_list:
                favourite_list.append(self.recipe_name)
            with open("info_list.txt", "w") as file:
                for i in favourite_list:
                    print(f"{i}", end=",", file=file)
                print("|", end="", file=file)
                for i in fridge_list:
                    print(f"{i}", end=",", file=file)
                print("|", end="", file=file)
                for i in shopping_list:
                    print(f"{i}", end=",", file=file)
        else:
            try:
                favourite_list.remove(self.recipe_name)
            finally:
                with open("info_list.txt", "w") as file:
                    for i in favourite_list:
                        print(f"{i}", end=",", file=file)
                    print("|", end="", file=file)
                    for i in fridge_list:
                        print(f"{i}", end=",", file=file)
                    print("|", end="", file=file)
                    for i in shopping_list:
                        print(f"{i}", end=",", file=file)

            self.if_favourite_cb.active = False
            self.if_favourite_btn.text = "Select As Favourite"
        favourite_screen.listing()

    def change_shoppinglist(self, action):
        shopping_list.append(self.recipe_name)
        shoppinglist_screen.shopping_listing()
        with open("info_list.txt", "w") as file:
            for i in favourite_list:
                print(f"{i}", end=",", file=file)
            print("|", end="", file=file)
            for i in fridge_list:
                print(f"{i}", end=",", file=file)
            print("|", end="", file=file)
            for i in shopping_list:
                print(f"{i}", end=",", file=file)


Builder.load_string("""
<RecipeButton>:
    random_color: (1,1,1,1)
    
    canvas.before:
        Color:
            rgba: self.random_color
        Rectangle:
            size: self.size
            pos: self.pos
""")  # Necessitated due to background


class RecipeButton(ButtonBehavior, Label):  # Creates Button redirecting to recipe details
    def __init__(self, rcp, text_size=(Window.width*0.07, None),
                 font_size=Window.width//60):
        super(RecipeButton, self).__init__()
        self.text = rcp
        self.text_size = text_size
        self.font_size = font_size
        colors_choice = [
            (154/255, 88/255, 188/255, 1),
            (52/255, 205/255, 99/255, 1),
            (27/255, 160/255, 131/255, 1),
            (211/255, 85/255, 0/255, 1),
            (152/255, 164/255, 164/255, 1),
            (235/255, 112/255, 94/255, 1),
            (39/255, 127/255, 191/255, 1)]
        self.random_color = random.choice(colors_choice)

    def on_press(self):
        recipe_details = curs.execute(
            f'SELECT * FROM CookHub where name'
            f'="{self.text.lower()}"').fetchall()[0]
        try:
            sm.remove_widget(sm.get_screen("RD"))
        except:
            pass
        finally:
            sm.add_widget(RecipeDetails(name="RD", recipe_name=self.text,
                                        minutes=recipe_details[1], tags=recipe_details[2],
                                        nutrition=recipe_details[3], n_steps=recipe_details[4],
                                        steps=recipe_details[5], description=recipe_details[6],
                                        ingredients=recipe_details[7], n_ingredients=recipe_details[8]))

        sm.current = "RD"


Builder.load_string("""
<ShowingList>:
    close: close
    Button:
        id: close
        text:"Done!"  # Press to close Popup
        size_hint:(0.9, 0.1)
        pos_hint:{"x": .05, "top": 0.15}
        background_color:(179/255, 220/255, 111/255, 1)
""")


Builder.load_string("""
<SmoothButton@Button>:
    background_color: (0,0,0,0)
    canvas.before:
        Color:
            rgba: (10/255, 101/255, 131/255, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [15,15,15,15]

<Search>:
    by_name: by_name
    by_tag: by_tag
    by_ingredient: by_ingredient
    Label:        
        text:"Search By:"
        size_hint:(0.9, 0.1)
        pos_hint: {"x":0.05, "top":0.75}
        font_size:(root.width+root.height)//30
        color: (0.8, 0.1, 0.4, 1)
        canvas.before:
            Color:
                rgba: (179/255, 220/255, 111/255, 1)
            Rectangle:
                size: self.size
                pos: self.pos
    SmoothButton:
        id: by_name
        text: "By Name"
        size_hint: 0.8, 0.1
        pos_hint: {"x":0.1, "top":0.6}
    SmoothButton:
        id: by_tag
        text: "By Tag"
        size_hint: 0.8, 0.1
        pos_hint: {"x":0.1, "top":0.47}
    SmoothButton:
        id: by_ingredient
        text: "By Ingredient"
        size_hint: 0.8, 0.1
        pos_hint: {"x":0.1, "top":0.34}       
""")


class ByIngredient(FloatLayout):
    f_s = (Window.width + Window.height)//100  # Static font_size for dynamic layout
    t_s = (Window.width//6, None)  # Static text_size for dynamic layout
    id_s = []
    name = []  # Container for  matching names, preventing duplicates

    def __init__(self):
        super(ByIngredient, self).__init__()
        self.add_widget(Builder.load_string("""
Label:        
    text:"Enter Ingredient:"
    size_hint:(0.9, 0.1)
    pos_hint: {"x":0.05, "top":.97}
    font_size:(root.width+root.height)//12
    color: (0.8, 0.1, 0.4, 1)
    canvas.before:
        Color:
            rgba: (179/255, 220/255, 111/255, 1)
        Rectangle:
            size: self.size
            pos: self.pos
        """))
        self.search_output = Builder.load_string("""
ScrollView:
    size_hint: 0.9, .46
    pos_hint: {"x":0.05, "top": .6}
    gl:gl
    GridLayout:
        id: gl
        cols: 1
        spacing: 0, root.width//25
        size_hint_y: None
        """)
        self.add_widget(self.search_output)
        self.search_input = TextInput(padding=(5, 5), size_hint=(0.69, 0.1),
                                      pos_hint={"x": .05, "top": .84}, multiline=False)
        self.do_search = ImageButton(src="search2.png", size_hint=(.2, .2),
                                     pos_hint={"x": .75, "top": .89})
        self.do_search.on_press = self.find_by_ingredient
        self.add_widget(self.search_input)
        self.add_widget(self.do_search)

        self.close = Button(text="Close", size_hint=(0.8, 0.1),
                            pos_hint={"x": .1, "top": .1},
                            background_color=(179/255, 220/255, 111/255, 1))
        self.add_widget(self.close)

        self.dd = DropDown(max_height=Window.height//3)
        self.mainbutton = Button(text="Select Ingredient:", size_hint=(0.9, 0.1),
                                 pos_hint={"x": .05, "top": .72},
                                 font_size=self.f_s,
                                 background_normal="selection.png")
        self.mainbutton.bind(on_release=self.dd.open)
        self.add_widget(self.mainbutton)

        ingredient = curs.execute("SELECT ingredients from Uniques").fetchall()

        btn = Button(text="1 From VirtualFridge", text_size=(self.width, None),
                     size_hint_y=None, height=Window.height//15,
                     on_release=lambda buttn: self.change_input(buttn.text),
                     background_color=(12/255, 63/255, 82/255, 1),)
        self.dd.add_widget(btn)

        for i in sorted(ingredient[0][0][1:-1].split(",")):
            i = i.strip(" ' ").capitalize()
            btn = Button(text=f"{i}", text_size=(self.width, None),
                         size_hint_y=None, height=Window.height//15,
                         on_release=lambda buttn: self.change_input(buttn.text),
                         background_color=(12/255, 63/255, 82/255, 1),)
            self.dd.add_widget(btn)

    def change_input(self, x):
        self.search_input.text += f"{x},"

    def find_by_ingredient(self):
        self.name = []
        ingredients = curs.execute("SELECT ingredients FROM CookHub").fetchall()
        if "1 From VirtualFridge" in self.search_input.text:
            for f in fridge_list:
                self.search_input.text = self.search_input.text + f"{f},"
        for i in ingredients:
            for j in self.search_input.text.split(",")[:-1]:
                if j.lower() in str(i):
                    try:
                        x = curs.execute(f'SELECT name FROM'
                                         f' CookHub where ingredients="{str(i)[2:-3]}"').fetchall()
                        if x[0][0] not in self.name:
                            self.name.append(x[0][0])
                    except:
                        continue
        try:
            for i in self.id_s:
                self.search_output.gl.remove_widget(i)
        except:
            pass
        self.search_output.gl.height = 0
        for i in self.name:
            btn = RecipeButton(rcp=i.capitalize(),
                               text_size=self.t_s, font_size=self.f_s)
            self.id_s.append(btn)
            self.search_output.gl.add_widget(btn)
            self.search_output.gl.height += 50


class ByTag(FloatLayout):
    f_s = (Window.width + Window.height)//100  # Static font_size for dynamic layout
    t_s = (Window.width//6, None)  # Static text_size for dynamic layout
    id_s = []
    name = []  # Container for  matching names, preventing duplicates

    def __init__(self):
        super(ByTag, self).__init__()
        self.add_widget(Builder.load_string("""
Label:        
    text:"Enter Tag:"
    size_hint:(0.9, 0.1)
    pos_hint: {"x":0.05, "top":.97}
    font_size:(root.width+root.height)//12
    color: (0.8, 0.1, 0.4, 1)
    canvas.before:
        Color:
            rgba: (179/255, 220/255, 111/255, 1)
        Rectangle:
            size: self.size
            pos: self.pos
        """))
        self.search_output = Builder.load_string("""
ScrollView:
    size_hint: 0.9, .46
    pos_hint: {"x":0.05, "top": .6}
    gl:gl
    GridLayout:
        id: gl
        cols: 1
        spacing: 0, root.width//25
        size_hint_y: None
        """)
        self.add_widget(self.search_output)
        self.search_input = TextInput(padding=(5, 5), size_hint=(0.69, 0.1),
                                      pos_hint={"x": .05, "top": .84}, multiline=False)
        self.do_search = ImageButton(src="search2.png", size_hint=(.2, .2),
                                     pos_hint={"x": .75, "top": .89})
        self.do_search.on_press = self.find_by_tag
        self.add_widget(self.search_input)
        self.add_widget(self.do_search)

        self.close = Button(text="Close", size_hint=(0.8, 0.1),
                            pos_hint={"x": .1, "top": .1},
                            background_color=(179/255, 220/255, 111/255, 1))
        self.add_widget(self.close)

        self.dd = DropDown(max_height=Window.height//3)
        self.mainbutton = Button(text="Select Tags:", size_hint=(0.9, 0.1),
                                 pos_hint={"x": .05, "top": .72},
                                 background_normal="selection.png")
        self.mainbutton.bind(on_release=self.dd.open)
        self.add_widget(self.mainbutton)

        tag = curs.execute("SELECT tags from Uniques").fetchall()
        for i in sorted(tag[0][0][1:-1].split(",")):
            i = i.strip(" ' ").capitalize()
            btn = Button(text=f"{i}", text_size=(self.width, None),
                         size_hint_y=None, height=Window.height//15,
                         on_release=lambda buttn: self.change_input(buttn.text),
                         background_color=(12/255, 63/255, 82/255, 1),)
            self.dd.add_widget(btn)

    def change_input(self, x):
        self.search_input.text += f"{x},"

    def find_by_tag(self):
        self.name = []
        tags = curs.execute("SELECT tags FROM CookHub").fetchall()
        for i in tags:
            for j in self.search_input.text.split(",")[:-1]:
                if j.lower() in str(i):
                    try:
                        x = curs.execute('SELECT name FROM'
                                             f' CookHub where tags="{str(i)[2:-3]}"').fetchall()
                        if x[0][0] not in self.name:
                            self.name.append(x[0][0])
                    except:
                        continue
        try:
            for i in self.id_s:
                self.search_output.gl.remove_widget(i)
        except:
            pass
        self.search_output.gl.height = 0
        for i in self.name:
            btn = RecipeButton(rcp=i.capitalize(),
                               text_size=self.t_s, font_size=self.f_s)
            self.id_s.append(btn)
            self.search_output.gl.add_widget(btn)
            self.search_output.gl.height += 50


class ByName(FloatLayout):
    f_s = (Window.width + Window.height)//100  # Static font_size for dynamic layout
    t_s = (Window.width//6, None)  # Static text_size for dynamic layout
    id_s = []

    def __init__(self):
        super(ByName, self).__init__()
        self.add_widget(Builder.load_string("""
Label:        
    text:"Enter Name:"
    size_hint:(0.9, 0.1)
    pos_hint: {"x":0.05, "top":.97}
    font_size:(root.width+root.height)//12
    color: (0.8, 0.1, 0.4, 1)
    canvas.before:
        Color:
            rgba: (179/255, 220/255, 111/255, 1)
        Rectangle:
            size: self.size
            pos: self.pos
        """))
        self.search_output = Builder.load_string("""
ScrollView:
    size_hint: 0.9, .6
    pos_hint: {"x":0.05, "top": .72}
    gl:gl
    GridLayout:
        id: gl
        cols: 1
        spacing: 0, root.width//25
        size_hint_y: None
        """)
        self.add_widget(self.search_output)
        self.search_input = TextInput(padding=(5, 5), size_hint=(0.69, 0.1),
                                      pos_hint={"x": .05, "top": .84}, multiline=False)
        self.do_search = ImageButton(src="search2.png", size_hint=(.2, .2),
                                     pos_hint={"x": .75, "top": .89})
        self.do_search.on_press = self.find_by_name
        self.add_widget(self.search_input)
        self.add_widget(self.do_search)

        self.close = Button(text="Close", size_hint=(0.8, 0.1),
                            pos_hint={"x": .1, "top": .1},
                            background_color=(179/255, 220/255, 111/255, 1))
        self.add_widget(self.close)

    def find_by_name(self):
        name = curs.execute("SELECT name from CookHub").fetchall()
        try:
            for i in self.id_s:
                self.search_output.gl.remove_widget(i)
        except:
            pass
        self.search_output.gl.height = 0
        for i in name:
            for j in self.search_input.text.split(" "):
                if j.lower() in i[0] and j != "" and j != " ":
                    btn = RecipeButton(rcp=i[0].capitalize(),
                                       text_size=self.t_s, font_size=self.f_s)
                    self.id_s.append(btn)
                    self.search_output.gl.add_widget(btn)
                    self.search_output.gl.height += 50


class Search(Screen, FloatLayout):
    def __init__(self, **kwargs):
        super(Search, self).__init__(**kwargs)
        self.add_widget(ButtonPanel().icons_box)
        self.add_widget(Builder.load_string(logo))

        show1 = ByName()
        self.by_name_popup = Popup(title="Search by Name",
                                         content=show1,
                                         title_color=(224/255, 10/255, 20/255, 1),
                                         size_hint=(.9, .9),
                                         background="bg.png")
        show1.close.on_press = self.by_name_popup.dismiss
        self.by_name.on_press = self.by_name_popup.open

        show2 = ByTag()
        self.by_tag_popup = Popup(title="Search by Tag",
                                  content=show2,
                                  title_color=(224/255, 10/255, 20/255, 1),
                                  size_hint=(.9, .9),
                                  background="bg.png")
        show2.close.on_press = self.by_tag_popup.dismiss
        self.by_tag.on_press = self.by_tag_popup.open

        show3 = ByIngredient()
        self.by_ingredient_popup = Popup(title="Search by Ingredient",
                                         content=show3,
                                         title_color=(224/255, 10/255, 20/255, 1),
                                         size_hint=(.9, .9),
                                         background="bg.png")
        show3.close.on_press = self.by_ingredient_popup.dismiss
        self.by_ingredient.on_press = self.by_ingredient_popup.open


sm.add_widget(Search(name="Search"))


class ShoppingList(Screen, FloatLayout):  # ShoppingList Page
    id_s = []
    popup_window = Popup(title="Buy Ingredients",
                         title_color=(224/255, 10/255, 20/255, 1),
                         size_hint=(0.9, 0.8),
                         background="bg.png")

    def __init__(self, **kwargs):
        super(ShoppingList, self).__init__(**kwargs)
        self.add_widget(Builder.load_string(logo))
        self.ShoppingLayout = Builder.load_string("""
FloatLayout:
    gl: gl
    s_gl: s_gl
    s_gl1: s_gl1
    s_gl2: s_gl2
    size_hint: 1, 0.8
    pos_hint: {"x":0, "top":0.8}

    Label:        
        text:"My Shopping Lists:"
        size_hint:(0.9, 0.1)
        pos_hint: {"x":0.05, "top":0.98}
        font_size:(root.width+root.height)//30
        color: (0.8, 0.1, 0.4, 1)
        canvas.before:
            Color:
                rgba: (179/255, 220/255, 111/255, 1)
            Rectangle:
                size: self.size
                pos: self.pos
    GridLayout:
        id: gl
        cols: 1
        FloatLayout:
            size_hint: 1,1
            ScrollView:
                size_hint: 0.9, 0.7
                pos_hint: {"x":0.05, "top":0.83}
                canvas.before:
                GridLayout:
                    id: s_gl
                    cols: 2
                    size_hint_y: None
                    spacing: root.width//25, 0
                    GridLayout:
                        id: s_gl1
                        size_hint: 0.2, None
                        spacing: 0, root.width//15
                        cols: 1
                    GridLayout:
                        id: s_gl2
                        size_hint: 0.8, None
                        spacing: 0, root.width//15
                        cols: 1

        """)
        self.f_s = (Window.width + Window.height)//100  # Static font_size for dynamic layout
        self.t_s = (Window.width//6, None)  # Static text_size for dynamic layout
        self.shopping_listing()

        self.ShoppingLayout.gl.add_widget(ButtonPanel().icons_box)
        self.add_widget(self.ShoppingLayout)

    def shopping_listing(self):
        self.show = ShowingList()
        self.popup_window.content = self.show
        self.ShoppingLayout.s_gl.height = len(shopping_list)*50
        self.ShoppingLayout.s_gl1.height = len(shopping_list)*50
        self.ShoppingLayout.s_gl2.height = len(shopping_list)*50
        for i in self.id_s:
            self.ShoppingLayout.s_gl1.remove_widget(i[0])
            self.ShoppingLayout.s_gl2.remove_widget(i[1])
        self.id_s = []
        for i in sorted(shopping_list):
            delete_btn = ImageButton(src="delete2.png", id=f"{i}")
            self.ShoppingLayout.s_gl1.add_widget(delete_btn)
            lists_btn = Button(text=f"{i}",
                                    font_size=self.f_s, text_size=self.t_s,
                                    background_color=(92/255, 146/255, 48/255, 1),
                                    on_press=lambda btn: self.popup_open(btn.text))
            self.id_s.append([delete_btn, lists_btn])
            self.ShoppingLayout.s_gl2.add_widget(lists_btn)

    def popup_open(self, x):
        show = ShowingList(x)
        self.popup_window.content = show
        show.close.on_press = self.popup_window.dismiss
        self.popup_window.open()


shoppinglist_screen = ShoppingList(name="SL")
sm.add_widget(shoppinglist_screen)


class VirtualFridge(Screen, FloatLayout):  # Virtual Fridge Page
    id_s = []

    def __init__(self, **kwargs):
        super(VirtualFridge, self).__init__(**kwargs)
        self.add_widget(Builder.load_string(logo))
        self.FridgeLayout = Builder.load_string("""
FloatLayout:
    gl: gl
    ai: ai
    s_gl: s_gl
    s_gl1: s_gl1
    s_gl2: s_gl2
    size_hint: 1, 0.8
    pos_hint: {"x":0, "top":0.8}
    ImageButton:
        id: ai
        source: "add.png"
        size_hint: (.2, .4)
        pos_hint:{"top": 0.47, "x":0.05}
    Label:
        text: "Add your ingredients"
        font_size: (root.width+root.height)//45
        color: (0.8, 0.1, 0.4, 1)
        canvas.before:
            Color:
                rgba: (179/255, 220/255, 111/255, 1)
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [17,17,17,17]
        size_hint: (0.65, 0.11) 
        pos_hint:{"top": 0.325, "x":0.28}
    Label:        
        text:"My Ingredients:"
        size_hint:(0.9, 0.1)
        pos_hint: {"x":0.05, "top":0.98}
        font_size:(root.width+root.height)//30
        color: (0.8, 0.1, 0.4, 1)
        canvas.before:
            Color:
                rgba: (179/255, 220/255, 111/255, 1)
            Rectangle:
                size: self.size
                pos: self.pos
    GridLayout:
        id: gl
        cols: 1
        FloatLayout:
            size_hint: 1,1
            ScrollView:
                size_hint: 0.9, 0.6
                pos_hint: {"x":0.05, "top":0.83}
                canvas.before:
                GridLayout:
                    id: s_gl
                    cols: 2
                    size_hint_y: None
                    spacing: root.width//25, 0
                    GridLayout:
                        id: s_gl1
                        size_hint: 0.2, None
                        spacing: 0, root.width//15
                        cols: 1
                    GridLayout:
                        id: s_gl2
                        size_hint: 0.8, None
                        spacing: 0, root.width//15
                        cols: 1

        """)
        self.f_s = (Window.width + Window.height)//100  # Static font_size for dynamic layout
        self.t_s = (Window.width//6, None)  # Static text_size for dynamic layout
        self.ingredients_listing()

        self.FridgeLayout.gl.add_widget(ButtonPanel().icons_box)
        self.add_widget(self.FridgeLayout)
        self.show = AddingIngredients()
        self.popup_window = Popup(title="Add Ingredients",
                                  title_color=(224/255, 10/255, 20/255, 1),
                                  content=self.show, size_hint=(0.9, 0.7),
                                  background="bg.png")
        self.FridgeLayout.ai.on_press = self.popup_window.open

    def ingredients_listing(self):
        self.FridgeLayout.s_gl.height = len(fridge_list)*50
        self.FridgeLayout.s_gl1.height = len(fridge_list)*50
        self.FridgeLayout.s_gl2.height = len(fridge_list)*50
        for i in self.id_s:
            self.FridgeLayout.s_gl1.remove_widget(i[0])
            self.FridgeLayout.s_gl2.remove_widget(i[1])
        self.id_s = []
        for i in sorted(fridge_list):
            delete_btn = ImageButton(src="delete.png", id=f"{i}")
            self.FridgeLayout.s_gl1.add_widget(delete_btn)
            ingredient_btn = Button(text=f"{i}",
                                         font_size=self.f_s, text_size=self.t_s,
                                         background_color=(92/255, 146/255, 48/255, 1))
            self.id_s.append([delete_btn, ingredient_btn])
            self.FridgeLayout.s_gl2.add_widget(ingredient_btn)


virtualfridge_screen = VirtualFridge(name="VF")
sm.add_widget(virtualfridge_screen)


class Favourite(Screen, FloatLayout):  # Displays favourite list
    ids = []

    def __init__(self, **kwargs):
        super(Favourite, self).__init__(**kwargs)
        self.add_widget(Builder.load_string(logo))
        self.add_widget(ButtonPanel().icons_box)
        self.add_widget(Builder.load_string("""
Label:        
    text:"Your Favourites:"
    size_hint:(0.9, 0.1)
    pos_hint: {"x":0.05, "top":0.77}
    font_size:(root.width+root.height)//10
    color: (0.8, 0.1, 0.4, 1)
    canvas.before:
        Color:
            rgba: (179/255, 220/255, 111/255, 1)
        Rectangle:
            size: self.size
            pos: self.pos
        """))
        self.favourite_listing = Builder.load_string("""
ScrollView:
    gl: gl
    size_hint: 0.9, 0.4
    pos_hint: {"x": 0.05, "top": 0.63}
    GridLayout:
        id: gl
        size_hint_y: None
        cols: 1
        spacing: 0, root.height * 0.03
        """)
        self.add_widget(self.favourite_listing)
        self.t_s = (self.width*1.5, None)
        self.f_s = Window.width//60
        self.listing()

    def listing(self):
        try:
            for i in self.ids:
                self.favourite_listing.gl.remove_widget(i)
            self.ids = []
        except:
            pass
        self.favourite_listing.gl.height = len(favourite_list)*Window.height*0.08

        for i in range(len(favourite_list)):
            self.ids.append(RecipeButton(
                rcp=favourite_list[i], text_size=self.t_s, font_size=self.f_s))
            self.favourite_listing.gl.add_widget(self.ids[i])


favourite_screen = Favourite(name="F")
sm.add_widget(favourite_screen)


class Home(Screen, FloatLayout):  # Home Page
    def __init__(self, **kwargs):
        super(Home, self).__init__(**kwargs)
        self.add_widget(Builder.load_string(logo))
        self.add_widget(ButtonPanel().icons_box)

        name = curs.execute("SELECT name from CookHub").fetchall()
        curs.execute("SELECT max(rowid) from CookHub")
        n_rows = int(curs.fetchall()[0][0])

        self.recommendation_list = Builder.load_string("""
ScrollView:
    gl: gl
    size_hint: (0.9, 0.55)
    pos_hint: {}
    bar_width: root.width//50
    bar_color: (1,1,1,1)
    GridLayout:
        size_hint_y: None
        spacing: root.width*0.03, root.height*0.04
        id: gl
        cols: 3
        height: {}
        """.format({"x": 0.05, "top": 0.75}, (n_rows/3+1)*110))

        for i in range(n_rows):
            self.recommendation_list.gl.add_widget(RecipeButton(rcp=name[i][0].capitalize()))
        self.add_widget(self.recommendation_list)


sm.add_widget(Home(name="Home"))


class CookHubApp(App):  # Initializing Class
    Window.size = (230, 470)
    Window.clearcolor = (233/255, 169/255, 63/255, 1)

    def build(self):
        sm.current = "Home"
        return sm


if __name__ == "__main__":
    CookHubApp().run()
