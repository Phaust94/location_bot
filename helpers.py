"""
Helper functions for location bot
"""

from __future__ import annotations

import copy
import itertools
import typing
from dataclasses import dataclass
import hashlib

from geopy import Point
from telegram.files.location import Location
import geopy.distance

from constants import ACCURACY_METERS, DIGEST_LENGTH
from secrets import SALT

__all__ = [
    "Point",
    "MyLocation",
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
        inst = cls(tg_location.longitude, tg_location.latitude, tg_location.horizontal_accuracy)
        return inst


@dataclass
class Point:
    x_km: float
    y_km: float

    @classmethod
    def from_tg_location(cls, location: Location):
        location = MyLocation.from_tg_location(location)
        loc_x = copy.deepcopy(location)
        loc_x.latitude = 0
        x = loc_x.dist(location) * (1 if location.latitude > 0 else -1)
        loc_y = copy.deepcopy(location)
        loc_y.longitude = 0
        y = loc_y.dist(location) * (1 if location.longitude > 0 else -1)
        inst = cls(x, y)
        return inst

    @staticmethod
    def _round(value: float, precision: int) -> float:
        return ((value * 1000) // precision) * precision / 1000

    def round(self, precision: int = ACCURACY_METERS) -> Point:
        x = self._round(self.x_km, precision)
        y = self._round(self.y_km, precision)

        # noinspection PyArgumentList
        inst = self.__class__(x, y)
        return inst

    def __str__(self):
        return f"Point(x={self.x_km}, y={self.y_km})"

    @property
    def hash(self):
        rounded = self.round()
        to_hash = f"{rounded!s}_{SALT}"
        m = hashlib.sha256()
        m.update(to_hash.encode())
        digest = m.hexdigest()[:DIGEST_LENGTH]
        return digest

    def __add__(self, other: Point) -> Point:
        # noinspection PyArgumentList
        inst = self.__class__(self.x_km + other.x_km, self.y_km + other.y_km)
        return inst

    def __mul__(self, other: float) -> Point:
        # noinspection PyArgumentList
        pt = self.__class__(self.x_km * other, self.y_km * other)
        return pt

    def __rmul__(self, other: float) -> Point:
        return self * other

    def neighbours(self, radius_meters: float, n: int = 1) -> typing.List[Point]:
        offsets = list(range(-n, n + 1))
        vectors = itertools.product(offsets, repeat=2)
        vectors_scaled = [radius_meters / 1000 * Point(*v) for v in vectors]
        neighb = [self + direction for direction in vectors_scaled]
        return neighb
