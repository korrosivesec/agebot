# bot.py
import os
import discord
import random
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
from match_variables import *


# Establish Discord client object
description = 'Age of Empires 4 Discord Bot'
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='/', description=description, intents=intents)

# Get secrets from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


def set_win_conditions() -> list:
    output = []
    for key in win_conditions.keys:
        if random.choice(win_conditions[key]):
            output.append(key)
    return output

def get_factors(num: int) -> list:
    factors = []
    for i in range(1, num):
        if num % i == 0:
            factors.append(i)
    return factors[1:-1]

def pick_teams() -> str:
    """ Pick teams for a match. """
    # There are 8 possible teams for a match.  Find out how many open spot there are
    open_slots = 8 - len(human_players)
    # Pick a random number of AI players from the number of open slots
    num_ai_players = random.randint(0, open_slots)
    # Calculate the total number of players in the match.
    total_num_players = len(human_players) + num_ai_players

    # Make sure we have an even number of players for each team
    if total_num_players != 8:
        if (total_num_players % 2) != 0:
            num_ai_players += 1
            total_num_players = len(human_players) + num_ai_players

    # Assign civs to human players
    players = {}
    for player in human_players:
        players[player] = random.choice(civs)

    # Assign civs to AI players
    for i in range(num_ai_players):
        players[f'AI_Player_{i}'] = random.choice(civs)

    # Get list of potential number of teams
    num_team_candidates = get_factors(total_num_players)
    # Randomly pick the number of teams
    num_teams = random.choice(num_team_candidates)

    players_per_team = total_num_players // num_teams

    teams= {}
    for i in range(num_teams):
        teams[i] = []
        for j in range(players_per_team):
            teams[i].append(players.pop(random.randint(0, len(players) - 1)))

    team_assignments = ''

    for team, members in teams.items():
        team_assignments += f'Team {team}: {members}\n'
    return team_assignments

def generate_random_match(num_players: int) -> str:
    map = random.choice(maps)
    map_size = random.choice(map_size)
    map_visibility = random.choice(map_visibility)
    biome = random.choice(biomes)
    starting_locations = random.choice(starting_locations)
    starting_age = random.choices(starting_age)
    starting_resouces = random.choices(starting_resouces)
    team_assignments = pick_teams(num_players)
    

    win_conditions = set_win_conditions()

    match_string = f"""
    **TEAMS**
    =====
    {team_assignments}

    **MAP**
    ===
    Map: _{map}_
    Size: _{map_size}_
    Biome: _{biome}_
    Visibility: _{map_visibility}_

    **STARTING SETTINGS**
    =================
    Starting Locations: _{starting_locations}_
    Starting Age: _{starting_age}_
    Starting Resources: _{starting_resouces}_

    **WIN CONDITIONS**
    ==============
    Win Conditions: _{win_conditions}_
    """

    return match_string

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def wololo(ctx, num_players: int) -> dict:
    """Generates random match parameters for a given number of players"""
    match_settings = generate_random_match(num_players)
    await ctx.send(match_settings)

bot.run(TOKEN)