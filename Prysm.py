#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Prysm.py
#
#  Copyright 2019  Riven Skaye / FokjeM
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
import os
import subprocess
import sys
import json
import discord
import discord.ext.commands

with open("Prysm.json", "r") as prysmjson:
    base_info = json.load(prysmjson)
guilds = base_info["Guilds"]
bot = discord.ext.commands.Bot(max_messages=0, fetch_offline_members=False, command_prefix=";")
print(os.getcwd())

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if str(guild.id) in guilds.keys():
            print("Guild found: %s" % guilds[str(guild.id)])
        else:
            print("New guild! %s" % guild.name)
            guilds[str(guild.id)] = guild.name
            print(guilds)
    # Once the loop's done, we save all servers we're in now.
    saveJSON("Prysm.json", base_info)

# async def initMessage(guild, channel):
@bot.event
async def on_command_error(ctx, err):
    if isinstance(err.original, discord.ext.commands.MissingPermissions):
        ctx.channel.send("Sorry %s, it seems you lack the permission %s" % (ctx.author.mention(), ", ".join(err.original.missing_perms)))

@bot.command(name="restart", help="Pulls in latest git code and restarts to load it in. Admins only!", pass_context=True)
@discord.ext.commands.has_permissions(administrator=True)
async def cmd_restart(ctx):
    saveJSON("Prysm.json", base_info)
    subprocess.Popen(["git", "pull"])
    print("bot restarting, if you read this it works!!")
    await bot.close()
    os.execv(sys.executable, ["python"]+sys.argv)

@bot.command(name="exit", help="Calls all closing methods on the bot, shutting it down. Admins only!", pass_context=True)
@discord.ext.commands.has_permissions(administrator=True)
async def cmd_exit(ctx):
    await ctx.channel.send("Prysm off, glad to be of service!")
    await bot_exit(0)

async def bot_exit(status=0):
    saveJSON("Prysm.json", base_info)
    await bot.close()
    exit(status)

def saveJSON(jsonFile, data):
    with open(jsonFile, "w") as jsonHandle:
        json.dump(data, jsonHandle, indent=4)

bot.run(base_info["Token"])
