from typing import Tuple

def expected_score(rating_a: float, rating_b: float) -> float:
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

def update_elo(rating_a: float, rating_b: float, outcome: float, k=32) -> Tuple[float, float]:
    e_a = expected_score(rating_a, rating_b)
    e_b = expected_score(rating_b, rating_a)
    new_a = rating_a + k * (outcome - e_a)
    new_b = rating_b + k * ((1 - outcome) - e_b)
    return new_a, new_b