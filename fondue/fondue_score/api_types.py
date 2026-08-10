from typing import TypedDict


class NamelessSpecReference(TypedDict):
    url: str


class SpecReference(TypedDict):
    name: str
    url: str


class TypeSpecReference(TypedDict):
    slot: int
    type: SpecReference


class VersionGroupInfo(TypedDict):
    generation: SpecReference
    id: int
    move_learn_methods: list[SpecReference]
    name: str
    order: int
    pokedexes: list[SpecReference]
    regions: list[SpecReference]
    versions: list[SpecReference]


class GenerationInfo(TypedDict):
    id: int
    name: str
    main_region: SpecReference
    moves: list[SpecReference]
    pokemon_species: list[SpecReference]
    types: list[SpecReference]
    version_groups: list[SpecReference]


class MoveMachineSpec(TypedDict):
    machine: NamelessSpecReference
    version_group: SpecReference


class MachineInfo(TypedDict):
    id: int
    item: SpecReference
    move: SpecReference
    version_group: SpecReference


class MetaMoveInfo(TypedDict):
    category: SpecReference
    ailment: SpecReference
    ailment_chance: int
    crit_rate: int
    drain: int
    flinch_chance: int
    healing: int
    min_hits: int | None
    max_hits: int | None
    min_turns: int | None
    max_turns: int | None
    stat_chance: int


class MoveInfo(TypedDict):
    id: int
    name: str
    power: int | None
    accuracy: int | None
    pp: int
    priority: int
    effect_change: int
    machines: list[MoveMachineSpec]
    meta: MetaMoveInfo | None
    damage_class: SpecReference
    type: SpecReference
    target: SpecReference


class TypeInfo(TypedDict):
    id: int
    name: str
    generation: SpecReference
    pokemon: list[SpecReference]
    moves: list[SpecReference]


class StatInfo(TypedDict):
    base_stat: int
    effort: int
    stat: SpecReference


class PastStatInfo(TypedDict):
    generation: SpecReference
    stats: list[StatInfo]


class PastTypeInfo(TypedDict):
    generation: SpecReference
    types: list[TypeSpecReference]


class PokemonInfo(TypedDict):
    id: int
    name: str
    species: SpecReference
    types: list[TypeSpecReference]
    past_types: list[PastTypeInfo]
    forms: list[SpecReference]
    moves: list[SpecReference]
    is_default: bool
    base_experience: int
    height: int
    weight: int
    stats: list[StatInfo]
    past_stats: list[PastStatInfo]


class PokemonSpeciesVarietyInfo(TypedDict):
    is_default: bool
    pokemon: SpecReference


class PokemonSpeciesInfo(TypedDict):
    id: int
    name: str
    order: int
    evolution_chain: NamelessSpecReference
    evolves_from_species: SpecReference
    varieties: list[PokemonSpeciesVarietyInfo]
    shape: SpecReference
    forms_switchable: bool
    gender_rate: int
    has_gender_differences: bool
    generation: SpecReference
    growth_rate: SpecReference
    hatch_counter: int
    egg_groups: list[SpecReference]
    is_baby: bool
    is_legendary: bool
    is_mythical: bool
