import webbrowser
from random import choice, sample

from InquirerLib import prompt

from GeneratePokeFile import get_all_dexes, Pokemon

VERSION = 0.1


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
        for _team in range(6):
            choices = []
            for _poke in range(3):
                drawn: Pokemon = choice(dex)
                dex.remove(drawn)
                choices.append(drawn)
            for i, c in enumerate(choices):
                print(f"{'1st' if i == 0 else ('2nd' if i == 1 else ('3rd' if i == 2 else str(i)+'th'))} choice is : {c.name}")
                if c.variant and not c.mega:
                    print(f"/!\\ {c.name} is a variant : {c.variant_det}")
                if c.mega:
                    print(f"/!\\ {c.name} is a mega !")
                webbrowser.open_new_tab('https://bulbapedia.bulbagarden.net/wiki/'+c.name)
            input('Press Enter to continue...')
    else:
        pokes = sample(dex, k=10)
        for poke in pokes:
            webbrowser.open_new_tab('https://bulbapedia.bulbagarden.net/wiki/'+poke.name)
            if poke.variant and not poke.mega:
                print(f"/!\\ {poke.name} is a variant : {poke.variant_det}")
            if poke.mega:
                print(f"/!\\ {poke.name} is a mega !")