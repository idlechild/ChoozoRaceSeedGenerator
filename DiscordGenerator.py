import asyncio
import datetime
import discord
from discord.ext import commands
import os
from os import system
import traceback
import SeedGenerator
from SeedGenerator import ChoozoException


exceptionrecursion = False
roles = None
intents = discord.Intents.all()
discordbot = commands.Bot(command_prefix="!", intents=intents)


async def discord_generate_choozo(ctx, race, split, area, boss, difficulty, escape, morph, start, title):
    await SeedGenerator.validate_choozo_params(split, area, boss, difficulty, escape, morph, start)
    await ctx.send("Generating seed...")
    seed = await SeedGenerator.generate_choozo_seed(race, split, area, boss, difficulty, escape, morph, start)

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
    seed = await SeedGenerator.generate_smvaria_seed(settingsPreset, skillsPreset, True, settingsDict)
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
    warnings = await SeedGenerator.parse_smvaria_warnings(seed)
    if len(warnings) > 0:
        embed.add_field(
            name="Warnings",
            value='\n'.join(warnings),
            inline=False
        )
    await ctx.send(embed=embed)


async def discord_validate_channel(ctx):
    if not isinstance(ctx.message.channel, discord.channel.DMChannel):
        if ctx.message.channel.id != 1021775359605219359 and ctx.message.channel.id != 1019847346344964126:
            raise ChoozoException("Please go to the #practice channel to generate seeds")


async def discord_generate_choozo_parse_args(ctx, race, args):
    try:
        await discord_validate_channel(ctx)
        await SeedGenerator.validate_arguments(args, 7, -1, "7 required (item split, area, boss, difficulty, escape, morph, start)")
        await discord_generate_choozo(ctx, race, args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7:])
    except ChoozoException as ce:
        await discord_send_message_to_channel(ctx, ce.message)
    except Exception as e:
        await discord_send_exception_to_sandbox(e)


async def discord_generate_smvaria_parse_args(ctx, args):
    try:
        await discord_validate_channel(ctx)
        await SeedGenerator.validate_arguments(args, 2, 2, "2 required (settings preset, skills preset)")
        await discord_generate_smvaria(ctx, args[0], args[1])
    except ChoozoException as ce:
        await discord_send_message_to_channel(ctx, ce.message)
    except Exception as e:
        await discord_send_exception_to_sandbox(e)


async def discord_generate_sgl23smr_parse_args(ctx, args):
    try:
        await discord_validate_channel(ctx)
        await SeedGenerator.validate_arguments(args, 0, 0, "0 expected")
        await discord_generate_smvaria(ctx, "SGL23Online", "Season_Races")
    except ChoozoException as ce:
        await discord_send_message_to_channel(ctx, ce.message)
    except Exception as e:
        await discord_send_exception_to_sandbox(e)


async def discord_help_parse_args(ctx, args):
    try:
        await discord_validate_channel(ctx)
        await SeedGenerator.validate_arguments(args, 0, 0, "0 expected")
        await ctx.send("Choozo Race Seed Generator online")
    except ChoozoException as ce:
        await discord_send_message_to_channel(ctx, ce.message)
    except Exception as e:
        await discord_send_exception_to_sandbox(e)


async def discord_handle_role_react(payload, add):
    try:
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
    except Exception as e:
        await discord_send_exception_to_sandbox(e)


async def discord_send_message_to_channel(channel, message):
    if not channel:
        raise ChoozoException("Request to send message to empty channel")
    if not message or 0 >= len(message):
        raise ChoozoException("Request to send empty message")
    while len(message) > 2000:
        await channel.send(message[:2000])
        message = message[2000:]
    if len(message) > 0:
        await channel.send(message)


async def discord_send_message_to_sandbox(message):
    channel = discordbot.get_channel(1019847346344964126)
    await discord_send_message_to_channel(channel, message)


async def discord_send_exception_to_sandbox(e):
    formatted_exception = ''.join(traceback.format_exception(None, e, e.__traceback__))
    message = "Choozo Race Seed Generator Exception:\n%s" % formatted_exception
    await discord_send_message_to_sandbox(message)


async def discord_handle_exception(self, loop, context):
    global exceptionrecursion
    if not exceptionrecursion:
        exceptionrecursion = True
        message = "Choozo Race Seed Generator Exception:\n%s" % context
        await discord_send_message_to_sandbox(message)
        exceptionrecursion = False


async def discord_handle_ready():
    asyncio.get_event_loop().set_exception_handler(discord_handle_exception)
    await discord_send_message_to_sandbox("Choozo Race Seed Generator started")


@discordbot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def choozopractice(ctx, *args):
    await discord_generate_choozo_parse_args(ctx, False, args)


@discordbot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def choozorace(ctx, *args):
    await discord_generate_choozo_parse_args(ctx, True, args)


@discordbot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def choozobot(ctx, *args):
    await discord_help_parse_args(ctx, args)


@discordbot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def smvaria(ctx, *args):
    await discord_generate_smvaria_parse_args(ctx, args)


@discordbot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def sgl23smr(ctx, *args):
    await discord_generate_sgl23smr_parse_args(ctx, args)


@discordbot.event
async def on_raw_reaction_add(payload):
    await discord_handle_role_react(payload, True)


@discordbot.event
async def on_raw_reaction_remove(payload):
    await discord_handle_role_react(payload, False)


@discordbot.event
async def on_ready():
    await discord_handle_ready()


@discordbot.event
async def on_message(message):
    ctx = await discordbot.get_context(message)
    await discordbot.invoke(ctx)


async def discord_start_bot():
    token = os.environ.get("CHOOZO_TOKEN")
    if not token:
        raise ChoozoException("Choozo Race Seed Generator CHOOZO_TOKEN not set!")
    await discordbot.start(token)

