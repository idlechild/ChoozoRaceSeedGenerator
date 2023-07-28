import json
import os
from os import system
from pyz3r.smvaria import SuperMetroidVaria


class ChoozoException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__("ChoozoException")


class VariaGenerator(SuperMetroidVaria):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.debugdefaults = False
        self.debugsettings = False
        self.debugskills = False


    async def get_default_settings(self):
        settings = await super().get_default_settings()
        if self.debugdefaults:
            debug_text = self.debug_settings_to_text(settings)
            raise ChoozoException("VariaGenerator Defaults:\n%s" % debug_text)
        return settings


    async def get_settings(self):
        settings = await super().get_settings()
        if self.debugsettings:
            debug_text = self.debug_settings_to_text(settings)
            raise ChoozoException("VariaGenerator Settings:\n%s" % debug_text)
        elif self.debugskills:
            debug_text = self.debug_skills_to_text(settings["paramsFileTarget"], "")
            raise ChoozoException("VariaGenerator Skills:\n%s" % debug_text)
        return settings


    def debug_settings_to_text(self, settings):
        debug_text = ""
        for key, value in sorted(settings.items()):
            if key != "paramsFileTarget":
                debug_text += "%s: %s\n" % (key, value)
            elif not self.debugskills:
                debug_text += "%s: %s\n" % (key, self.settings_preset)
            else:
                debug_text += "%s: {\n" % key
                debug_text += self.debug_skills_to_text(value, "        ")
                debug_text += "}\n"
        return debug_text


    def debug_skills_to_text(self, skills, indent):
        debug_text = ""
        debug_skills_data = json.loads(skills)
        for key, value in sorted(debug_skills_data.items()):
            if not isinstance(value, dict):
                debug_text += "%s%s: %s\n" % (indent, key, value)
            else:
                debug_text += "%s%s: {\n" % (indent, key)
                for k, v in sorted(value.items()):
                    debug_text += "%s        %s: %s\n" % (indent, k, v)
                debug_text += "%s}\n" % indent
        return debug_text


async def validate_arguments(args, minArgs, maxArgs, argsDescription):
    if (len(args) < minArgs) or ((maxArgs >= 0) and (len(args) > maxArgs)):
        argumentsProvided = "%s %s provided" % (len(args), "argument" if 1 == len(args) else "arguments")
        raise ChoozoException("%s, %s" % (argumentsProvided, argsDescription))


async def validate_choozo_params(split, area, boss, difficulty, escape, morph, start):
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


async def generate_choozo_seed(race, split, area, boss, difficulty, escape, morph, start):
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

    return await generate_smvaria_seed(settingsPreset, skillsPreset, race, settingsDict)


async def generate_smvaria_seed(settingsPreset, skillsPreset, race, settingsDict):
    seed = await VariaGenerator.create(
        settings_preset=settingsPreset,
        skills_preset=skillsPreset,
        race=race,
        settings_dict=settingsDict,
        raise_for_status=False
    )

    if not hasattr(seed, 'guid'):
        raise ChoozoException("Error: %s" % seed.data)

    return seed


async def parse_smvaria_warnings(seed):
    warnings = []
    errorMsg = seed.data.get('errorMsg', '')
    if len(errorMsg) > 0:
        warnings = errorMsg.replace("<br/>", "\n").rstrip().split('\n')
    return warnings

