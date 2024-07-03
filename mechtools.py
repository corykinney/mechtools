"""
Module with tools for working with Cantera mechanisms.
"""

__version__ = "0.0.1"


import typing
from collections import namedtuple
from collections.abc import Iterable

import cantera as ct


CopyResults = namedtuple("CopyResults", ["copied", "failed"])


def copy_transport_data(
        species: ct.Solution | ct.Species | typing.Iterable[ct.Species],
        reference: str | ct.Solution,
        *,
        overwrite: bool = False
) -> CopyResults:
    """
    Copy transport data from one Solution to another.

    :param species:
    :param reference:
    :param overwrite:
    :return:
    """

    if isinstance(species, ct.Solution):  # Get all species from Solution
        species = species.species()

    if not isinstance(species, Iterable):  # Turn single species into iterable
        species = [species]

    if isinstance(reference, str):  # Load reference mechanism
        reference = ct.Solution(reference)

    copied = []
    failed = []

    for sp in species:
        if overwrite or sp.transport is None:
            try:
                i = reference.species_index(sp.name)
                sp.transport = reference.species(i).transport
                copied.append(sp)
            except ValueError:
                failed.append(sp)

    return CopyResults(copied, failed)


class MechComparison:
    def __init__(self, first: str | ct.Solution, second: str | ct.Solution):
        if isinstance(first, str):
            first = ct.Solution(first)

        if isinstance(second, str):
            second = ct.Solution(second)

        assert isinstance(first, ct.Solution)
        assert isinstance(second, ct.Solution)

        self.first = first
        self.second = second

    @property
    def species_names(self):
        """
        Returns:
            Species only in the first mechanism.
            Species in both mechanisms.
            Species only in the second mechanism.
        """
        first_species = set(self.first.species_names)
        second_species = set(self.second.species_names)

        return (
            first_species - second_species,
            first_species & second_species,
            second_species - first_species
        )
