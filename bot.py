# bot.py
import os
import discord
import random
from typing import Tuple, Optional
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
import match_variables as mvar


# Establish Discord client object
description = 'Age of Empires 4 Discord Bot'
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='/', description=description, intents=intents)

# Get secrets from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


def set_win_conditions() -> str:
    output = []
    for key in mvar.win_conditions.keys():
        if random.choice(mvar.win_conditions[key]):
            output.append(key)

    if output:
        return ", ".join(output)
    else:
        return "Deathmatch"

def get_factors(num: int) -> list:
    factors = []
    for i in range(1, num + 1):
        if num % i == 0:
            factors.append(i)
    return factors[1:]

def initial_to_name(initial: str) -> str:
    """ Convert player initial to player name. """
    for name in mvar.human_players:
        if name[0] == initial:
            return name


def validate_player_input(player_input: str) -> Tuple[bool, Optional[list]]:
    """ Validate player input. """
    # Check if player input is valid
    initials = list(player_input.lower())

    # We only have 4 human players
    if len(input) > 4:
        return False, None
    
    # Only accept the initial of our first names
    for char in input:
        if char not in 'bdjk':
            return False, None

    # Map initials to names        
    players = list(map(initial_to_name, initials))
    return True, players


def pick_teams(players_input: list) -> Tuple[str, int]:
    """ Pick teams for a match. """
    # There are 8 possible teams for a match.  Find out how many open spot there are

    open_slots = 8 - len(players_input)
    print(f"Open slots: {open_slots}")
    # Pick a random number of AI players from the number of open slots
    num_ai_players = random.randint(0, open_slots)
    print(f"Number of AI players: {num_ai_players}")
    # Calculate the total number of players in the match.
    total_num_players = len(players_input) + num_ai_players
    print(f"Total number of players: {total_num_players}")

    # Make sure we have an even number of players for each team
    if total_num_players != 8:
        if (total_num_players % 2) != 0:
            num_ai_players += 1
            total_num_players = len(players_input) + num_ai_players

    print(f"Total number of players after rebalancing: {total_num_players}")
    # Assign civs to human players
    players = {}
    for player in players_input:
        players[player] = random.choice(mvar.civs)
        print(f"{player} is assigned {players[player]}")

    # Assign civs to AI players
    for i in range(1, num_ai_players + 1):
        players[f'AI_Player_{i}'] = random.choice(mvar.civs)
        print(f"AI_Player_{i} is assigned {players[f'AI_Player_{i}']}")


    # Get list of potential number of teams
    num_team_candidates = get_factors(total_num_players)
    print(f"Possible number of teams: {num_team_candidates}")
    # Randomly pick the number of teams
    num_teams = random.choice(num_team_candidates)
    print(f"Number of teams: {num_teams}")

    players_per_team = total_num_players // num_teams
    print(f"Players per team: {players_per_team}")

    #Convert players dict to list
    players = list(players.items())

    teams= {}
    for team_number in range(1, num_teams + 1):
        teams[team_number] = []
        print(f"Assigning Team {team_number} ...")
        for j in range(players_per_team):
            current_pick = players.pop(random.randint(0, len(players) - 1))
            teams[team_number].append(current_pick)

    team_assignments = ''

    spacer = " " * 8
    for team, members in teams.items():
        print (f"Team {team}: {members}")
        team_assignments += f"**Team {team}:**\n{spacer}"
        for member in members:
            team_assignments += f"**{member[0]}:**  *{member[1]}*\n{spacer}"
        team_assignments += "\n    "
    return team_assignments, total_num_players

def generate_random_match(players: Optional[str]) -> str:
    map = random.choice(mvar.maps)
    map_visibility = random.choice(mvar.map_visibility)
    biome = random.choice(mvar.biomes)
    starting_locations = random.choice(mvar.starting_locations)
    starting_age = random.choice(mvar.starting_age)
    starting_resouces = random.choice(mvar.starting_resouces)

    if players is None:
        players = mvar.human_players
    else:
        valid_input, players = validate_player_input(players)

    if not valid_input:
        return "Come on man... Gimme some legit initials.\n\n Try something like this: /wololo BDJ"

    team_assignments, num_players = pick_teams(players)

    map_size = mvar.map_size.copy()
    # Remove smaller maps that are too small for the number of players
    if num_players > 2:
        map_size.remove('Micro')
    if num_players > 4:
        map_size.remove('Small')
        map_size.remove('Medium')
    print(f"Given there are {num_players} the available map size options are: {map_size}")
    map_size = random.choice(map_size)
    

    win_conditions = set_win_conditions()

    match_string = f"""
    WOLOLO!! Random match settings generated!

    **TEAMS**
    =====
    {team_assignments}
    **MAP**
    ===
    **Map:** _{map}_
    **Size:** _{map_size}_
    **Biome:** _{biome}_
    **Visibility:** _{map_visibility}_

    **STARTING SETTINGS**
    ================
    **Starting Locations:** _{starting_locations}_
    **Starting Age:** _{starting_age}_
    **Starting Resources:** _{starting_resouces}_

    **WIN CONDITIONS**
    ==============
    **Win Conditions:** _{win_conditions}_
    """

    return match_string

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def wololo(ctx, players: str = None) -> dict:
    """Generates random match parameters for a given number of players"""
    match_settings = generate_random_match(players)
    await ctx.send(match_settings)

bot.run(TOKEN)