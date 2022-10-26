import asyncio
import copy
import json
import uuid
import aiohttp
from tenacity import RetryError, AsyncRetrying, stop_after_attempt, retry_if_exception_type


def mergedicts(dict1, dict2):
    for k in set(dict1.keys()).union(dict2.keys()):
        if k in dict1 and k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                yield (k, dict(mergedicts(dict1[k], dict2[k])))
            else:
                # If one of the values is not a dict, you can't continue merging it.
                # Value from second dict overrides one in first and we move on.
                yield (k, dict2[k])
                # Alternatively, replace this with exception raiser to alert you of value conflicts
        elif k in dict1:
            yield (k, dict1[k])
        else:
            yield (k, dict2[k])
          

class Pyz3rException(Exception):
    pass


class UnableToRetrieve(Pyz3rException):
    pass


class UnableToGenerate(Pyz3rException):
    pass


SETTINGS_DEFAULT = {
    "complexity": "advanced",
    "seed": "0",
    "preset": "regular",
    "raceMode": "off",
    "areaLayout": "off",
    "lightAreaRandomization": "off",
    "removeEscapeEnemies": "off",
    "layoutPatches": "on",
    "variaTweaks": "on",
    "gravityBehaviour": "Balanced",
    "nerfedCharge": "off",
    "itemsounds": "on",
    "elevators_doors_speed": "on",
    "spinjumprestart": "off",
    "rando_speed": "off",
    "animals": "off",
    "No_Music": "off",
    "random_music": "off",
    "maxDifficulty": "hardcore",
    "Infinite_Space_Jump": "off",
    "refill_before_save": "off",
    "missileQty": '3',
    "superQty": "2",
    "powerBombQty": "1",
    "minorQty": "100",
    "scavNumLocs": "10",
    "suitsRestriction": "on",
    "funCombat": "off",
    "funMovement": "off",
    "funSuits": "off",
    "hideItems": "off",
    "strictMinors": "off",
    "areaRandomization": "off",
    "bossRandomization": "off",
    "escapeRando": "off",
    "majorsSplit": "Full",
    "startLocation": "Landing Site",
    "energyQty": "vanilla",
    "morphPlacement": "early",
    "progressionDifficulty": "normal",
    "progressionSpeed": "medium",
    "startLocationMultiSelect": [
        'Ceres',
        'Landing Site',
        'Gauntlet Top',
        'Green Brinstar Elevator',
        'Big Pink,Etecoons Supers',
        'Wrecked Ship Main',
        'Firefleas Top',
        'Business Center',
        'Bubble Mountain',
        'Mama Turtle',
        'Watering Hole',
        'Aqueduct',
        'Red Brinstar Elevator',
        'Golden Four'
    ],
    "majorsSplitMultiSelect": [
        'Full',
        'Major',
        'Chozo'
    ],
    "progressionDifficultyMultiSelect": [
        'easier',
        'normal',
        'harder'
    ],
    "progressionSpeedMultiSelect": [
        'slowest',
        'slow',
        'medium',
        'fast',
        'fastest',
        'basic',
        'VARIAble',
        'speedrun'
    ],
    "morphPlacementMultiSelect": [
        'early',
        'late',
        'normal'
    ],
    "energyQtyMultiSelect": [
        'ultra sparse',
        'sparse',
        'medium',
        'vanilla'
    ],
    "minimizer": "off",
    "minimizerTourian": "off",
    "allowGreyDoors": "off",
    "minimizerQty": "45",
    "scavRandomized": "off",
    "hud": "off",
    "doorsColorsRando" : "off",
    "tourian" : "Vanilla",
    "objective" : ['kill all G4'],
}


class SuperMetroidVaria():
    def __init__(
        self,
        skills_preset,
        settings_preset,
        race,
        baseurl,
        username,
        password,
        settings_dict,
    ):
        self.skills_preset = skills_preset
        self.settings_preset = settings_preset
        self.baseurl = baseurl
        self.race = race
        self.username = username
        self.password = password
        self.auth = aiohttp.BasicAuth(login=username, password=password) if username and password else None
        self.settings_dict = settings_dict

    async def generate_game(self, raise_for_status=True):
        try:
            async for attempt in AsyncRetrying(
                    stop=stop_after_attempt(3),
                    retry=retry_if_exception_type((aiohttp.ClientResponseError, aiohttp.client_exceptions.ServerDisconnectedError))):
                with attempt:
                    async with aiohttp.request(
                            method='post',
                            url=f'{self.baseurl}/randomizerWebService',
                            data=self.settings,
                            auth=self.auth,
                            raise_for_status=raise_for_status) as resp:
                        req = await resp.json(content_type='text/html')
                    return req
        except RetryError as e:
            raise e.last_attempt._exception from e

    @classmethod
    async def create(
        cls,
        skills_preset='regular',
        settings_preset='default',
        race=False,
        baseurl='https://randommetroidsolver.pythonanywhere.com',
        username=None,
        password=None,
        settings_dict=None,
        raise_for_status=True,
    ):
        seed = cls(
            skills_preset=skills_preset,
            settings_preset=settings_preset,
            race=race,
            baseurl=baseurl,
            username=username,
            password=password,
            settings_dict=settings_dict,
        )

        seed.settings = await seed.get_settings()

        seed.data = await seed.generate_game(raise_for_status)
        if 'seedKey' in seed.data:
            seed.guid = uuid.UUID(hex=seed.data['seedKey'])

        return seed

    async def get_settings(self):
        skills_preset_data = await self.fetch_skills_preset(self.skills_preset)
        settings_preset_data = await self.fetch_settings_preset(self.settings_preset)

        settings = copy.deepcopy(SETTINGS_DEFAULT)
        settings = dict(mergedicts(settings, settings_preset_data))
        if self.settings_dict:
            settings = dict(mergedicts(settings, self.settings_dict))
        settings['preset'] = self.skills_preset
        settings['raceMode'] = "on" if self.race else "off"
        settings['paramsFileTarget'] = json.dumps(skills_preset_data)

        # convert any lists to comma-deliminated strings and return
        return {s: (','.join(v) if isinstance(v, list) else v) for (s, v) in settings.items()}

    async def fetch_settings_preset(self, setting):
        """Returns a dictonary of valid settings.
        Returns:
            dict -- dictonary of valid settings that can be used
        """
        data = {"randoPreset": setting, "origin": "extStats"}
        try:
            async with aiohttp.request(method='post', url=f'{self.baseurl}/randoPresetWebService', data=data, auth=self.auth, raise_for_status=True) as resp:
                settings = await resp.json(content_type='text/html')
        except aiohttp.client_exceptions.ClientResponseError as e:
            if e.code == 400:
                raise UnableToRetrieve(f'Unable to retrieve settings preset "{setting}".  It may not exist?') from e
            raise
        return settings

    async def fetch_skills_preset(self, skill):
        """Returns a dictonary of valid settings.
        Returns:
            dict -- dictonary of valid settings that can be used
        """
        try:
            async with aiohttp.request(method='post', url=f'{self.baseurl}/presetWebService', data={"preset": skill}, auth=self.auth, raise_for_status=True) as resp:
                settings = await resp.json(content_type='text/html')
        except aiohttp.client_exceptions.ClientResponseError as e:
            if e.code == 400:
                raise UnableToRetrieve(f'Unable to retrieve skill preset "{skill}".  It may not exist?') from e
            raise
        return settings

    @property
    def url(self):
        return f'{self.baseurl}/customizer/{str(self.guid)}'
