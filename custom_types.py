from dataclasses import dataclass
from typing import List


@dataclass
class Vector:
    x: float
    y: float
    z: float


@dataclass
class MeasurementsChunk:
    t: List[float]
    x: List[float]
    y: List[float]
    z: List[float]

    def extend(self, new: 'MeasurementsChunk') -> None:
        self.t.extend(new.t)
        self.x.extend(new.x)
        self.y.extend(new.y)
        self.z.extend(new.z)

    def drop_older_than(self, n) -> None:
        self.t = self.t[-n:]
        self.x = self.x[-n:]
        self.y = self.y[-n:]
        self.z = self.z[-n:]


