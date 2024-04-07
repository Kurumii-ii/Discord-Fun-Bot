import discord
from discord.ext import commands, tasks
import requests
from colorama import Fore
import asyncio
import os
import socket
from datetime import datetime
import shutil
from screenshotone import Client, TakeOptions
import socket
import time
import threading
import re
import json
import random
import openai
from discord import SyncWebhook
from queue import Queue


def getConfig():
    Config = "config.json"
    with open(Config) as Config_Json:
        Data = json.load(Config_Json)
    return Data


def prefix():
    return getConfig()["Prefix"]


async def get_prefix(client, message):
    return getConfig()["Prefix"]


screenshot = Client("ScreenShotOne Api Key Here", "ScreenShotOne Secret Key Here")

# Do Not Touch
log_channel = False
fcid = 0
tcid = 0
LOGWEB = ""

token = getConfig()["Token"]
uptime = None
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(
    command_prefix=get_prefix,
    help_command=None,
    intents=intents,
    chunk_guilds_at_startup=False,
)

client.launch_time = datetime.now()

Deleted_Msgs_Json = "DeletedMessages.json"
DeletedMessageIndex = 0
DeletedMessageServer = []
DeletedMessageChannel = []

Edited_Msgs_Json = "EditedMessages.json"


def log_deleted_msgs(guildID, guildName, channelID, channelName):
    try:
        with open(Deleted_Msgs_Json) as file:
            DeletedMsgs = json.load(file)
        DeletedMsgs[str(guildID)]["Data"]
    except:
        with open(Deleted_Msgs_Json) as file:
            DeletedMsgs = json.load(file)

        DeletedMsgs[guildID] = {"ServerName": guildName, "Data": {}}

        with open(Deleted_Msgs_Json, "r+") as json_file:
            json.dump(DeletedMsgs, json_file, indent=4, separators=(",", ": "))

    try:
        with open(Deleted_Msgs_Json) as file:
            DeletedMsgs = json.load(file)
        DeletedMsgs[str(guildID)]["Data"][str(channelID)]
    except:
        with open(Deleted_Msgs_Json) as file:
            DeletedMsgs = json.load(file)

        DeletedMsgs[str(guildID)]["Data"].update(
            {
                channelID: {
                    "ChannelName": channelName,
                    "Author": [],
                    "Message": [],
                    "Date": [],
                    "Content_type": [],
                    "Attachment_message": [],
                }
            }
        )

        with open(Deleted_Msgs_Json, "r+") as json_file:
            json.dump(DeletedMsgs, json_file, indent=4, separators=(",", ": "))


def log_edited_messages(guildID, guildName, channelID, channelName):
    try:
        with open(Edited_Msgs_Json) as file:
            EditedMsgs = json.load(file)
        EditedMsgs[str(guildID)]["Data"]
    except:
        with open(Edited_Msgs_Json) as file:
            EditedMsgs = json.load(file)

        EditedMsgs[guildID] = {"ServerName": guildName, "Data": {}}

        with open(Edited_Msgs_Json, "r+") as json_file:
            json.dump(EditedMsgs, json_file, indent=4, separators=(",", ": "))

    try:
        with open(Edited_Msgs_Json) as file:
            EditedMsgs = json.load(file)
        EditedMsgs[str(guildID)]["Data"][str(channelID)]
    except:
        with open(Edited_Msgs_Json) as file:
            EditedMsgs = json.load(file)

        EditedMsgs[str(guildID)]["Data"].update(
            {
                channelID: {
                    "channelName": channelName,
                    "Author": [],
                    "beforeEditMsg": [],
                    "afterEditMsg": [],
                    "Date": [],
                }
            }
        )

        with open(Edited_Msgs_Json, "r+") as json_file:
            json.dump(EditedMsgs, json_file, indent=4, separators=(",", ": "))


@tasks.loop(seconds=60)
async def update_status():
    textlist = [
        f"Discord Multi-Purpose Bot | {client.user}",
        f"{client.user} Is Watching {len(client.guilds)} Servers",
        f"Hello, My Name Is {client.user}",
    ]
    randText = random.choice(textlist)
    activity = discord.Game(name=f"{randText} | {prefix()}help")
    await client.change_presence(status=discord.Status.idle, activity=activity)


@client.event
async def on_ready():
    os.system("clear")
    print("[ + ] " + Fore.GREEN + f"{client.user} Is Ready!" + Fore.RESET)
    print("\n[ + ] " + Fore.GREEN + f"Bot Prefix Is {prefix()}" + Fore.RESET)
    print(
        "\n[ + ] "
        + Fore.GREEN
        + f"Bot Is Online In {len(client.guilds)} Servers"
        + Fore.RESET
    )
    for guilds in client.guilds:
        print(
            "\n[ + ] "
            + Fore.MAGENTA
            + "Server Name : "
            + guilds.name
            + Fore.RESET
            + "\n~~~~> "
            + Fore.MAGENTA
            + "Server ID : "
            + str(guilds.id)
            + Fore.RESET
        )
    update_status.start()


@client.event
async def on_message(message):
    global log_channel
    fchannel = client.get_channel(fcid)
    tchannel = client.get_channel(tcid)

    if log_channel:
        hooks = SyncWebhook.from_url(LOGWEB)
        if (
            message.channel == fchannel
            and message.author.id != client.user.id
            and not message.attachments
        ):
            try:
                hooks.send(
                    content=f"[ ~ ] {message.content}\n(User ID : {message.author.id})",
                    username=message.author.name,
                    avatar_url=message.author.avatar.url,
                )
            except:
                hooks.send(
                    content=f"[ ~ ] {message.content}\n(User ID : {message.author.id})",
                    username=message.author.name,
                )
        if (
            message.channel == fchannel
            and message.author.id != client.user.id
            and message.attachments
        ):
            for attachment in message.attachments:
                try:
                    hooks.send(
                        content=f"[ ~ ] {message.content} {attachment}\n(User ID : {message.author.id})",
                        username=message.author.name,
                        avatar_url=message.author.avatar.url,
                    )
                except:
                    hooks.send(
                        content=f"[ ~ ] {message.content} {attachment}\n(User ID : {message.author.id})",
                        username=message.author.name,
                    )
        if (
            message.author != client.user
            and message.channel.id == tchannel.id
            and "[ ~ ]" not in message.content
            and not message.attachments
        ):
            await fchannel.send(message.content)
        if (
            message.author != client.user
            and message.channel.id == tchannel.id
            and "[ ~ ]" not in message.content
            and message.attachments
        ):
            for attachment in message.attachments:
                await fchannel.send(f"{message.content} {attachment}")
    else:
        pass

    if (
        message.attachments
        and str(message.channel.id) == getConfig()["attachmentsChannel"]
    ):
        global DeletedMessageIndex
        attachments = message.attachments
        for attachment in attachments:

            with open(Deleted_Msgs_Json) as file:
                DeletedMsgs = json.load(file)

            DeletedMsgs[str(DeletedMessageServer[DeletedMessageIndex])]["Data"][
                str(DeletedMessageChannel[DeletedMessageIndex])
            ]["Message"].append(attachment.url)

            with open(Deleted_Msgs_Json, "r+") as json_file:
                json.dump(DeletedMsgs, json_file, indent=4, separators=(",", ": "))

            DeletedMessageIndex += 1
            await asyncio.sleep(3)

    await client.process_commands(message)


@client.event
async def on_message_delete(message):
    date = datetime.today().strftime("%Y-%m-%d | %H:%M:%S")
    guildID = message.guild.id
    guildName = message.guild.name
    channelID = message.channel.id
    channelName = message.channel.name
    authorName = message.author.name
    deletedContent = message.content

    if not message.attachments and message.author.id != client.user.id:
        log_deleted_msgs(guildID, guildName, channelID, channelName)

        with open(Deleted_Msgs_Json) as file:
            DeletedMsgs = json.load(file)

        DeletedMsgs[str(message.guild.id)]["Data"][str(message.channel.id)][
            "Author"
        ].append(authorName)
        DeletedMsgs[str(message.guild.id)]["Data"][str(message.channel.id)][
            "Message"
        ].append(deletedContent)
        DeletedMsgs[str(message.guild.id)]["Data"][str(message.channel.id)][
            "Date"
        ].append(date)
        DeletedMsgs[str(message.guild.id)]["Data"][str(message.channel.id)][
            "Content_type"
        ].append("text")
        DeletedMsgs[str(message.guild.id)]["Data"][str(message.channel.id)][
            "Attachment_message"
        ].append("")

        with open(Deleted_Msgs_Json, "r+") as json_file:
            json.dump(DeletedMsgs, json_file, indent=4, separators=(",", ": "))

    if message.attachments and message.author.id != client.user.id:
        log_deleted_msgs(guildID, guildName, channelID, channelName)

        attachments = message.attachments

        for attachment in attachments:

            with open(Deleted_Msgs_Json) as file:
                DeletedMsgs = json.load(file)

            DeletedMsgs[str(message.guild.id)]["Data"][str(message.channel.id)][
                "Author"
            ].append(authorName)
            DeletedMsgs[str(message.guild.id)]["Data"][str(message.channel.id)][
                "Attachment_message"
            ].append(deletedContent)
            DeletedMsgs[str(message.guild.id)]["Data"][str(message.channel.id)][
                "Date"
            ].append(date)
            DeletedMsgs[str(message.guild.id)]["Data"][str(message.channel.id)][
                "Content_type"
            ].append("attachment")

            with open(Deleted_Msgs_Json, "r+") as json_file:
                json.dump(DeletedMsgs, json_file, indent=4, separators=(",", ": "))

            DeletedMessageServer.append(guildID)
            DeletedMessageChannel.append(channelID)
            await attachment.save(attachment.filename)
            saveto = client.get_channel(int(getConfig()["attachmentsChannel"]))
            file = discord.File(attachment.filename)
            await saveto.send(
                file=file, content=f"By {authorName} In {guildName} [#{channelName}]"
            )
            os.remove(attachment.filename)
            await asyncio.sleep(3)


@client.event
async def on_bulk_message_delete(message):
    for msg in list(message):
        date = datetime.today().strftime("%Y-%m-%d | %H:%M:%S")
        guildID = msg.guild.id
        guildName = msg.guild.name
        channelID = msg.channel.id
        channelName = msg.channel.name
        authorID = msg.author.id
        authorName = msg.author.name
        deletedContent = msg.content
        attachments = msg.attachments

        if not attachments and authorID != client.user.id:
            log_deleted_msgs(guildID, guildName, channelID, channelName)

            with open(Deleted_Msgs_Json) as file:
                DeletedMsgs = json.load(file)

            DeletedMsgs[str(guildID)]["Data"][str(channelID)]["Author"].append(
                authorName
            )
            DeletedMsgs[str(guildID)]["Data"][str(channelID)]["Message"].append(
                deletedContent
            )
            DeletedMsgs[str(guildID)]["Data"][str(channelID)]["Date"].append(date)
            DeletedMsgs[str(guildID)]["Data"][str(channelID)]["Content_type"].append(
                "text"
            )
            DeletedMsgs[str(guildID)]["Data"][str(channelID)][
                "Attachment_message"
            ].append("")

            with open(Deleted_Msgs_Json, "r+") as json_file:
                json.dump(DeletedMsgs, json_file, indent=4, separators=(",", ": "))

        if attachments and authorID != client.user.id:
            log_deleted_msgs(guildID, guildName, channelID, channelName)

            for attachment in attachments:

                with open(Deleted_Msgs_Json) as file:
                    DeletedMsgs = json.load(file)

                DeletedMsgs[str(guildID)]["Data"][str(channelID)]["Author"].append(
                    authorName
                )
                DeletedMsgs[str(guildID)]["Data"][str(channelID)][
                    "Attachment_message"
                ].append(deletedContent)
                DeletedMsgs[str(guildID)]["Data"][str(channelID)]["Date"].append(date)
                DeletedMsgs[str(guildID)]["Data"][str(channelID)][
                    "Content_type"
                ].append("attachment")

                with open(Deleted_Msgs_Json, "r+") as json_file:
                    json.dump(DeletedMsgs, json_file, indent=4, separators=(",", ": "))

                DeletedMessageServer.append(guildID)
                DeletedMessageChannel.append(channelID)
                await attachment.save(attachment.filename)
                saveto = client.get_channel(int(getConfig()["attachmentsChannel"]))
                file = discord.File(attachment.filename)
                await saveto.send(
                    file=file,
                    content=f"By {authorName} In {guildName} [#{channelName}]",
                )
                os.remove(attachment.filename)
                await asyncio.sleep(3)


@client.event
async def on_message_edit(before, after):
    date = datetime.today().strftime("%Y-%m-%d | %H:%M:%S")
    guildID = before.guild.id
    guildName = before.guild.name
    channelID = before.channel.id
    channelName = before.channel.name
    authorName = before.author.name
    beforeContent = before.content
    afterContent = after.content

    if before.author.id != client.user.id:
        log_edited_messages(guildID, guildName, channelID, channelName)

        with open(Edited_Msgs_Json) as file:
            EditedMsgs = json.load(file)

        EditedMsgs[str(guildID)]["Data"][str(channelID)]["Author"].append(authorName)
        EditedMsgs[str(guildID)]["Data"][str(channelID)]["beforeEditMsg"].append(
            beforeContent
        )
        EditedMsgs[str(guildID)]["Data"][str(channelID)]["afterEditMsg"].append(
            afterContent
        )
        EditedMsgs[str(guildID)]["Data"][str(channelID)]["Date"].append(date)

        with open(Edited_Msgs_Json, "r+") as json_file:
            json.dump(EditedMsgs, json_file, indent=4, separators=(",", ": "))


@client.event
async def on_command(ctx):
    user = ctx.author
    avatar = ctx.author.avatar.url
    command = ctx.command
    server = ctx.guild.name
    channel = client.get_channel(int(getConfig()["logChannel"]))
    embed = discord.Embed(
        title=f"**{user}**",
        color=discord.Colour.random(),
        timestamp=datetime.now(),
    )
    embed.add_field(
        name=f"**Command : {command}**", value=f"{ctx.message.content}", inline=False
    )
    embed.add_field(
        name=f"Channel Name : {ctx.channel}", value=f"{ctx.channel.id}", inline=False
    )
    embed.set_footer(text=f"{server}")
    embed.set_thumbnail(url=f"{avatar}")
    await channel.send(embed=embed)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title=f"**Command Not Found!**",
            description=f"Type {prefix()}help For Command List.",
            color=discord.Color.red(),
            timestamp=ctx.message.created_at,
        )
        await ctx.send(embed=embed)

    if isinstance(error, commands.BadArgument):
        await ctx.send(
            f"Usage:\n{prefix()}snipe <Number Ex. 1>\n{prefix()}snipeedit <Number Ex.1>"
        )


@client.command()
@commands.is_owner()
async def clear(ctx, type=None):

    clearJson = {}

    if type == None:
        await ctx.send(
            f"{prefix()}clear 1 ( To Clear All Logged Deleted Messages )\n{prefix()}clear 2 ( To Clear All Logged Edited Messages )"
        )

    if type == "1":
        try:
            with open(Deleted_Msgs_Json, "w") as json_file:
                json.dump(clearJson, json_file, indent=4, separators=(",", ": "))
            await ctx.send(f"Cleared {Deleted_Msgs_Json} Successfully")
        except Exception as e:
            await ctx.send(e)

    if type == "2":
        try:
            with open(Edited_Msgs_Json, "w") as json_file:
                json.dump(clearJson, json_file, indent=4, separators=(",", ": "))
            await ctx.send(f"Cleared {Edited_Msgs_Json} Successfully")
        except Exception as e:
            await ctx.send(e)


@client.command()
async def snipe(ctx, index: int = None):
    if str(ctx.author.id) in getConfig()["SnipeUser"]:

        serverID = ctx.guild.id
        channelID = ctx.channel.id

        try:
            with open(Deleted_Msgs_Json) as file:
                DeletedMsgs = json.load(file)
            totalmsg = len(
                DeletedMsgs[str(serverID)]["Data"][str(channelID)]["Message"]
            )
        except:
            await ctx.send(f"There Is No Deleted Message In #{ctx.channel.name}")
            return

        if index == None:
            index = totalmsg - 1
        else:
            index = index - 1

        try:
            with open(Deleted_Msgs_Json) as file:
                checkIndex = json.load(file)
            checkIndex[str(serverID)]["Data"][str(channelID)]["Message"][index]
        except Exception as e:
            await ctx.send(e)
            return

        msg = DeletedMsgs[str(serverID)]["Data"][str(channelID)]["Message"][index]
        author = DeletedMsgs[str(serverID)]["Data"][str(channelID)]["Author"][index]
        date = DeletedMsgs[str(serverID)]["Data"][str(channelID)]["Date"][index]
        attachment_msg = DeletedMsgs[str(serverID)]["Data"][str(channelID)][
            "Attachment_message"
        ][index]

        async def text_response():
            embed = discord.Embed(
                title=f"Currently Viewing {index + 1}/{totalmsg} Of Deleted Messages In #{ctx.channel.name}",
                description=msg,
                color=discord.Color.red(),
            )
            embed.set_footer(text=f"Deleted By {author} [ {date} ]")
            await ctx.send(embed=embed)

        async def attachment_response():
            embed = discord.Embed(
                title=f"Currently Viewing {index + 1}/{totalmsg} Of Deleted Attachments In #{ctx.channel.name}",
                description=attachment_msg,
                color=discord.Color.red(),
            )
            embed.set_footer(text=f"Deleted By {author} [ {date} ]")
            embed.add_field(
                name=f"Attachment Name : {msg}",
                value=f"Attachment URL : [Download](<{msg}>)",
                inline=False,
            )
            embed.set_image(url=msg)
            await ctx.send(embed=embed)

        if (
            DeletedMsgs[str(serverID)]["Data"][str(channelID)]["Content_type"][index]
            == "text"
        ):
            await text_response()

        if (
            DeletedMsgs[str(serverID)]["Data"][str(channelID)]["Content_type"][index]
            == "attachment"
        ):
            await attachment_response()
    else:
        await ctx.reply("No Permission")


@client.command()
async def snipeedit(ctx, index: int = None):
    if str(ctx.author.id) in getConfig()["SnipeUser"]:

        serverID = ctx.guild.id
        channelID = ctx.channel.id

        try:
            with open(Edited_Msgs_Json) as file:
                EditedMsgs = json.load(file)
            totalmsg = len(
                EditedMsgs[str(serverID)]["Data"][str(channelID)]["beforeEditMsg"]
            )
        except:
            await ctx.send(f"There Is No Edited Message In #{ctx.channel.name}")
            return

        if index == None:
            index = totalmsg - 1
        else:
            index = index - 1

        try:
            with open(Edited_Msgs_Json) as file:
                checkIndex = json.load(file)
            checkIndex[str(serverID)]["Data"][str(channelID)]["beforeEditMsg"][index]
        except Exception as e:
            await ctx.send(e)
            return

        author = EditedMsgs[str(serverID)]["Data"][str(channelID)]["Author"][index]
        beforemsg = EditedMsgs[str(serverID)]["Data"][str(channelID)]["beforeEditMsg"][
            index
        ]
        aftermsg = EditedMsgs[str(serverID)]["Data"][str(channelID)]["afterEditMsg"][
            index
        ]
        date = EditedMsgs[str(serverID)]["Data"][str(channelID)]["Date"][index]

        async def edited_response():
            embed = discord.Embed(
                title=f"Currently Viewing {index + 1}/{totalmsg} Of Edited Messages In #{ctx.channel.name}",
                color=discord.Color.red(),
            )
            embed.set_footer(text=f"Edited By {author} [ {date} ]")
            embed.add_field(
                name="Message : Before Edited", value=beforemsg, inline=False
            )
            embed.add_field(name="Message : After Edited", value=aftermsg, inline=False)
            await ctx.send(embed=embed)

        await edited_response()
    else:
        await ctx.reply("No Permission")


@client.command()
@commands.is_owner()
async def settings(ctx, mode=None, key=None, value=None, type=None):
    Config = "config.json"

    def get_size(file_path, unit="bytes"):
        file_size = os.path.getsize(file_path)
        exponents_map = {"bytes": 0, "kb": 1, "mb": 2, "gb": 3}
        if unit not in exponents_map:
            raise ValueError("Select From 'bytes', 'kb', 'mb', 'gb'")
        else:
            size = file_size / 1024 ** exponents_map[unit]
            return round(size, 3)

    async def configs():
        with open(Config) as fp:
            NewData = json.load(fp)
        del NewData["Token"]
        newData = json.dumps(NewData, indent=4, separators=(",", ": "))
        content = f"```json\n{newData}\n```"
        configSize = f"```json\n\"Config.json\": \"{get_size(Config, 'kb')} kb\"\n```"
        delMsgSize = f"```json\n\"DeletedMessages.json\": \"{get_size(Deleted_Msgs_Json, 'kb')} kb\"\n```"
        editMsgSize = f"```json\n\"EditedMessages.json\": \"{get_size(Edited_Msgs_Json, 'kb')} kb\"\n```"
        embed = discord.Embed(
            title="Settings",
            description=f"{content}\n{configSize}\n{delMsgSize}\n{editMsgSize}",
            color=discord.Color.pink(),
        )
        embed.add_field(
            name="Mode : set",
            value=f"{prefix()}settings set <key> <value>",
            inline=False,
        )
        embed.add_field(
            name="Mode : append",
            value=f"{prefix()}settings append <key> <value>",
            inline=False,
        )
        embed.add_field(
            name="Mode : remove",
            value=f"{prefix()}settings remove <key> <value>",
            inline=False,
        )
        embed.add_field(
            name="Mode : addkey",
            value=f"{prefix()}settings addkey <key> <value> <list/leave blank for default>",
            inline=False,
        )
        embed.add_field(
            name="Mode : delkey", value=f"{prefix()}settings delkey <key>", inline=False
        )
        await ctx.send(embed=embed)

    if mode == None:
        await configs()
        return

    if mode == "remove":
        try:
            with open(Config) as fp:
                NewData = json.load(fp)

            NewData[key].remove(value)

            with open(Config, "w+") as json_file:
                json.dump(NewData, json_file, indent=4, separators=(",", ": "))

            await configs()
            return
        except Exception as e:
            await ctx.send(e)
            return

    if mode == "append":
        try:
            with open(Config) as fp:
                NewData = json.load(fp)

            NewData[key].append(value)

            with open(Config, "r+") as json_file:
                json.dump(NewData, json_file, indent=4, separators=(",", ": "))

            await configs()
            return
        except Exception as e:
            await ctx.send(e)
            return

    if mode == "addkey":

        if type == None:
            try:
                with open(Config) as fp:
                    NewData = json.load(fp)

                NewData[key] = value

                with open(Config, "w+") as json_file:
                    json.dump(NewData, json_file, indent=4, separators=(",", ": "))

                await configs()
                return
            except Exception as e:
                await ctx.send(e)
                return

        if type == "list":
            try:
                with open(Config) as fp:
                    NewData = json.load(fp)

                NewData[key] = [value]

                with open(Config, "w+") as json_file:
                    json.dump(NewData, json_file, indent=4, separators=(",", ": "))

                await configs()
                return
            except Exception as e:
                await ctx.send(e)
                return

    if mode == "delkey":
        try:
            with open(Config) as fp:
                NewData = json.load(fp)

            del NewData[key]

            with open(Config, "w+") as json_file:
                json.dump(NewData, json_file, indent=4, separators=(",", ": "))

            await configs()
            return
        except Exception as e:
            await ctx.send(e)
            return

    if mode == "set":
        try:
            with open(Config) as fp:
                NewData = json.load(fp)

            NewData[key] = value

            with open(Config, "w+") as json_file:
                json.dump(NewData, json_file, indent=4, separators=(",", ": "))

            await configs()
            return
        except Exception as e:
            await ctx.send(e)
            return


@client.command()
async def get(ctx, link):
    await ctx.reply("Please Wait A Few Seconds", delete_after=0.5)

    if "https://" not in link and "http://" not in link:
        link = "https://" + link

    session = requests.Session()
    response = session.get(
        link,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0"
        },
    )

    with open("data.txt", "w") as file:
        file.write(response.text)
        file.close()
    await ctx.send("Print Output (p) or Send File (s)")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msgs = await client.wait_for("message", check=check, timeout=30)
    except asyncio.TimeoutError:
        await ctx.send("You Didn't Reply In Time.")

    if msgs.content == "p":
        with open("data.txt", "r") as file:
            msg = file.read(2000).strip()
            while len(msg) > 0:
                embed = discord.Embed(
                    title=link.lower(),
                    description=f"{msg}",
                    color=discord.Color.red(),
                    timestamp=datetime.now(),
                )
                user = ctx.author
                await user.send(embed=embed)
                msg = file.read(2000).strip()
        os.remove("data.txt")
    else:
        user = ctx.author
        await user.send(file=discord.File("data.txt"))
        os.remove("data.txt")


@client.command()
async def render(ctx, wrld):
    urls = f"https://s3.amazonaws.com/world.growtopiagame.com/{wrld}.png"
    req = requests.get(urls)
    if req.status_code == 200:
        await ctx.send("Please Wait A Few Seconds", delete_after=1)
        embed = discord.Embed(
            title=f"Render Of {wrld.upper()}", color=discord.Color.green()
        )
        embed.set_image(url=urls)
        await ctx.reply(embed=embed)
    else:
        await ctx.send("Please Wait A Few Seconds", delete_after=1)
        embeds = discord.Embed(
            title=f"World : {wrld.upper()}",
            description="Not Found 404",
            color=discord.Color.red(),
        )
        await ctx.reply(embed=embeds)


@client.command()
async def server(ctx, mode=None):
    if str(ctx.author.id) == getConfig()["Admin"]:
        guildList = {"Data": {}}
        guildList["Data"]["ServerCount"] = len(client.guilds)
        guildList["Data"]["Servers"] = {}

        if mode == None:
            for guild in client.guilds:
                try:
                    guildList["Data"]["Servers"][guild.name]
                except:
                    guildList["Data"]["Servers"].update(
                        {guild.name: {"Server_ID": guild.id}}
                    )

            guildData = json.dumps(guildList, indent=4, separators=(",", ": "))
            guildDatas = f"```json\n{guildData}\n```"

            embed = discord.Embed(description=guildDatas, color=discord.Color.random())
            embed.set_footer(
                text=f"*Tip : {prefix()}server file [ Sends Servers.json With More Details ]"
            )
            await ctx.send(embed=embed)

        if mode == "file":
            for guild in client.guilds:
                try:
                    guildList["Data"]["Servers"][guild.name]
                except:
                    guildList["Data"]["Servers"].update(
                        {
                            guild.name: {
                                "Server_ID": guild.id,
                                "Created_At": (guild.created_at).strftime(
                                    "%d-%m-%Y | %H:%M"
                                ),
                                "Member_Count": guild.member_count,
                                "Category_Count": len(guild.categories),
                                "Channel_Count": len(guild.channels),
                                "Role_Count": len(guild.roles),
                            }
                        }
                    )

            with open("Servers.json", "w") as file:
                file.write("{}")
                file.close()

            with open("Servers.json", "r+") as json_file:
                json.dump(guildList, json_file, indent=4, separators=(",", ": "))

            await ctx.send(file=discord.File("Servers.json"))
            os.remove("Servers.json")
    else:
        await ctx.send("You Don't Have Permission For This Command")


@client.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, limit: int):
    await ctx.message.delete()
    await asyncio.sleep(1)
    await ctx.channel.purge(limit=limit)
    purge_embed = discord.Embed(
        title=f"Purge [{prefix()}purge]",
        description=f"Successfully purged {limit} messages. \nCommand executed by {ctx.author}.",
        color=discord.Colour.random(),
    )
    purge_embed.set_footer(text=str(datetime.now()))
    await ctx.channel.send(embed=purge_embed, delete_after=True)


class MyView(discord.ui.View):
    def __init__(self, author):
        super().__init__(timeout=180)
        self.author = author

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        embed = discord.Embed(
            title="Timeout",
            description="You Did Not Respond Within 3 Minutes",
            color=discord.Color.magenta(),
        )
        embed.set_thumbnail(url=client.user.avatar.url)
        embed.set_footer(text=f"Type {prefix()}help To View Help Menu Again")
        await self.message.edit(embed=embed, view=self)

    async def on_timeout(self) -> None:
        await self.disable_all_items()

    @discord.ui.button(
        label="Main Menu", style=discord.ButtonStyle.success, disabled=True
    )
    async def first_help_callback(
        self, interaction: discord.Interaction, button: discord.ui.button
    ):
        button.disabled = True

        button_two = self.children[1]
        button_two.disabled = False

        button_three = self.children[2]
        button_three.disabled = False

        delta_uptime = datetime.now() - client.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        embed = discord.Embed(
            title=f"Hello, I am {client.user}",
            description="Click On One Of The Buttons Below To View The Help Menu.",
            color=discord.Color.random(),
        )
        embed.add_field(
            name="Bot Info",
            value=f"Online Time: **{days}d, {hours}h, {minutes}m, {seconds}s** | Ping: **{round(client.latency*1000)} Ms**",
            inline=False,
        )
        embed.set_thumbnail(url=client.user.avatar.url)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="User", style=discord.ButtonStyle.primary)
    async def second_help_callback(
        self, interaction: discord.Interaction, button: discord.ui.button
    ):
        button.disabled = True

        button_one = self.children[0]
        button_one.disabled = False

        button_three = self.children[2]
        button_three.disabled = False

        embed = discord.Embed(title="Help Menu", color=discord.Color.blue())
        embed.add_field(
            name=f"{prefix()}render", value="<name of gt world>", inline=False
        )
        embed.add_field(
            name=f"{prefix()}chat", value="<whatever you want to ask>", inline=False
        )
        embed.add_field(name=f"{prefix()}purge", value="<amount of msgs>", inline=False)
        embed.add_field(
            name=f"{prefix()}snipe",
            value="<number of msg>, Returns Most Current Deleted Msgs If Argument Is Left Blank",
            inline=False,
        )
        embed.add_field(
            name=f"{prefix()}snipeedit",
            value="<number of msg>, Returns Most Current Edited Msgs If Argument Is Left Blank",
            inline=False,
        )
        embed.add_field(name=f"{prefix()}get", value="<website url>", inline=False)
        embed.add_field(
            name=f"{prefix()}porthelp", value="Help Menu Of Port Scanner", inline=False
        )
        embed.add_field(
            name=f"{prefix()}ttb",
            value="<text> INFO : Convert Texts To Binary",
            inline=False,
        )
        embed.add_field(
            name=f"{prefix()}btt",
            value="<binary code> INFO : Convert Binary To Texts",
            inline=False,
        )
        embed.add_field(name=f"{prefix()}ss", value="<website url>", inline=False)
        embed.add_field(name=f"{prefix()}check", value="<ip/website url>", inline=False)
        embed.add_field(name=f"{prefix()}ping", value="Shows Bot Latency", inline=False)
        embed.set_thumbnail(url=client.user.avatar.url)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Owner", style=discord.ButtonStyle.primary)
    async def third_help_callback(
        self, interaction: discord.Interaction, button: discord.ui.button
    ):
        if str(interaction.user.id) == getConfig()["Admin"]:
            button.disabled = True

            button_two = self.children[1]
            button_two.disabled = False

            button_one = self.children[0]
            button_one.disabled = False

            owner = discord.Embed(
                title="Help Menu (Owner Only)", color=discord.Color.red()
            )
            owner.add_field(
                name=f"{prefix()}settings",
                value=f"Shows / Changes Settings Of {client.user}",
                inline=False,
            )
            owner.add_field(
                name=f"{prefix()}clear",
                value="[1] For All Logged Deleted Messages\n[2] For All Logged Edited Messages",
                inline=False,
            )
            owner.add_field(
                name=f"{prefix()}server",
                value="Get a List Of Servers The Bot Joined",
                inline=False,
            )
            owner.add_field(name=f"{prefix()}invite", value="<server id>", inline=False)
            owner.add_field(
                name=f"{prefix()}start",
                value="<channel id> INFO : Logs Messages From a Channel",
                inline=False,
            )
            owner.add_field(name=f"{prefix()}stop", value="Stops Logging Message")
            owner.set_thumbnail(url=client.user.avatar.url)
            await interaction.response.send_message(
                embed=owner, view=self, ephemeral=True
            )
        else:
            await interaction.response.send_message("No Permission", ephemeral=True)

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.author.id:
            return interaction.user.id == self.author.id
        else:
            await interaction.response.send_message(
                "You Cannot Interact With This Message", ephemeral=True
            )


@client.command(aliases=["HELP"])
async def help(ctx):
    delta_uptime = datetime.now() - client.launch_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    embed = discord.Embed(
        title=f"Hello, I am {client.user}",
        description="Click On One Of The Buttons Below To View The Help Menu.",
        color=discord.Color.random(),
    )
    embed.add_field(
        name="Bot Info",
        value=f"Online Time: **{days}d, {hours}h, {minutes}m, {seconds}s** | Ping: **{round(client.latency*1000)} Ms**",
        inline=False,
    )
    embed.set_thumbnail(url=client.user.avatar.url)
    view = MyView(ctx.author)
    message = await ctx.send(embed=embed, view=view)
    view.message = message


@client.command()
async def check(ctx, ip: str = None):
    if ip is None:
        await ctx.send("Please sepcify an IP address")
        return
    else:
        try:
            with requests.session() as ses:
                resp = ses.get(f"https://ipinfo.io/{ip}/json")
                if "Wrong ip" in resp.text:
                    await ctx.send("Invalid IP address")
                    return
                else:
                    try:
                        j = resp.json()
                        embed = discord.Embed(
                            color=discord.Colour.red(),
                            title=f"INFO",
                            timestamp=datetime.now(),
                        )
                        embed.add_field(name=f"IP", value=f"{ip}", inline=True)
                        embed.add_field(name=f"City", value=f'{j["city"]}', inline=True)
                        embed.add_field(
                            name=f"Region", value=f'{j["region"]}', inline=True
                        )
                        embed.add_field(
                            name=f"Country", value=f'{j["country"]}', inline=True
                        )
                        embed.add_field(
                            name=f"Coordinates", value=f'{j["loc"]}', inline=True
                        )
                        embed.add_field(
                            name=f"Postal", value=f'{j["postal"]}', inline=True
                        )
                        embed.add_field(
                            name=f"Timezone", value=f'{j["timezone"]}', inline=True
                        )
                        embed.add_field(
                            name=f"Organization", value=f'{j["org"]}', inline=True
                        )
                        embed.set_footer(
                            text="これを使用していただきありがとうございます"
                        )
                        await ctx.send(embed=embed)
                    except discord.HTTPException:
                        await ctx.send(
                            f'**{ip} Info**\n\nCity: {j["city"]}\nRegion: {j["region"]}\nCountry: {j["country"]}\nCoordinates: {j["loc"]}\nPostal: {j["postal"]}\nTimezone: {j["timezone"]}\nOrganization: {j["org"]}'
                        )
        except Exception as e:
            await ctx.send(f"Error: {e}")


@client.command()
async def porthelp(ctx):
    embed = discord.Embed(
        title=f"""Usage Of {prefix()}scan <ip/url> Scan For Open Ports""",
        description=f"""{prefix()}scan 127.0.0.1\n\n\n\n\n**Port Scanner Tools By : https://github.com/inforkgodara/python-port-scanner**""",
        color=discord.Color.green(),
    )
    embed.set_thumbnail(url=ctx.author.avatar.url)
    await ctx.send(embed=embed)


@client.command()
async def scan(ctx, ipa):
    socket.setdefaulttimeout(0.25)
    lock = threading.Lock()
    host = socket.gethostbyname(ipa)
    await ctx.send("Scanning on IP Address: " + host)
    fi = open("ports.txt", "w+")
    fi.truncate(0)
    fil = open("ports.txt", "w")
    fil.close()

    def scan(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            con = sock.connect((host, port))
            with lock:
                f = open("ports.txt", "a")
                f.write(str(port) + " is open\n")
                f.close()
                con.close()
        except:
            pass

    def execute():
        while True:
            worker = queue.get()
            scan(worker)
            queue.task_done()

    queue = Queue()
    start_time = time.time()
    for x in range(100):
        thread = threading.Thread(target=execute)
        thread.daemon = True
        thread.start()
    for worker in range(1, 1024):
        queue.put(worker)
    queue.join()
    fol = open("ports.txt", "r")
    mug = fol.readlines()
    new_sentences = [re.sub(r"\n+", "", s) for s in mug]
    await ctx.send(new_sentences)
    await ctx.send("Time taken:" + str(time.time() - start_time))
    os.remove("ports.txt")


@client.command()
async def btt(ctx, *, bit):
    revert = "".join([chr(int(s, 2)) for s in bit.split()])
    embed = discord.Embed(
        title="Binary To Text",
        description=f"Binary : {bit}"
        + "\n\nConverted To"
        + f"\n\nText : {revert}"
        + "\n\n[Source](https://stackoverflow.com/a/48219616)",
        color=discord.Color.red(),
    )
    await ctx.send(embed=embed)


@client.command()
async def ttb(ctx, *, ans):
    out = " ".join(format(ord(x), "b") for x in ans)
    embed = discord.Embed(
        title="Text To Binary",
        description=f"Text : {ans}"
        + "\n\nConverted To"
        + f"\n\nBinary : {out}"
        + "\n\n[Source](https://stackoverflow.com/a/48219616)",
        color=discord.Color.red(),
    )
    await ctx.send(embed=embed)


@client.command()
async def ss(ctx, urlx):
    wait = discord.Embed(
        title="Please wait for a few seconds", color=discord.Colour.random()
    )
    await ctx.send(embed=wait, delete_after=True)
    if "https://" not in urlx and "http://" not in urlx:
        urlx = "https://" + urlx
    try:
        options = (
            TakeOptions.url(urlx)
            .format("png")
            .viewport_width(1024)
            .viewport_height(768)
            .block_cookie_banners(True)
            .block_chats(True)
        )
        image = screenshot.take(options)
        with open("result.png", "wb") as result_file:
            shutil.copyfileobj(image, result_file)
        file = discord.File("result.png")
        embed = discord.Embed(
            description=f"Screenshot Of {urlx.lower()}", color=discord.Colour.random()
        )
        embed.set_image(url="attachment://result.png")
        await ctx.send(embed=embed, file=file)
        os.remove("result.png")
    except:
        error = discord.Embed(
            title="Request Failed",
            description="Invalid Url",
            color=discord.Colour.random(),
        )
        await ctx.send(embed=error)


@client.command()
@commands.is_owner()
async def invite(ctx, guildid: int):
    try:
        guild = client.get_guild(guildid)
        invitelink = ""
        i = 0
        while invitelink == "":
            channel = guild.text_channels[i]
            link = await channel.create_invite(max_age=0, max_uses=0)
            invitelink = str(link)
            i += 1
        await ctx.send(invitelink)
    except Exception:
        await ctx.send("Something went wrong")


@client.command()
async def ping(ctx):
    await ctx.send(f"My ping is** {round(client.latency*1000)} Ms**")


@client.command()
@commands.is_owner()
async def start(ctx, arg: int):
    await ctx.send("Message Logger Started")
    global log_channel
    log_channel = True
    global fcid
    fcid = arg
    global tcid
    tcid = ctx.channel.id
    global LOGWEB
    weeb = await ctx.channel.create_webhook(name="Webhook")
    LOGWEB = weeb.url


@client.command()
@commands.is_owner()
async def stop(ctx):
    await ctx.send("Message Logger Stopped")
    global log_channel
    log_channel = False
    global LOGWEB
    webhooks = await ctx.channel.webhooks()
    for webhook in webhooks:
        if webhook.url == LOGWEB:
            await webhook.delete()
            await ctx.send("Webhook Deleted")


@client.command()
async def chat(ctx, *, question):
    openai.api_key = getConfig()["openaiKey"]
    openai.base_url = "https://api.pawan.krd/pai-001/v1/"

    await ctx.send("Pls Wait For a Few Seconds...", delete_after=True)
    completion = openai.chat.completions.create(
        model="pai-001", messages=[{"role": "user", "content": question}]
    )
    await ctx.send(completion.choices[0].message.content)


client.run(token)
