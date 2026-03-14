from typing import List

from statistics import mean


def moving_average(values: List[float], window: int = 3) -> float:
    if not values:
        return 0.0
    return mean(values[-window:])
