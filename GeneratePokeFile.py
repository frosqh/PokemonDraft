import json
import time
import requests
import concurrent.futures
from bs4 import BeautifulSoup
from tqdm import tqdm


class Pokemon(object):
    def __init__(self, name, mega=False, variant=False, variant_det=None):
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
            mega = 'Mega' in variant_det
            dex.append(Pokemon(poke_name, mega=mega, variant=variant, variant_det=variant_det))
        else:
            dex.append(Pokemon(poke_name))
    return dex


def get_dex_data(url, pbar, chunk_size):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(requests.get, url)

        current_chunk_progress = 0
        max_simulated = chunk_size * 0.95

        while not future.done():
            step = (max_simulated - current_chunk_progress) / 10

            if step > 0.05:
                safe_step = max(0, min(step, pbar.total - pbar.n))
                if safe_step > 0:
                    current_chunk_progress += safe_step
                    pbar.update(safe_step)

            time.sleep(0.1)

        response = future.result()
        remaining = chunk_size - current_chunk_progress

        safe_remaining = max(0, min(remaining, pbar.total - pbar.n))
        if safe_remaining > 0:
            pbar.update(safe_remaining)

    html = response.text
    parser = BeautifulSoup(html, 'html.parser')
    for script in parser.find_all('script'):
        if "injectRpcs" in script.text:
            return json.loads(script.text[14:])['injectRpcs']
    return None


def get_all_dexes():
    dexes = {}

    pbar = tqdm(
        total=100,
        desc="Downloading...",
        bar_format="{desc}: {percentage:3.0f}%|{bar}| {unit}]",
        colour="white"
    )

    pbar.unit = "Initialisation"
    dex = get_dex_data("https://www.smogon.com/dex/", pbar, chunk_size=10.0)

    gens = get_gens(dex)
    default_gen = json.loads(dex[1][0])[1]['gen']
    poke_list = dex[1][1]['pokemon']
    dexes[default_gen] = get_dex(poke_list)

    remaining_gens = [g for g in gens if g[1] != default_gen]

    chunk_per_gen = 90.0 / len(remaining_gens)

    for gen in remaining_gens:
        gen_name, gen_shorthand = gen
        pbar.unit = f"{gen_name}"

        gen_dex_data = get_dex_data(f"https://www.smogon.com/dex/{gen_shorthand}/pokemon", pbar,
                                    chunk_size=chunk_per_gen)
        if gen_dex_data:
            gen_poke_list = gen_dex_data[1][1]['pokemon']
            dexes[gen_shorthand] = get_dex(gen_poke_list)

    pbar.unit = "Done !"
    pbar.close()
    return dexes, gens


if __name__ == '__main__':
    all_dexes, all_gens = get_all_dexes()