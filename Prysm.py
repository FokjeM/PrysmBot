#!/usr/bin/env python

import os
import subprocess
import sys
import json
import discord
import discord.ext.commands

try :
    with open("Prysm.json", "r") as prysmjson:
        base_info = json.load(prysmjson)
        print(base_info["Token"])
        assert (len(base_info["Token"]) > 0), "No token given! Fix your Prysm.json!"
except FileNotFoundError:
    with open("Prysm.json", "w+") as prysmjson:
        prysmjson.write("{\r\n    \"Token\": \"\",\r\n    \"Guilds\": {}\r\n}")
        print("There was no Prysm.py found; It was created, now add the Token for the bot.")
    exit(1)
except AssertionError:
    print("No token given! Fix your Prysm.json!")
    exit(1)

guilds = base_info["Guilds"]
bot = discord.ext.commands.Bot(max_messages=0, fetch_offline_members=False, command_prefix=";")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(name="the boss", type=discord.ActivityType.listening))
    for guild in bot.guilds:
        if str(guild.id) not in guilds.keys():
            guilds[str(guild.id)] = guild.name
        if os.path.isfile(str("Guilds/"+str(guild.id)+".json")):
            with open(str("Guilds/"+str(guild.id)+".json")) as gjson:
                g = json.load(gjson)
                if len(str(g["Init"])) > 0:
                    e = discord.Embed(title="Prysm started", description="This is a message to let all users know Prysm is online and receptive for input.", colour=discord.Colour.from_rgb(172, 85, 172))
                    await bot.get_channel(g["Init"]).send(embed=e)
    # Once the loop's done, we save all servers we're in now.
    saveJSON("Prysm.json", base_info)

# async def initMessage(guild, channel):
@bot.event
async def on_command_error(ctx, err):
    if isinstance(err, discord.ext.commands.MissingPermissions):
        await ctx.channel.send("Sorry %s, it seems you lack the permission %s" % (ctx.author.mention(), err.missing_perms))

@bot.command(name="setInit", help="Sets what channel to send a message signaling the bot is online. Requires the 'manage channels' permission.", pass_context=True)
@discord.ext.commands.has_permissions(manage_channels=True)
async def cmd_setInit(ctx):
    guildfile = str("Guilds/"+str(ctx.guild.id)+".json")
    if not os.path.isfile(guildfile):
        with open(guildfile, "w+") as f:
            f.write("{}")
    with open(guildfile, "r") as gf:
        channel = json.load(gf)
    channel["Init"] = ctx.channel.id
    saveJSON(guildfile, channel)
    e = discord.Embed(title="Registered Init Channel", description="This message will now be used to notify of Prysm's online status.", colour=discord.Colour.from_rgb(172, 85, 172))
    await bot.get_channel(channel["Init"]).send(embed=e)

@bot.command(name="restart", help="Pulls in latest git code and restarts to load it in. Admins only!", pass_context=True)
@discord.ext.commands.has_permissions(administrator=True)
async def cmd_restart(ctx):
    saveJSON("Prysm.json", base_info)
    await ctx.channel.send("I'm now updating and restarting. As soon as I'm back, you can use me again!")
    subprocess.Popen(["git", "pull"]).wait()
    os.execv(sys.executable, ["python"]+sys.argv)

@bot.command(name="exit", help="Calls all closing methods on the bot, shutting it down. Admins only!", pass_context=True)
@discord.ext.commands.has_permissions(administrator=True)
async def cmd_exit(ctx):
    await ctx.channel.send("Prysm off, glad to be of service!")
    await bot_exit()

async def bot_exit(status=0):
    saveJSON("Prysm.json", base_info)
    await bot.close()

def saveJSON(jsonFile, data):
    with open(jsonFile, "w") as jsonHandle:
        json.dump(data, jsonHandle, indent=4)

bot.run(base_info["Token"])
