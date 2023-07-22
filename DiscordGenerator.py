import datetime
import discord
from discord.ext import commands
import os
from os import system
import traceback
from SeedGenerator import ChoozoException
from SeedGenerator import validate_choozo
from SeedGenerator import generate_choozo
from SeedGenerator import generate_smvaria


roles = None
intents = discord.Intents.all()
discordbot = commands.Bot(command_prefix="!", intents=intents)


async def discord_generate_choozo(ctx, race, split, area, boss, difficulty, escape, morph, start, title):
    await validate_choozo(split, area, boss, difficulty, escape, morph, start)
    await ctx.send("Generating seed...")
    seed = await generate_choozo(race, split, area, boss, difficulty, escape, morph, start)

    splitDescriptionDict = {
        "FullCountdown": "Full Countdown",
        "M/m": "Major/minor",
        "RandomSplit": "Random"
    }

    if difficulty == "VeryHardDifficulty":
        difficulty = "Very HardDifficulty"

    if start == "NotDeepStart":
        start = "Not DeepStart"

    embedTitle = "%s\n%s Seed" % (
        "Generated Super Metroid Choozo" if len(title) == 0 else ' '.join(title),
        "Race" if race else "Practice"
    )
    embedDescription = (
        f"**Item Split: **{splitDescriptionDict[split]}\n"
        f"**Area: **{area[:-4]}\n"
        f"**Boss: **{boss[:-4]}\n"
        f"**Difficulty: **{difficulty[:-10]}\n"
        f"**Escape: **{escape[:-6]}\n"
        f"**Morph: **{morph[:-5]}\n"
        f"**Start: **{start[:-5]}"
    )
    await discord_embed_seed(ctx, seed, embedTitle, embedDescription)


async def discord_generate_smvaria(ctx, settingsPreset, skillsPreset):
    await ctx.send("Generating seed...")
    settingsDict = {}
    seed = await generate_smvaria(settingsPreset, skillsPreset, True, settingsDict)
    embedTitle = "Generated Super Metroid Race Seed"
    embedDescription = (
        f"**Settings: **{settingsPreset}\n"
        f"**Skills: **{skillsPreset}"
    )
    await discord_embed_seed(ctx, seed, embedTitle, embedDescription)


async def discord_embed_seed(ctx, seed, embedTitle, embedDescription):
    embed = discord.Embed(
        title=embedTitle,
        description=embedDescription,
        color=discord.Colour.orange(),
        timestamp=datetime.datetime.utcnow()
    )
    embed.add_field(
        name="Link",
        value=seed.url,
        inline=False
    )
    errorMsg = seed.data.get('errorMsg', '')
    if errorMsg != '':
        embed.add_field(
            name="Warnings",
            value=errorMsg.replace("<br/>", "\n").rstrip(),
            inline=False
        )
    await ctx.send(embed=embed)


async def discord_validate_channel(ctx):
    if not isinstance(ctx.message.channel, discord.channel.DMChannel):
        if ctx.message.channel.id != 1021775359605219359 and ctx.message.channel.id != 1019847346344964126:
            raise ChoozoException("Please go to the #practice channel to generate seeds")


async def discord_get_arguments_provided_text(args):
    return "%s %s provided" % (len(args), "argument" if 1 == len(args) else "arguments")


async def discord_generate_choozo_parse_args(ctx, race, args):
    try:
        await discord_validate_channel(ctx)
        if len(args) < 7:
            argumentsProvided = await discord_get_arguments_provided_text(args)
            raise ChoozoException("%s, 7 required (item split, area, boss, difficulty, escape, morph, start)" % argumentsProvided)
        await discord_generate_choozo(ctx, race, args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7:])
    except ChoozoException as ce:
        await ctx.send(ce.message)


async def discord_generate_smvaria_parse_args(ctx, args):
    try:
        await discord_validate_channel(ctx)
        if len(args) != 2:
            argumentsProvided = await discord_get_arguments_provided_text(args)
            raise ChoozoException("%s, 2 required (settings preset, skills preset)" % argumentsProvided)
        await discord_generate_smvaria(ctx, args[0], args[1])
    except ChoozoException as ce:
        await ctx.send(ce.message)


async def discord_help_parse_args(ctx, args):
    try:
        await discord_validate_channel(ctx)
        if len(args) != 0:
            argumentsProvided = await discord_get_arguments_provided_text(args)
            raise ChoozoException("%s, 0 expected" % argumentsProvided)
        await ctx.send("Choozo Race Seed Generator online")
    except ChoozoException as ce:
        await ctx.send(ce.message)


@discordbot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def choozopractice(ctx, *args):
    try:
        await discord_generate_choozo_parse_args(ctx, False, args)
    except Exception as e:
        await discord_send_exception_to_sandbox(e)


@discordbot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def choozorace(ctx, *args):
    try:
        await discord_generate_choozo_parse_args(ctx, True, args)
    except Exception as e:
        await discord_send_exception_to_sandbox(e)


@discordbot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def choozobot(ctx, *args):
    try:
        await discord_help_parse_args(ctx, args)
    except Exception as e:
        await discord_send_exception_to_sandbox(e)


@discordbot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def smvaria(ctx, *args):
    try:
        await discord_generate_smvaria_parse_args(ctx, args)
    except Exception as e:
        await discord_send_exception_to_sandbox(e)


async def discord_on_role_react(payload, add):
    global roles
    if 1021969894293647411 == payload.channel_id:
        emojiDict = {
            "🇦": "Async Race Admin",
            "🇨": "Comms",
            "🇵": "Practice",
            "🇷": "Runner",
            "🇹": "Tracking"
        }
        if payload.emoji.name in emojiDict:
            reactRoleName = emojiDict[payload.emoji.name]
            if roles is None:
                roles = await discordbot.guilds[0].fetch_roles()
            for role in roles:
                if role.name == reactRoleName:
                    if add:
                        await payload.member.add_roles(role)
                    else:
                        for member in discordbot.get_all_members():
                            if member.id == payload.user_id:
                                await member.remove_roles(role)


@discordbot.event
async def on_raw_reaction_add(payload):
    try:
        await discord_on_role_react(payload, True)
    except Exception as e:
        await discord_send_exception_to_sandbox(e)


@discordbot.event
async def on_raw_reaction_remove(payload):
    try:
        await discord_on_role_react(payload, False)
    except Exception as e:
        await discord_send_exception_to_sandbox(e)


async def discord_send_message_to_sandbox(message):
    channel = discordbot.get_channel(1019847346344964126)
    await channel.send(message)


async def discord_send_exception_to_sandbox(e):
    message = ''.join(traceback.format_exception(None, e, e.__traceback__))
    await discord_send_message_to_sandbox("Choozo Race Seed Generator Exception:\n%s" % message)
    raise e


@discordbot.event
async def on_ready():
    await discord_send_message_to_sandbox("Choozo Race Seed Generator started")


@discordbot.event
async def on_message(message):
    ctx = await discordbot.get_context(message)
    await discordbot.invoke(ctx)


async def discord_start_bot():
    token = os.environ.get("CHOOZO_TOKEN")
    if not token:
        raise ChoozoException("Choozo Race Seed Generator CHOOZO_TOKEN not set!")
    await discordbot.start(token)

