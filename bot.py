#Todo
#Gracefully timeout old interactions
#Allow DB/Saving of modified settings
#Prettier display of data [Embed/Image]

footer_text = 'BU Bot v1.0'
allowed_channels = [] #list of allowed channels
admin_roles = [] #list of admin-level roles (for managing this bot)
banlist = [] #banlist for disallowed users
bot_disabled = False

import discord, asyncio
from discord.ext import commands
from discord.ext.commands import bot

#.env Grabber [Replace this with however you might like to get your token]
import os
from dotenv import load_dotenv
import requests as http

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
#END .env Grabber

#Provided default intent for simplicity, narrow down as you please
Intent = discord.Intents.default()
Intent.message_content = True
bot = commands.Bot(command_prefix='#', intents=Intent)
bot.remove_command('help')

#Permissions
def is_admin(_context):
    return len([role for role in _context.author.roles if role.id in admin_roles]) > 0
def approved(_context):
    check_channel = _context.channel.id in allowed_channels
    check_banlist = not _context.author.id in banlist
    return (check_channel and check_banlist and not bot_disabled) or is_admin(_context)

print('==API Setup==')
#HTTP call code
def API_Call(_url):
    try:
        Request = http.get(_url, timeout = 5)
        if not Request.status_code == 200:
            return f'HTTPError[{Request.status_code}]'
        Request = Request.json()
        if len(Request) == 0:
            return 'NoResults'
        return Request
    except http.Timeout as error:
        return 'Timeout'

npc_data = API_Call('https://game.bones-underground.org/api/npcs/search')
npc_definitions = {
    "Quest":      "NPC",
    "Haircolor":  "NPC",
    "Hairstyle":  "NPC",
    "Barber":     "NPC",
    "Jailbook":   "NPC",
    "Bank":       "NPC",
    "Priest":     "NPC",
    "Law":        "NPC",
    "Guild":      "NPC",
    "Delivery":   "NPC",

    "Skills":     "Skill",
    "Shop":       "Shop",
    "Pet":        "Pet",
    "Aggressive": "Enemy",
    "Passive":    "Enemy",
}

item_data = API_Call('https://game.bones-underground.org/api/items/search')
item_definitions = {
    'Static-None':       "Item",
    'Key-None':          "Item",
    'Currency-None':     "Item",

    'PetSpawn-None':     "PetItem",
    'Potion-None':       "Potion",
    'EffectPotion-None': "Effect",
    'NameChange-None':   "Name",
    'EXPReward-None':    "Exp",
    'Scroll-None':       "Scroll",

    'Buff-Attack':       "Buff",
    'Buff-Defense':      "Buff",

    'Weapon-None':       "Equip",
    'Weapon-Ranged':     "Equip",
    'Shield-None':       "Equip",
    'Shield-Arrows':     "Equip",

    'Armor-None':        "Equip",
    'Gloves-None':       "Equip",
    'Necklace-None':     "Equip",
    'Hat-None':          "Equip",
    'Charm-None':        "Equip",
    'Bracelet-None':     "Equip",
    'Ring-None':         "Equip",
    'Belt-None':         "Equip",
    'Bracer-None':       "Equip",
    'Boots-None':        "Equip",
}
print(f'NPCs: {type(npc_data) == list} | Items: {type(item_data) == list}')
print('==End API Setup==')

def output_data_string_interaction(_id, _type, _source):
    if _source == "npcs":
        npc = [npc for npc in npc_data if _id == npc["id"]][0]
    else:
        item = [item for item in item_data if _id == item["id"]][0]
    match _type:
        #NPCs
        case "locations":
            locations = "\n".join([f'[{loc["id"]:3}] {loc["name"]}' for loc in npc["locations"]])
            if len(locations) > 1800:
                locations = locations[:1800] + "\n[Truncated]"
            return f'**Locations:**```{locations}```'
        case "drops":
            drops = "\n".join([f'{drop["chance"]:5.1f}% {drop["name"]} ({drop["min"]}-{drop["max"]})' for drop in npc["drops"]])
            if len(drops) > 1800:
                drops = drops[:1800] + "\n[Truncated]"
            return f'**Drops:**```{drops}```'
        case "crafts":
            crafts = ''
            for craft in npc["shop_craft"]:
                crafts += f'-- {craft["name"]} --\n'
                for ing in craft["ingredients"]:
                    crafts += f'{ing["amount"]:3} {ing["name"]}\n'
                crafts += '\n'
            
            if len(crafts) > 1800:
                crafts = crafts[:1800] + "\n[Truncated]"
            return f'***{npc["shop_name"]}* Crafts:**```{crafts}```'
        case "trades":
            trades = "\n".join([f'[{trade["id"]:3}] {trade["name"]}  Buy: ${trade["buy"]}  Sell: ${trade["sell"]}' for trade in npc["shop_trade"]])
            if len(trades) > 1800:
                trades = trades[:1800] + "\n[Truncated]"
            return f'***{npc["shop_name"]}* Trades:**```{trades}```'
        case "skills":
            skills = "\n".join([f' {skill["name"]:>16}  ${skill["cost"]:8}  Lvl Req:{skill["level"]}' for skill in npc["skill_learn"]])
            if len(skills) > 1800:
                skills = skills[:1800] + "\n[Truncated]"
            return f'***{npc["skill_name"]}* Spells:**```{skills}```'

        #Items
        case "crafted_by":
            crafted_by = ''
            for source in item["crafted_by"]:
                crafted_by += f'\n[{source["id"]:3}]{source["name"]}\n'
                for ingredient in source["ingredients"]:
                    crafted_by += f'  {ingredient["amount"]} {ingredient["name"]}\n'
            if len(crafted_by) > 1800:
                crafted_by = crafted_by[:1800] + "\n[Truncated]"
            return f'**Crafted by:**```{crafted_by}```'
        case "crafts_into":
            crafts_into = "\n".join([f'[{source["id"]:3}]{source["name"]}' for source in item["crafts_into"]])
            if len(crafts_into) > 1800:
                crafts_into = crafts_into[:1800] + "\n[Truncated]"
            return f'**Crafts Into:**```\n{crafts_into}```'
        case "dropped_by":
            dropped_by = "\n".join([f'[{source["id"]:3}]{source["name"]} {source["chance"]:5.1f}% ({source["min"]}-{source["max"]})' for source in item["dropped_by"]])
            if len(dropped_by) > 1800:
                dropped_by = dropped_by[:1800] + "\n[Truncated]"
            return f'**Dropped By:**```\n{dropped_by}```'
        case "traded_by":
            traded_by = "\n".join([f'[{source["id"]:3}]{source["name"]} Buy: ${source["buy"]} Sell: ${source["sell"]}' for source in item["traded_by"]])
            if len(traded_by) > 1800:
                traded_by = traded_by[:1800] + "\n[Truncated]"
            return f'**Shops:**```\n{traded_by}```'
        case _:
            return 'Invalid Data'

def output_data_string(_entity, _format):
    special = f' *{_entity["special"]}*' if "special" in _entity and not _entity["special"] == "Common" else ''
    match _format:
        #NPCs
        case "Enemy":
            return f'**[{_entity["id"]:3}]{_entity["name"]}**```Experience: {_entity["experience"]:7}\nType: {_entity["type"]}\n\n   Health   Armour\n {_entity["hp"]:8}  {_entity["armor"]:7}\n      Acc    Evade\n  {_entity["accuracy"]:7}  {_entity["evade"]:7}\n            Damage\n   {str(_entity["min_damage"]) + "-" + str(_entity["max_damage"]):>15}```'
        case "Pet":
            return f'**[{_entity["id"]:3}]{_entity["name"]} {_entity["type"]}**```  Attack    Heal\n {_entity["attack_spell_amount"]:7} {_entity["heal_spell_amount"]:7}\n          Damage\n  {str(_entity["min_damage"]) + "-" + str(_entity["max_damage"]):>14}```'
        case "Skill" | "Shop" | "NPC":
            return f'**[{_entity["id"]:3}]{_entity["name"]} {_entity["type"]}**'

        #Items
        case "PetItem":
            return f'**[{_entity["id"]:3}]{_entity["name"]}** {_entity["type"]}{special}```Weight: {_entity["weight"]}\nPet Name: [{_entity["pet"]:3}]{npc_data[_entity["pet"]-1]["name"]}```'
        case "Potion":
            return f'**[{_entity["id"]:3}]{_entity["name"]}** {_entity["type"]}{special}```Weight: {_entity["weight"]}\nHP: {_entity["hp"]}\nTP: {_entity["tp"]}```'
        case "Effect":
            return f'**[{_entity["id"]:3}]{_entity["name"]}** {_entity["type"]}{special}```Weight: {_entity["weight"]}\nEffect ID: {_entity["effect"]}```'
        case "Exp":
            return f'**[{_entity["id"]:3}]{_entity["name"]}** {_entity["type"]}{special}```Weight: {_entity["weight"]}\nExperience: {_entity["reward"]}```'
        case "Scroll":
            return f'**[{_entity["id"]:3}]{_entity["name"]}** {_entity["type"]}{special}```Weight: {_entity["weight"]}\nDestination: {_entity["scroll_map"]} x:{_entity["scroll_x"]} y:{_entity["scroll_y"]}```'
        case "Buff":
            return f'**[{_entity["id"]:3}]{_entity["name"]}** {_entity["type"]}{special}```Weight: {_entity["weight"]}\nHP: {_entity["hp"]}\nTP: {_entity["tp"]}\n\nDuration: {_entity["duration"]} seconds\nBuff Type: {_entity["subtype"]}\nIncrease: {_entity["buff_value"]}%```'
        case "Equip":
            if _entity["subtype"]  == "Ranged":
                output_type = "Ranged Weapon"
            elif _entity["subtype"] == "Arrows":
                output_type = "Arrows"
            else:
                output_type = _entity["type"]

            data = '\n'
            if _entity["type"] == "Armor":
                data += f'Gender: {_entity["gender"]}\n'

            if _entity["min_damage"] + _entity["max_damage"] > 0:
                data += f'Damage: {_entity["min_damage"]}-{_entity["max_damage"]}\n'

            if _entity["type"] == "Weapon":
                if not _entity["subtype"] == "Ranged":
                    data += f'AOE: {_entity["aoe_range"]}\n'
                else:
                    data += f'Range: {_entity["range"]}\n'

            if _entity["hp"] > 0:
                data += f'HP: {_entity["hp"]}\n'
            if _entity["tp"] > 0:
                data += f'TP: {_entity["tp"]}\n'

            if _entity["armor"] > 0:
                data += f'Armour: {_entity["armor"]}\n'
            if _entity["accuracy"] > 0:
                data += f'Accuracy: {_entity["accuracy"]}\n'
            if _entity["evade"] > 0:
                data += f'Evade: {_entity["evade"]}\n'

            if _entity["str"] > 0:
                data += f'Bonus STR: {_entity["str"]}\n'
            if _entity["int"] > 0:
                data += f'Bonus INT: {_entity["int"]}\n'
            if _entity["wis"] > 0:
                data += f'Bonus WIS: {_entity["wis"]}\n'
            if _entity["agi"] > 0:
                data += f'Bonus AGI: {_entity["agi"]}\n'
            if _entity["con"] > 0:
                data += f'Bonus CON: {_entity["con"]}\n'
            if _entity["cha"] > 0:
                data += f'Bonus CHA: {_entity["cha"]}\n'

            if _entity["exp"] > 0:
                data += f'Extra Exp: {_entity["exp"]}%!\n'
            if _entity["drop"] > 0:
                data += f'Extra Drop Chance: {_entity["drop"]}%\n'

            if not _entity["description"] == "":
                data += f'Description: {_entity["description"]}\n'

            return f'**[{_entity["id"]:3}]{_entity["name"]}** {output_type}{special}```Weight: {_entity["weight"]}{data}```'
        case "Item" | "Name":
            return f'**[{_entity["id"]:3}]{_entity["name"]}** {_entity["type"]}{special}```Weight: {_entity["weight"]}```'
        case _:
            return f'**[{_entity["id"]:3}]{_entity["name"]}** {_entity["type"]} - {_format}\nInvalid Data'

class NPCDataView(discord.ui.View):

    def __init__(self, _npcid, _list):
        super().__init__()
        self.npcid = _npcid
        for item in self.children:
            if item.custom_id in _list:
                item.style = discord.ButtonStyle.green
            else:
                item.disabled = True

    @discord.ui.button(label="Locations", style=discord.ButtonStyle.grey, custom_id="locations")
    async def viewlocations(self, interaction: discord.Interaction, button: discord.ui.button):
        await interaction.response.send_message(output_data_string_interaction(self.npcid, 'locations', "npcs"), ephemeral=True)

    @discord.ui.button(label="Drops", style=discord.ButtonStyle.grey, custom_id="drops")
    async def viewdrops(self, interaction: discord.Interaction, button: discord.ui.button):
        await interaction.response.send_message(output_data_string_interaction(self.npcid, 'drops', "npcs"), ephemeral=True)

    @discord.ui.button(label="Crafts", style=discord.ButtonStyle.grey, custom_id="crafts")
    async def viewcrafts(self, interaction: discord.Interaction, button: discord.ui.button):
        await interaction.response.send_message(output_data_string_interaction(self.npcid, 'crafts', "npcs"), ephemeral=True)

    @discord.ui.button(label="Trades", style=discord.ButtonStyle.grey, custom_id="trades")
    async def viewtrades(self, interaction: discord.Interaction, button: discord.ui.button):
        await interaction.response.send_message(output_data_string_interaction(self.npcid, 'trades', "npcs"), ephemeral=True)

    @discord.ui.button(label="Spells", style=discord.ButtonStyle.grey, custom_id="skills")
    async def viewskills(self, interaction: discord.Interaction, button: discord.ui.button):
        await interaction.response.send_message(output_data_string_interaction(self.npcid, 'skills', "npcs"), ephemeral=True)

class ItemDataView(discord.ui.View):

    def __init__(self, _itemid, _list):
        super().__init__()
        self.itemid = _itemid
        for item in self.children:
            if item.custom_id in _list:
                item.style = discord.ButtonStyle.green
            else:
                item.disabled = True

    @discord.ui.button(label="Crafted By", style=discord.ButtonStyle.grey, custom_id="crafted_by")
    async def viewcrafted_by(self, interaction: discord.Interaction, button: discord.ui.button):
        await interaction.response.send_message(output_data_string_interaction(self.itemid, 'crafted_by', "items"), ephemeral=True)

    @discord.ui.button(label="Crafts Into", style=discord.ButtonStyle.grey, custom_id="crafts_into")
    async def viewcrafts_into(self, interaction: discord.Interaction, button: discord.ui.button):
        await interaction.response.send_message(output_data_string_interaction(self.itemid, 'crafts_into', "items"), ephemeral=True)

    @discord.ui.button(label="Dropped", style=discord.ButtonStyle.grey, custom_id="dropped_by")
    async def viewdropped_by(self, interaction: discord.Interaction, button: discord.ui.button):
        await interaction.response.send_message(output_data_string_interaction(self.itemid, 'dropped_by', "items"), ephemeral=True)

    @discord.ui.button(label="Traded", style=discord.ButtonStyle.grey, custom_id="traded_by")
    async def viewtraded_by(self, interaction: discord.Interaction, button: discord.ui.button):
        await interaction.response.send_message(output_data_string_interaction(self.itemid, 'traded_by', "items"), ephemeral=True)

@bot.command(pass_context=True)
async def online(ctx, data = None):
    if not approved(ctx):
        return
    online_list = API_Call('https://game.bones-underground.org/api/online')

    if not type(online_list) == list:
        await ctx.send(f'Lookup Failed.\nError reason: {online_list}.')
        return

    if not data == None: #Guild Entered
        data = data[:3].upper()
        online_list = [player for player in online_list if player['guild_tag'].upper() == data]
        if len(online_list) == 0:
            await ctx.send(f'No `[{data}]` players found.\nMaybe try searching without a Guild.')
            return

    if len(online_list) == 0:
        await ctx.send('No one is Online?')
        return

    parsed_list = sorted([player["name"] for player in online_list])

    output = 'Players Online:```' if not data else f'{data} Members Online:```'
    for index in range(len(parsed_list)):
        if index % 4 == 0:
            output += '\n'
        output += f'{parsed_list[index]:>13}'
    output += '```'
    await ctx.send(output)

@bot.command(pass_context=True)
async def item(ctx, data = None):
    if not approved(ctx):
        return
    if data == None:
        await ctx.send('Invalid Command. Usage: `#item [ID / Name]`')
        return
    
    data = ctx.message.content[6:].lower()
    search_name = not data.isnumeric()
    if not type(item_data) == list:
        await ctx.send(f'Lookup Failed.\nError reason: {item_data}.')
        return

    if search_name:
        item_filter = [item for item in item_data if data in item["name"].lower()]
    else:
        item_filter = [item for item in item_data if data == str(item["id"])]

    if len(item_filter) == 0:
        await ctx.send('Nothing found.')
    elif len(item_filter) == 1:
        item = item_filter[0]

        show_list = []
        if 'crafted_by_size' in item and item["crafted_by_size"] > 0:
            show_list.append('crafted_by')
        if 'crafts_into_size' in item and item["crafts_into_size"] > 0:
            show_list.append('crafts_into')
        if 'dropped_by_size' in item and item["dropped_by_size"] > 0:
            show_list.append('dropped_by')
        if 'traded_by_size' in item and item["traded_by_size"] > 0:
            show_list.append('traded_by')

        if len(show_list) > 0:
            view = ItemDataView(item["id"], show_list)
            await ctx.send(output_data_string(item, item_definitions[f'{item["type"]}-{item["subtype"]}']), view=view)
        else:
            await ctx.send(output_data_string(item, item_definitions[f'{item["type"]}-{item["subtype"]}']))
    else:
        await ctx.send('```' + '\n'.join([f'[{npc["id"]:3}]{npc["name"]}' for npc in item_filter])[:1900] + '```')

@bot.command(pass_context=True)
async def npc(ctx, data = None):
    if not approved(ctx):
        return
    if data == None:
        await ctx.send('Invalid Command. Usage: `#npc [ID / Name]`')
        return
    
    data = ctx.message.content[5:].lower()
    search_name = not data.isnumeric()
    
    if not type(npc_data) == list:
        await ctx.send(f'Lookup Failed.\nError reason: {npc_data}.')
        return

    if search_name:
        npc_filter = [npc for npc in npc_data if data in npc["name"].lower() and not "Placeholder" in npc["name"]]
    else:
        npc_filter = [npc for npc in npc_data if data == str(npc["id"])]

    if len(npc_filter) == 0:
        await ctx.send('Nothing found.')
    elif len(npc_filter) == 1:
        npc = npc_filter[0]

        show_list = []
        if 'locations_size' in npc and npc["locations_size"] > 0:
            show_list.append('locations')
        if 'drops_size' in npc and npc["drops_size"] > 0:
            show_list.append('drops')
        if 'shop_craft_size' in npc and npc["shop_craft_size"] > 0:
            show_list.append('crafts')
        if 'shop_trade_size' in npc and npc["shop_trade_size"] > 0:
            show_list.append('trades')
        if 'skill_learn_size' in npc and npc["skill_learn_size"] > 0:
            show_list.append('skills')

        if len(show_list) > 0:
            view = NPCDataView(npc["id"], show_list)
            await ctx.send(output_data_string(npc, npc_definitions[npc["type"]]), view=view)
        else:
            await ctx.send(output_data_string(npc, npc_definitions[npc["type"]]))
    else:
        await ctx.send('```' + '\n'.join([f'[{npc["id"]:3}]{npc["name"]}' for npc in npc_filter])[:1900] + '```')

@bot.command(pass_context=True)
async def test(ctx):
    if not approved(ctx):
        return
    if is_admin(ctx):
        await ctx.send(ctx.message.content)

@bot.command(pass_context=True)
async def help(ctx):
    if not approved(ctx):
        return
    embed = discord.Embed(
        color = discord.Color.green()
    )
    embed.set_author(name='Command List (Help)')
    embed.set_thumbnail(url='https://game.bones-underground.org/api/gfx/npcs?id=424')
    embed.add_field(name='#Help', value='Open this help menu.', inline=False)
    embed.add_field(name='#Online', value='Tells you all the online players when the command was ran.', inline=False)
    embed.add_field(name='#Online [Guild]', value='Tells you all the online players of a particular guild when the command was ran.', inline=False)
    embed.add_field(name='#NPC [ID / Name]', value='Searches for NPCs with the given ID or Name.', inline=False)
    embed.add_field(name='#Item [ID / Name]', value='Searches for Items with the given ID or Name.', inline=False)
    embed.set_footer(text=footer_text + ' - Written by Mikkul')
    await ctx.send(embed=embed)

#management
@bot.command(pass_context=True)
async def enable(ctx):
    if not is_admin(ctx):
        return
    global bot_disabled
    bot_disabled = False
    await ctx.send('Bot Enabled')

@bot.command(pass_context=True)
async def disable(ctx):
    if not is_admin(ctx):
        return
    global bot_disabled
    bot_disabled = True
    await ctx.send('Bot Disabled')

@bot.command(pass_context=True)
async def reload(ctx):
    if not is_admin(ctx):
        return
    
    npc_data = API_Call('https://game.bones-underground.org/api/npcs/search')
    item_data = API_Call('https://game.bones-underground.org/api/items/search')
    print('Reloaded API calls')

@bot.command(pass_context=True)
async def blacklist(ctx, data=0):
    if not is_admin(ctx):
        return
    global banlist
    banlist.append(data)

@bot.command(pass_context=True)
async def whitelist(ctx, data=0):
    if not is_admin(ctx):
        return
    global banlist
    banlist.remove(data)

bot.run(TOKEN)
