from telegram.files.location import Location
from helpers import Point, MyLocation


loc1 = Location(49.943954, 36.301394)
p1 = Point.from_tg_location(loc1)
print(p1.hash)
loc2 = Location(49.943942, 36.301433)
p2 = Point.from_tg_location(loc2)
print(p2.hash)

loc3 = Location(49.943992, 36.301972)
p3 = Point.from_tg_location(loc3)
print(p3.hash)

print(MyLocation.from_tg_location(loc1).dist(MyLocation.from_tg_location(loc2)))
print(MyLocation.from_tg_location(loc1).dist(MyLocation.from_tg_location(loc3)))

nb = p3.neighbours(15)
hh = set(x.hash for x in nb)
print(hh)
print(hh.union([p3.hash]))

ng = p1.round(50) + Point(25 / 1000, 25 / 1000)

nb = set(x.hash for x in ng.neighbours(26))
print(nb)
print(nb.union([ng.hash]))