import os
from os import system
from pyz3r.smvaria import SuperMetroidVaria


class ChoozoException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__("ChoozoException")


async def validate_choozo(split, area, boss, difficulty, escape, morph, start):
    if split not in ['FullCountdown', 'M/m', 'RandomSplit']:
        raise ChoozoException("Invalid item split setting.  Must be FullCountdown, M/m or RandomSplit.")

    if area not in ['FullArea', 'LightArea', 'VanillaArea']:
        raise ChoozoException("Invalid area setting.  Must be FullArea, LightArea or VanillaArea.")

    if boss not in ['RandomBoss', 'VanillaBoss']:
        raise ChoozoException("Invalid boss setting.  Must be RandomBoss or VanillaBoss.")

    if difficulty not in ['VeryHardDifficulty', 'HarderDifficulty', 'HardDifficulty', 'MediumDifficulty', 'EasyDifficulty', 'BasicDifficulty']:
        raise ChoozoException("Invalid difficulty setting.  Must be VeryHardDifficulty, HarderDifficulty, HardDifficulty, MediumDifficulty, EasyDifficulty or BasicDifficulty.")

    if escape not in ['RandomEscape', 'VanillaEscape']:
        raise ChoozoException("Invalid escape setting.  Must be RandomEscape or VanillaEscape.")

    if morph not in ['LateMorph', 'RandomMorph', 'EarlyMorph']:
        raise ChoozoException("Invalid morph setting.  Must be LateMorph, RandomMorph or EarlyMorph.")

    if start not in ['DeepStart', 'RandomStart', 'NotDeepStart', 'ShallowStart', 'VanillaStart']:
        raise ChoozoException("Invalid start setting.  Must be DeepStart, RandomStart, NotDeepStart, ShallowStart or VanillaStart.")


async def generate_choozo(race, split, area, boss, difficulty, escape, morph, start):
    splitDict = {
        "FullCountdown": "FullWithHUD",
        "M/m": "Major",
        "RandomSplit": "random"
    }

    difficultyDict = {
        "VeryHardDifficulty": "harder",
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

    settingsPreset = "Season_Races"
    skillsPreset = "newbie" if difficulty == "BasicDifficulty" else "Season_Races"
    settingsDict = {
        "hud": "on",
        "suitsRestriction": "off",
        "variaTweaks": "on",

        "majorsSplit": splitDict[split],
        "majorsSplitMultiSelect": ['FullWithHUD', 'Major'],

        "areaRandomization": "full" if area == "FullArea" else "light" if area == "LightArea" else "off",
        "areaLayout": "off" if area == "VanillaArea" else "on",

        "bossRandomization": "off" if boss == "VanillaBoss" else "on",

        "maxDifficulty": difficultyDict[difficulty],

        "escapeRando": "off" if escape == "VanillaEscape" else "on",

        "morphPlacement": morphDict[morph],

        "startLocation": "Landing Site" if start == "VanillaStart" else "random",
        "startLocationMultiSelect": startDict[start]
    }

    return await generate_smvaria(settingsPreset, skillsPreset, race, settingsDict)


async def generate_smvaria(settingsPreset, skillsPreset, race, settingsDict):
    seed = await SuperMetroidVaria.create(
        settings_preset=settingsPreset,
        skills_preset=skillsPreset,
        race=race,
        settings_dict=settingsDict,
        raise_for_status=False
    )

    if not hasattr(seed, 'guid'):
        raise ChoozoException("Error: %s" % seed.data)

    return seed

