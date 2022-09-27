import datetime
import discord
from discord.ext import commands
import logging
import os
from os import system
from pyz3r.smvaria import SuperMetroidVaria


roles = None
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


class ChoozoException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__("ChoozoException")


async def generate_choozo(ctx, race, split, area, boss, difficulty, escape, morph, start, title):
    if split not in ['FullCountdown', 'M/m', 'RandomSplit']:
        raise ChoozoException("Invalid item split setting.  Must be FullCountdown, M/m or RandomSplit.")

    if area not in ['FullArea', 'LightArea', 'VanillaArea']:
        raise ChoozoException("Invalid area setting.  Must be FullArea, LightArea or VanillaArea.")

    if boss not in ['RandomBoss', 'VanillaBoss']:
        raise ChoozoException("Invalid boss setting.  Must be RandomBoss or VanillaBoss.")

    if difficulty not in ['HarderDifficulty', 'HardDifficulty', 'MediumDifficulty', 'EasyDifficulty', 'BasicDifficulty']:
        raise ChoozoException("Invalid difficulty setting.  Must be HarderDifficulty, HardDifficulty, MediumDifficulty, EasyDifficulty or BasicDifficulty.")

    if escape not in ['RandomEscape', 'VanillaEscape']:
        raise ChoozoException("Invalid escape setting.  Must be RandomEscape or VanillaEscape.")

    if morph not in ['LateMorph', 'RandomMorph', 'EarlyMorph']:
        raise ChoozoException("Invalid morph setting.  Must be LateMorph, RandomMorph or EarlyMorph.")

    if start not in ['DeepStart', 'RandomStart', 'NotDeepStart', 'ShallowStart', 'VanillaStart']:
        raise ChoozoException("Invalid start setting.  Must be DeepStart, RandomStart, NotDeepStart, ShallowStart or VanillaStart.")

    splitDict = {
        "FullCountdown": "FullWithHUD",
        "M/m": "Major",
        "RandomSplit": "random"
    }

    difficultyDict = {
        "HarderDifficulty": "harder",
        "HardDifficulty": "hard",
        "MediumDifficulty": "medium",
        "EasyDifficulty": "easy",
        "BasicDifficulty": "easy"
    }

    morphDict = {
        "LateMorph": "late",
        "RandomMorph": "random",
        "EarlyMorph": "early"
    }

    startDict = {
        "DeepStart": [
            'Aqueduct',
            'Bubble Mountain',
            'Firefleas Top'
        ],
        "RandomStart": [
            'Aqueduct',
            'Big Pink',
            'Bubble Mountain',
            'Business Center',
            'Etecoons Supers',
            'Firefleas Top',
            'Gauntlet Top',
            'Golden Four',
            'Green Brinstar Elevator',
            'Red Brinstar Elevator',
            'Wrecked Ship Main'
        ],
        "NotDeepStart": [
            'Big Pink',
            'Business Center',
            'Etecoons Supers',
            'Gauntlet Top',
            'Golden Four',
            'Green Brinstar Elevator',
            'Red Brinstar Elevator',
            'Wrecked Ship Main'
        ],
        "ShallowStart": [
            'Big Pink',
            'Gauntlet Top',
            'Green Brinstar Elevator',
            'Wrecked Ship Main'
        ],
        "VanillaStart": [
            'Landing Site'
        ]
    }

    settings = {
        "hud": "on",
        "suitsRestriction": "off",
        "variaTweaks": "on",

        "majorsSplit": splitDict[split],
        "majorsSplitMultiSelect": ['FullWithHUD', 'Major'],

        "areaRandomization": "off" if area == "VanillaArea" else "on",
        "areaLayout": "off" if area == "VanillaArea" else "on",
        "lightAreaRandomization": "on" if area == "LightArea" else "off",

        "bossRandomization": "off" if boss == "VanillaBoss" else "on",

        "maxDifficulty": difficultyDict[difficulty],

        "escapeRando": "off" if escape == "VanillaEscape" else "on",

        "morphPlacement": morphDict[morph],

        "startLocation": "Landing Site" if start == "VanillaStart" else "random",
        "startLocationMultiSelect": startDict[start]
    }

    await ctx.send("Generating seed...")
    seed = await SuperMetroidVaria.create(
        settings_preset="Season_Races",
        skills_preset="newbie" if difficulty == "BasicDifficulty" else "Season_Races",
        race=race,
        settings_dict=settings
    )
    if not hasattr(seed, 'guid'):
        raise ChoozoException("Error: %s" % seed.data)

    splitDescriptionDict = {
        "FullCountdown": "Full Countdown",
        "M/m": "Major/minor",
        "RandomSplit": "Random"
    }

    if start == "NotDeepStart":
        start="Not DeepStart"

    embed = discord.Embed(
        title="%s\n%s Seed" % (
            "Generated Super Metroid Choozo" if len(title) == 0 else ' '.join(title),
            "Race" if race else "Practice"
        ),
        description=(
            f"**Item Split: **{splitDescriptionDict[split]}\n"
            f"**Area: **{area[:-4]}\n"
            f"**Boss: **{boss[:-4]}\n"
            f"**Difficulty: **{difficulty[:-10]}\n"
            f"**Escape: **{escape[:-6]}\n"
            f"**Morph: **{morph[:-5]}\n"
            f"**Start: **{start[:-5]}"
        ),
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


async def generate_choozo_parse_args(ctx, race, args):
    try:
        if ctx.message.channel.id != 1021775359605219359 and ctx.message.channel.id != 1019847346344964126:
            raise ChoozoException("Please go to the #practice channel to generate race seeds")
        if len(args) < 7:
            raise ChoozoException("%s %s provided, 7 required (item split, area, boss, difficulty, escape, morph, start)" % (len(args), "argument" if 1 == len(args) else "arguments"))
        await generate_choozo(ctx, race, args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7:])
    except ChoozoException as ce:
        await ctx.send(ce.message)


@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def choozopractice(ctx, *args):
    await generate_choozo_parse_args(ctx, False, args)


@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def choozorace(ctx, *args):
    await generate_choozo_parse_args(ctx, True, args)


async def on_role_react(payload, add):
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
                roles = await bot.guilds[0].fetch_roles()
            for role in roles:
                if role.name == reactRoleName:
                    if add:
                        await payload.member.add_roles(role)
                    else:
                        for member in bot.get_all_members():
                            if member.id == payload.user_id:
                                await member.remove_roles(role)


@bot.event
async def on_raw_reaction_add(payload):
    await on_role_react(payload, True)


@bot.event
async def on_raw_reaction_remove(payload):
    await on_role_react(payload, False)


@bot.event
async def on_message(message):
    ctx = await bot.get_context(message)
    await bot.invoke(ctx)


token = os.environ['CHOOZO_TOKEN']
bot.run(token, log_handler=logging.StreamHandler())

