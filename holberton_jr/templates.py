"""Starter templates for each camp day — each returns (filename, content)."""

TEMPLATES = [
    {
        "key": "player_profile",
        "name_en": "Player Profile",
        "name_es": "Perfil del Jugador",
        "filename": "player_profile.py",
        "content": """\
# Player Profile
# Fill in your info and see it printed out!

name = input("What's your name? ")
age = input("How old are you? ")
color = input("What's your favorite color? ")
superpower = input("If you had a superpower, what would it be? ")

print()
print("=" * 40)
print(f"  PLAYER PROFILE")
print("=" * 40)
print(f"  Name:       {{name}}")
print(f"  Age:        {{age}}")
print(f"  Color:      {{color}}")
print(f"  Superpower: {{superpower}}")
print("=" * 40)
print(f"\\nWelcome, {{name}}! Your {superpower} powers are now active! ⚡")
""",
    },
    {
        "key": "password_checker",
        "name_en": "Password Checker / Quiz",
        "name_es": "Verificador de Contrasena / Quiz",
        "filename": "password_checker.py",
        "content": """\
# Password Checker / Quiz
# Make your own quiz or password gate!

SECRET = "holberton"

print("Welcome to the secret club!")
guess = input("Enter the password: ")

if guess == SECRET:
    print("Access granted! Welcome inside! 🎉")
else:
    print("Wrong password! Try again next time. 🚫")

# Challenge: add a loop so the user gets 3 tries!
# tries = 0
# while tries < 3:
#     ...
""",
    },
    {
        "key": "guess_number",
        "name_en": "Guess the Number",
        "name_es": "Adivina el Numero",
        "filename": "guess_number.py",
        "content": """\
# Guess the Number
# The computer picks a number, you try to guess it!

import random

secret = random.randint(1, 100)
print("I'm thinking of a number between 1 and 100.")

guesses = 0

while True:
    guess = input("Your guess: ")
    guess = int(guess)
    guesses += 1

    if guess < secret:
        print("Too low! Try higher.")
    elif guess > secret:
        print("Too high! Try lower.")
    else:
        print(f"You got it in {{guesses}} guesses! 🎯")
        break
""",
    },
    {
        "key": "battle_game",
        "name_en": "Battle Game",
        "name_es": "Juego de Batalla",
        "filename": "battle_game.py",
        "content": """\
# Battle Game
# Fight monsters with random attacks!

import random

player_hp = 100
monster_hp = 100
round_num = 0

print("⚔️  BATTLE START! ⚔️")
print(f"You: {{player_hp}} HP  |  Monster: {{monster_hp}} HP")

while player_hp > 0 and monster_hp > 0:
    round_num += 1
    print(f"\\n--- Round {{round_num}} ---")

    # Player's turn
    attack = random.randint(10, 30)
    monster_hp -= attack
    print(f"You attack for {{attack}} damage!")

    # Monster's turn
    if monster_hp > 0:
        monster_attack = random.randint(5, 20)
        player_hp -= monster_attack
        print(f"Monster attacks for {{monster_attack}} damage!")

    print(f"You: {{max(player_hp, 0)}} HP  |  Monster: {{max(monster_hp, 0)}} HP")

if player_hp > 0:
    print("\\n🎉 You win! The monster is defeated!")
else:
    print("\\n💀 Game over! The monster won...")
""",
    },
    {
        "key": "turtle_art",
        "name_en": "Turtle Art",
        "name_es": "Arte con Turtle",
        "filename": "turtle_art.py",
        "content": """\
# Turtle Art
# Draw colorful shapes and spirals!

import turtle
import random

t = turtle.Turtle()
t.speed(0)
turtle.bgcolor("black")

# Draw a colorful hexagon spiral
colors = ["red", "orange", "yellow", "green", "blue", "purple"]
size = 10

for i in range(60):
    t.color(colors[i % len(colors)])
    t.forward(size)
    t.left(59)
    size += 2

# Draw a filled hexagon
t.penup()
t.goto(0, -100)
t.pendown()
t.color("cyan")

for i in range(6):
    t.forward(80)
    t.left(60)

print("Art complete! Close the turtle window when done.")
turtle.done()
""",
    },
    {
        "key": "chatbot",
        "name_en": "Chatbot",
        "name_es": "Chatbot",
        "filename": "chatbot.py",
        "content": """\
# Chatbot
# Your first chatbot that remembers your name!

print("Hi! I'm ChatBot. Type 'quit' to exit.")

name = input("What's your name? ")
print(f"Nice to meet you, {{name}}!")

mood = input("How are you feeling today? (happy/sad/angry/tired): ")

if mood == "happy":
    print("That's great to hear! Keep smiling! 😊")
elif mood == "sad":
    print("Aww, I hope things get better, {{name}}. 💛")
elif mood == "angry":
    print("Take a deep breath, {{name}}. You got this! 🧘")
elif mood == "tired":
    print("Rest is important, {{name}}. Take a break! 😴")
else:
    print(f"I don't know that mood, but I'm sure you're awesome, {{name}}! 🌟")

print(f"\\nGoodbye, {{name}}! Come back anytime!")
""",
    },
    {
        "key": "story_generator",
        "name_en": "AI Story Prompt Generator",
        "name_es": "Generador de Historias",
        "filename": "story_generator.py",
        "content": """\
# AI Story Prompt Generator
# Mix random characters, settings, and plots for story ideas!

import random

characters = [
    "a time-traveling cat",
    "a robot who loves pizza",
    "a dragon afraid of fire",
    "a kid who can fly",
    "a talking fish",
]

settings = [
    "in a haunted castle",
    "on a spaceship headed to Mars",
    "in an underwater city",
    "at a magical school",
    "in a volcano village",
]

plots = [
    "must find a hidden treasure",
    "accidentally becomes president",
    "has to save their best friend",
    "discovers a secret door",
    "enters a cooking contest",
]

print("🎬 STORY GENERATOR 🎬")
print("=" * 40)

for i in range(3):
    char = random.choice(characters)
    setting = random.choice(settings)
    plot = random.choice(plots)
    print(f"\\nStory {{i + 1}}:")
    print(f"  {{char}} {{setting}} {{plot}}.")

print("\\n" + "=" * 40)
print("Pick your favorite and start writing! ✍️")
""",
    },
    {
        "key": "final_project",
        "name_en": "Final Project",
        "name_es": "Proyecto Final",
        "filename": "final_project.py",
        "content": """\
# Final Project
# Combine everything you've learned!
# Ideas: a game, a story, a quiz, an adventure...

import random
import time

def greet():
    name = input("What's your name? ")
    print(f"\\nWelcome, {{name}}! Let's go on an adventure! 🗺️")
    return name

def choose_path():
    print("\\nYou come to a fork in the road.")
    print("  1. Enter the dark cave")
    print("  2. Cross the wobbly bridge")
    print("  3. Climb the tall tree")
    choice = input("What do you choose? (1/2/3): ")
    return choice

def cave():
    print("\\nYou enter the cave and find...")
    time.sleep(1)
    treasure = random.randint(1, 100)
    print(f"A chest with {{treasure}} gold coins! 💰")
    return treasure

def bridge():
    print("\\nYou cross the bridge and meet...")
    time.sleep(1)
    print("A friendly troll who gives you a map! 🗺️")

def tree():
    print("\\nYou climb the tree and see...")
    time.sleep(1)
    print("A beautiful sunset over the mountains! 🌅")

# Main game
name = greet()
choice = choose_path()

if choice == "1":
    gold = cave()
elif choice == "2":
    bridge()
elif choice == "3":
    tree()
else:
    print("\\nYou stand there thinking... and nothing happens. 😅")

print(f"\\nThanks for playing, {{name}}! 🎮")
""",
    },
]


def get_template(key: str) -> dict:
    """Get a template by its key."""
    for t in TEMPLATES:
        if t["key"] == key:
            return t
    return TEMPLATES[0]


def template_names(lang: str = "en") -> list:
    """Get list of (key, display_name) tuples for the Templates menu."""
    return [
        (t["key"], t[f"name_{lang}"] if f"name_{lang}" in t else t["name_en"])
        for t in TEMPLATES
    ]