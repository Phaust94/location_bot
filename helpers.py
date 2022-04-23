"""
Helper functions for location bot
"""

from __future__ import annotations

import copy
import typing
from dataclasses import dataclass

from telegram.files.location import Location
import geopy.distance

__all__ = [
    "Point",
]


class MyLocation(Location):

    def as_tuple(self) -> typing.Tuple[float, float]:
        return self.latitude, self.longitude

    def dist(self, other: MyLocation) -> float:
        res = geopy.distance.geodesic(
            self.as_tuple(),
            other.as_tuple()
        ).km
        return res

    @classmethod
    def from_tg_location(cls, tg_location: Location) -> MyLocation:
        inst = cls(tg_location.latitude, tg_location.longitude, tg_location.horizontal_accuracy)
        return inst


@dataclass
class Point:
    x: float
    y: float

    @classmethod
    def from_tg_location(cls, location: Location):
        location = MyLocation.from_tg_location(location)
        loc_x = copy.deepcopy(location)
        loc_x.latitude = 0
        x = loc_x.dist(location)
        loc_y = copy.deepcopy(location)
        loc_y.longitude = 0
        y = loc_y.dist(location)
        inst = cls(x, y)
        return inst
