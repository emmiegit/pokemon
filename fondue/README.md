## Fondue Scoring

A calculation of the overall risk associated with each Pokémon type, as it applies in [Ironmon](https://ironmon.gg). So named as comes from an idea from [Cheezinator](https://www.twitch.tv/cheezinator), and represents an analysis of the "mix" of all the moves of that type. This is then multiplied by the average BST of Pokémon with that type to factor in STAB.

Then, based on this, we can determine the best defensive types for reducing overall danger from enemy attacks.

Uses [PokéAPI](https://pokeapi.co/) for data. Designed for Generation IV, but may work for other generations.

Description of methodology to follow.

### Execution

```sh
python -m fondue [game]
```

Give the name of the game / version group, with some abbreviations accepted. For instance, `platinum` for Platinum or `hgss` for HeartGold/SoulSilver.

### Development

For formatting, linting, etc.:

```sh
$ ruff format fondue
$ ruff check fondue
$ mypy fondue_score
```
