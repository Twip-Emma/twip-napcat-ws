from .config import petpet_config
from .functions import *

memes = [
    
    Meme("do", do, ("撅",)),
    Meme("shoot", shoot, ("射",)),
]

memes = [meme for meme in memes if meme.name not in petpet_config.petpet_disabled_list]
