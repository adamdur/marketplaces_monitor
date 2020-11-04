import os

DB_HOST = "<HOST>"
DB_PORT = "<PORT>"
DB_DATABASE = "<DB>"
DB_USER = "<USER>"
DB_PW = "<PW>"

# The prefix that will be used to parse commands.
# It doesn't have to be a single character!
COMMAND_PREFIX = "?"

# The bot token. Keep this secret!
BOT_TOKEN = "<BOT_TOKEN>"
BOT_USER_TOKEN = "<BOT_USER_TOKEN>"

BOT_NAME = "MARKETPLACES MONITOR BY SMYB"
BOT_URL = "https://discord.gg/hmmRweZh"

# The now playing game. Set this to anything false-y ("", None) to disable it
NOW_PLAYING = "with Bot Markets"

# Base directory. Feel free to use it if you want.
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
SETUP_FILE = os.path.dirname(os.path.realpath(__file__)) + '/json_setup.json'
SETUP_DIR = os.path.dirname(os.path.realpath(__file__)) + '/setup'
INIT_SETUP_DATA = {
    "channels": {},
    "setup": {}
}

MODERATOR_ROLE = 'SMYBOTMODERATOR'
ALLOWED_ROLES = ['admin', 'owner', 'smybotmoderator']

DEFAULT_CHANNEL_CATEGORY = 'SMYBOT MONITORS'
DEFAULT_SETUP_CHANNEL = 'setup-channel'
DEFAULT_WATCHER_CHANNEL = '<DEFAULT_CHANNEL>' # int value

ALLOWED_CHANNEL_TYPES = ['wts', 'wtb', 'wtt', 'wtr', 'wtro']
CHANNELS_IDENTIFIERS = ['wts-', 'wtb-', 'wtt-', 'wtr-', 'wtro-', '-buy', '-sell', '-trade', '-rental']
CHANNELS_NEGATIVE_IDENTIFIERS = ['other', 'items', 'staff', 'only', 'membership', 'roboflips', 'clothing', 'shoes', 'proxies', 'boosters', 'notify', 'signal', 'apparel', 'funko', 'digital', 'physical', 'bulk', 'bots']
ALLOWED_BOTS = {
    'adept': ['adept'],
    'anb': ['anb'],
    'balko': ['balko'],
    'bnb': ['bnb'],
    'burst': ['burst'],
    'candypreme': ['candypreme'],
    'cyber': ['cyber'],
    'dashe': ['dashe'],
    'deadsuite': ['deadsuite'],
    'dragon': ['dragon'],
    'esnkrs': ['esnkrs'],
    'estock': ['estock'],
    'eve': ['eve'],
    'f3': ['f3', 'f3ather'],
    'flare': ['flare'],
    'fleek': ['fleek'],
    'flow_gizmo': ['flow_gizmo', 'flow-gizmo'],
    'galaxsio': ['galaxsio'],
    'ganesh': ['ganesh'],
    'hawkmesh': ['hawkmesh'],
    'hayha': ['hayha'],
    'kickmoji': ['kickmoji'],
    'kilo': ['kilo'],
    'kodai': ['kodai'],
    'launcher': ['launcher'],
    'mango': ['mango'],
    'mbot': ['mbot'],
    'mek': ['mek', 'mekpreme'],
    'mekaio': ['mekaio'],
    'mercury': ['mercury'],
    'nike_bots': ['nike_bots', 'nike-bot'],
    'pd': ['pd'],
    'phantom': ['phantom', 'ghost-phantom'],
    'phasma': ['phasma'],
    'phoenix': ['phoenix', 'phoenix-aio'],
    'polaris': ['polaris'],
    'prism': ['prism'],
    'pulsar': ['pulsar'],
    'qbot': ['qbot'],
    'reaio': ['reaio'],
    'rush': ['rush', 'rushaio'],
    's_chrysant': ['s_chrysant', 's-chrysant'],
    'sf': ['sf', 'splashforce'],
    'sicko': ['sicko'],
    'sieupreme': ['sieupreme', 'backdoor', 'backdoorio'],
    'sole': ['sole', 'soleaio'],
    'solyd': ['solyd'],
    'sypion': ['sypion'],
    'tks': ['tks'],
    'tohru': ['tohru'],
    'torpedo': ['torpedo'],
    'valor': ['valor'],
    'velox': ['velox'],
    'wrath': ['wrath'],
    'zeny': ['zeny'],
}
