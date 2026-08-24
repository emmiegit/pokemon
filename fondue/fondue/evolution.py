import logging

from .api_types import EvolutionChainHead, EvolutionChainInfo, EvolutionChainLink

logger = logging.getLogger(__name__)


def is_fully_evolved(
    species_name: str,
    chain_head: EvolutionChainHead,
) -> bool:
    chain = chain_head["chain"]

    # Species that never evolves
    if not chain["evolves_to"]:
        # We could just call the recursive helper,
        # but we have this check to ensure the user
        # didn't pass in the evolution chain for the
        # wrong mon (then it'll give wrong answers)
        if chain["species"]["name"] != species_name:
            raise ValueError(species_name)

        return True

    return _is_fully_evolved(species_name, chain)


def _is_fully_evolved(
    species_name: str,
    chain: EvolutionChainInfo | EvolutionChainLink,
) -> bool:
    if chain["species"]["name"] == species_name:
        # if there are still paths, then it's not fully evolved
        return not chain["evolves_to"]

    # otherwise, recursively check each evolution path
    for link in chain["evolves_to"]:
        if _is_fully_evolved(species_name, link):
            return True

    return False
