import os
import webbrowser
from random import choice, sample

from InquirerLib import prompt

from GeneratePokeFile import get_all_dexes, Pokemon

from termcolor import colored

os.system("color")

VERSION = 0.1

def complete_space(s, l):
    if l > len(s):
        prespace = (l - len(s)) // 2
        postspace = l - len(s) - prespace
        s = " " * prespace + s + postspace * " "
        return s
    return s

def print_choices(tab):
    lengths = [max(len("1st Pokémon"),max([len(y)+2 for y in x])) for x in tab]
    titles = []
    title_lengths = []
    for i in range(6):
        l = lengths[i] if i < len(lengths) else 0
        prefix = "1st" if i == 0 else "2nd" if i == 1 else "3rd" if i == 2 else f"{i+1}th"
        title = f" {prefix} Pokémon "
        title = complete_space(title, l)
        title_lengths.append(len(title))
        title = (colored(title, 'green') if i == len(lengths) - 1 else title)
        titles.append(title)
    header = "|" + "|".join(titles) + "|"
    header_line = "| " + " | ".join(["-" *(x-2) for x in title_lengths]) + " |"
    print(header)
    print(header_line)
    for i in range(3):
        pokemons = []
        for j in range(6):
            pokemon = tab[j][i] if j < len(tab) else "---"
            pokemon = complete_space(str(pokemon), title_lengths[j])
            pokemons.append(pokemon)
        line = "|" + "|".join(pokemons) + "|"
        print(line)


if __name__ == '__main__':

    dexes, gens = get_all_dexes()
    gens_dict = dict(gens)

    questions = [
        {
            "type": "list",
            "message": "Which generation?",
            "choices": [g[0] for g in gens],
            "multiselect": False,
            "name": "gen"
        },
        {
            "type": "list",
            "message": "Which mode?",
            "choices": ["Draft", "Stack"],
            "multiselect": False,
            "name": "mode"
        },
    ]

    result = prompt(questions)
    gen = gens_dict[result["gen"]]
    mode = result["mode"]
    dex = dexes[gen]

    if mode == "Draft":
        team_choices = []
        for team in range(6):
            choices = []
            for _poke in range(3):
                drawn: Pokemon = choice(dex)
                dex.remove(drawn)
                choices.append(drawn)
            team_choices.append(choices)
            print_choices(team_choices)
            for c in choices:
                webbrowser.open_new_tab('https://bulbapedia.bulbagarden.net/wiki/' + c.name)
            questions = [
                {
                    "type": "list",
                    "message": "Reroll or continue? (Press space to select multiple choices)",
                    "choices": ["Continue", "Reroll 1st choice", "Reroll 2nd choice", "Reroll 3rd choice"],
                    "multiselect": True,
                    "name": "reroll"
                },
            ]
            while True:
                result = prompt(questions)
                if result["reroll"] == ["Continue"]:
                    break
                if "Reroll 1st choice" in result["reroll"]:
                    choices[0] = choice(dex)
                    dex.remove(choices[0])
                if "Reroll 2nd choice" in result["reroll"]:
                    choices[1] = choice(dex)
                    dex.remove(choices[1])
                if "Reroll 3rd choice" in result["reroll"]:
                    choices[2] = choice(dex)
                    dex.remove(choices[2])
                team_choices.pop()
                team_choices.append(choices)
                print_choices(team_choices)
                for c in choices:
                    webbrowser.open_new_tab('https://bulbapedia.bulbagarden.net/wiki/' + c.name)
    else:
        pokes = sample(dex, k=10)
        for poke in pokes:
            webbrowser.open_new_tab('https://bulbapedia.bulbagarden.net/wiki/' + poke.name)
            if poke.variant and not poke.mega:
                print(f"/!\\ {poke.name} is a variant : {poke.variant_det}")
            if poke.mega:
                print(f"/!\\ {poke.name} is a mega !")
