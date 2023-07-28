import asyncio
import datetime
import discord
from discord.ext import commands
import os
from os import system
import traceback
import SeedGenerator
from SeedGenerator import ChoozoException


class DiscordGeneratorBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.exceptionrecursion = False
        self.readyevent = asyncio.Event()
        self.roles = None


    async def generate_choozo(self, ctx, race, split, area, boss, difficulty, escape, morph, start, title):
        await SeedGenerator.validate_choozo_params(split, area, boss, difficulty, escape, morph, start)
        await self.send_message_to_channel(ctx, "Generating seed...")
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
        await self.embed_seed(ctx, seed, embedTitle, embedDescription)


    async def generate_smvaria(self, ctx, settingsPreset, skillsPreset):
        await self.send_message_to_channel(ctx, "Generating seed...")
        settingsDict = {}
        seed = await SeedGenerator.generate_smvaria_seed(settingsPreset, skillsPreset, True, settingsDict)
        embedTitle = "Generated Super Metroid Race Seed"
        embedDescription = (
            f"**Settings: **{settingsPreset}\n"
            f"**Skills: **{skillsPreset}"
        )
        await self.embed_seed(ctx, seed, embedTitle, embedDescription)


    async def embed_seed(self, ctx, seed, embedTitle, embedDescription):
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


    async def validate_channel(self, ctx):
        if not isinstance(ctx.message.channel, discord.channel.DMChannel):
            if ctx.message.channel.id != 1021775359605219359 and ctx.message.channel.id != 1019847346344964126:
                raise ChoozoException("Please go to the #practice channel to generate seeds")


    async def generate_choozo_parse_args(self, ctx, race, args):
        try:
            await self.validate_channel(ctx)
            await SeedGenerator.validate_arguments(args, 7, -1, "7 required (item split, area, boss, difficulty, escape, morph, start)")
            await self.generate_choozo(ctx, race, args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7:])
        except ChoozoException as ce:
            await self.send_message_to_channel(ctx, ce.message)
        except Exception as e:
            await self.send_exception_to_sandbox(e)


    async def generate_smvaria_parse_args(self, ctx, args):
        try:
            await self.validate_channel(ctx)
            await SeedGenerator.validate_arguments(args, 2, 2, "2 required (settings preset, skills preset)")
            await self.generate_smvaria(ctx, args[0], args[1])
        except ChoozoException as ce:
            await self.send_message_to_channel(ctx, ce.message)
        except Exception as e:
            await self.send_exception_to_sandbox(e)


    async def generate_sgl23smr_parse_args(self, ctx, args):
        try:
            await self.validate_channel(ctx)
            await SeedGenerator.validate_arguments(args, 0, 0, "0 expected")
            await self.generate_smvaria(ctx, "SGL23Online", "Season_Races")
        except ChoozoException as ce:
            await self.send_message_to_channel(ctx, ce.message)
        except Exception as e:
            await self.send_exception_to_sandbox(e)


    async def help_parse_args(self, ctx, args):
        try:
            await self.validate_channel(ctx)
            await SeedGenerator.validate_arguments(args, 0, 0, "0 expected")
            await self.send_message_to_channel(ctx, "Choozo Race Seed Generator online")
        except ChoozoException as ce:
            await self.send_message_to_channel(ctx, ce.message)
        except Exception as e:
            await self.send_exception_to_sandbox(e)


    async def handle_role_react(self, payload, add):
        try:
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
                    if self.roles is None:
                        self.roles = await self.guilds[0].fetch_roles()
                    for self.role in roles:
                        if self.role.name == reactRoleName:
                            if add:
                                await payload.member.add_roles(role)
                            else:
                                for member in self.get_all_members():
                                    if member.id == payload.user_id:
                                        await member.remove_roles(role)
        except Exception as e:
            await self.send_exception_to_sandbox(e)


    async def send_message_to_channel(self, channel, message):
        if not channel:
            raise ChoozoException("Request to send message to empty channel")
        if not message or 0 >= len(message):
            raise ChoozoException("Request to send empty message")
        while len(message) > 2000:
            await channel.send(message[:2000])
            message = message[2000:]
        if len(message) > 0:
            await channel.send(message)


    def external_send_message_to_sandbox(self, message):
        self.dispatch("send_message_to_sandbox", message)


    async def handle_send_message_to_sandbox(self, message):
        channel = self.get_channel(1019847346344964126)
        await self.send_message_to_channel(channel, message)


    async def send_exception_to_sandbox(self, e):
        formatted_exception = ''.join(traceback.format_exception(None, e, e.__traceback__))
        message = "Choozo Race Seed Generator Exception:\n%s" % formatted_exception
        self.external_send_message_to_sandbox(message)
        raise e


    def handle_exception(self, loop, context):
        if not self.exceptionrecursion:
            self.exceptionrecursion = True
            message = "Choozo Race Seed Generator Exception:\n%s" % context
            self.external_send_message_to_sandbox(context)
            self.exceptionrecursion = False


    async def handle_ready(self):
        asyncio.get_event_loop().set_exception_handler(self.handle_exception)
        await self.handle_send_message_to_sandbox("Choozo Race Seed Generator started")
        self.readyevent.set()


    async def handle_message(self, message):
        ctx = await self.get_context(message)
        await self.invoke(ctx)


    def get_ready_event(self):
        return self.readyevent


discordbot = DiscordGeneratorBot(command_prefix="!", intents=discord.Intents.all())


@discordbot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def choozopractice(ctx, *args):
    await discordbot.generate_choozo_parse_args(ctx, False, args)


@discordbot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def choozorace(ctx, *args):
    await discordbot.generate_choozo_parse_args(ctx, True, args)


@discordbot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def choozobot(ctx, *args):
    await discordbot.help_parse_args(ctx, args)


@discordbot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def smvaria(ctx, *args):
    await discordbot.generate_smvaria_parse_args(ctx, args)


@discordbot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def sgl23smr(ctx, *args):
    await discordbot.generate_sgl23smr_parse_args(ctx, args)


@discordbot.event
async def on_raw_reaction_add(payload):
    await discordbot.handle_role_react(payload, True)


@discordbot.event
async def on_raw_reaction_remove(payload):
    await discordbot.handle_role_react(payload, False)


@discordbot.event
async def on_send_message_to_sandbox(message):
    await discordbot.handle_send_message_to_sandbox(message)


@discordbot.event
async def on_ready():
    await discordbot.handle_ready()


@discordbot.event
async def on_message(message):
    await discordbot.handle_message(message)


def discord_get_bot():
    global discordbot
    return discordbot


async def discord_start_bot(discordbot):
    token = os.environ.get("CHOOZO_TOKEN")
    if not token:
        raise ChoozoException("Choozo Race Seed Generator CHOOZO_TOKEN not set!")
    await discordbot.start(token)

