import logging
import os
from os import system
from racetime_bot import Bot
from racetime_bot import RaceHandler
import ssl
from DiscordGenerator import DiscordGeneratorBot
import SeedGenerator
from SeedGenerator import ChoozoException


class RacetimeGeneratorHandler(RaceHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.seed_rolled = False


    def set_discord_bot(self, discordbot):
        self.discordbot = discordbot


    async def begin(self):
        await self.send_message("Coming Soon\u2122")


    async def error(self, data):
        self.discordbot.external_send_message_to_sandbox("RacetimeGeneratorHandler error: %s" % data.get('errors'))
        raise Exception(data.get('errors'))


    async def validate_can_roll_seed(self):
        if self.seed_rolled:
            raise ChoozoException("Seed already rolled for this raceroom")
        if self.data.get('status').get('value') in ('pending', 'in_progress'):
            raise ChoozoException("Cannot roll seed, race already in progress")


    async def ex_sgl23smr(self, args, message):
        try:
            await SeedGenerator.validate_arguments(args, 0, 0, "0 expected")
            await self.validate_can_roll_seed()
            await self.generate_smvaria("SGL23Online", "Season_Races")
        except ChoozoException as ce:
            await self.send_message(ce.message)
        except Exception as e:
            await discordbot.send_exception_to_sandbox(e)


    async def generate_smvaria(self, settingsPreset, skillsPreset):
        await self.send_message("Generating seed...")
        settingsDict = {}
        seed = await SeedGenerator.generate_smvaria_seed(settingsPreset, skillsPreset, True, settingsDict)
        await self.set_bot_raceinfo(f"{settingsPreset} / {skillsPreset} - {seed.url}")
        await self.send_message(seed.url)
        warnings = await SeedGenerator.parse_smvaria_warnings(seed)
        for warning in warnings:
            await self.send_message(warning)
        self.seed_rolled = True


class RacetimeGeneratorBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)


    def set_discord_bot(self, discordbot):
        self.discordbot = discordbot


    def start_racetime_bot(self):
        self.loop.create_task(self.reauthorize())
        self.loop.create_task(self.refresh_races())


    def get_handler_class(self):
        return RacetimeGeneratorHandler


    def create_handler(self, race_data):
        if not self.discordbot:
            raise ChoozoException("RacetimeGeneratorBot creating handler without discord bot!")
        handler = super().create_handler(race_data)
        handler.set_discord_bot(self.discordbot)
        return handler


racetimebot = None


async def racetime_create_and_start_bot(discordbot):
    try:
        await discordbot.get_ready_event().wait()
        clientId = os.environ.get("SMR_RACETIME_CLIENT_ID")
        if not clientId:
            raise ChoozoException("Choozo Race Seed Generator SMR_RACETIME_CLIENT_ID not set!")
        clientSecret = os.environ.get("SMR_RACETIME_CLIENT_SECRET")
        if not clientSecret:
            raise ChoozoException("Choozo Race Seed Generator SMR_RACETIME_CLIENT_SECRET not set!")
        racetimebot = RacetimeGeneratorBot(
            category_slug="smr",
            client_id=clientId,
            client_secret=clientSecret,
            logger=logging.getLogger()
        )
        racetimebot.set_discord_bot(discordbot)
        racetimebot.start_racetime_bot()
    except Exception as e:
        await discordbot.send_exception_to_sandbox(e)

