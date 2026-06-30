import json

import tqdm
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

class Pokemon(object):

    def __init__(self, name, mega=False, variant=False, variant_det = None):
        self.name = name
        self.mega = mega
        self.variant = variant
        self.variant_det = variant_det

    def __str__(self):
        return f"{'Mega ' if self.mega else ''}| {self.name}| {self.variant_det if self.variant and not self.mega else ''}"


def get_gens(dex):
    gens = [[gen['name'], gen['shorthand'].lower()] for gen in dex[0][1]]
    return gens

def get_dex(poke_list):
    dex = []
    for p in poke_list:
        poke_name = p['name']
        if '-' in poke_name:
            variant_det = ' '.join(poke_name.split('-')[1:])
            poke_name = poke_name.split('-')[0]
            variant = True
            mega = False
            if 'Mega' in variant_det:
                mega = True
            dex.append(Pokemon(poke_name, mega=mega, variant=variant, variant_det=variant_det))
        else:
            dex.append(Pokemon(poke_name))
    return dex

def get_dex_from_url(url):
    response = requests.get(url)
    html = response.text
    parser = BeautifulSoup(html, 'html.parser')
    other_gens = parser.find_all('script')
    for script in other_gens:
        if "injectRpcs" in script.text:
            return json.loads(script.text[14:])['injectRpcs']
    return None


def get_smogon_formats_and_main_list():
    dex = get_dex_from_url("https://www.smogon.com/dex/")
    dexes = {}
    gens = get_gens(dex)
    default_gen = json.loads(dex[1][0])[1]['gen']
    poke_list = dex[1][1]['pokemon']
    poke_dex = get_dex(poke_list)
    dexes[default_gen] = poke_dex
    return gens, default_gen, dexes

def get_gen_list(gen):
    dex = get_dex_from_url(f"https://www.smogon.com/dex/{gen}/pokemon")
    poke_list = dex[1][1]['pokemon']
    poke_dex = get_dex(poke_list)
    return poke_dex

def get_all_dexes():
    gens, default_gen, dexes = get_smogon_formats_and_main_list()
    pbar = tqdm(gens)
    pbar.set_description(f"Fetching generations and processing {default_gen}")
    for gen in pbar:
        if gen[1] == default_gen:
            continue
        dexes[gen[1]] = get_gen_list(gen[1])
        pbar.set_description(f"Processing {gen[0]}")
    return dexes, gens



def get_name(n):
    url = "https://pokeapi.co/api/v2/pokemon/{}".format(n)
    response = requests.get(url)
    return response.json()['name']

def get_dex_number(name):
    url = "https://pokeapi.co/api/v2/pokemon/{}".format(name)
    response = requests.get(url)
    return response.json()['number']


if __name__ == '__main__':
    get_all_dexes()