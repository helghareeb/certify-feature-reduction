"""The retention rule is load-bearing for R1.1 -- pin its exact semantics, including the
two properties that must NOT be 'fixed': the >=1 floor and banker's rounding."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nsclinfs.reduction import retained_k


def test_retained_k_full_table():
    # dataset p -> k at fracs (1.0, 0.75, 0.5, 0.33, 0.25); verified against the v1 grid
    table = {
        3: (3, 2, 2, 1, 1),      # haberman: 0.33 and 0.25 are the SAME one-feature model
        5: (5, 4, 2, 2, 1),      # mammographic: 0.5*5=2.5 rounds to 2 (banker's), floor at 0.25
        8: (8, 6, 4, 3, 2),
        9: (9, 7, 4, 3, 2),      # 4.5 -> 4
        11: (11, 8, 6, 4, 3),    # 5.5 -> 6
        12: (12, 9, 6, 4, 3),
        16: (16, 12, 8, 5, 4),
        18: (18, 14, 9, 6, 4),   # 4.5 -> 4
        30: (30, 22, 15, 10, 8), # 22.5 -> 22; 7.5 -> 8
        44: (44, 33, 22, 15, 11),
    }
    fracs = (1.0, 0.75, 0.5, 0.33, 0.25)
    for p, ks in table.items():
        got = tuple(retained_k(f, p) for f in fracs)
        assert got == ks, f"p={p}: {got} != {ks}"


def test_floor_never_below_one():
    for p in (1, 2, 3, 5):
        for f in (0.01, 0.1, 0.25):
            assert retained_k(f, p) >= 1


def test_bankers_rounding_edges():
    assert retained_k(0.5, 5) == 2       # 2.5 -> 2, not 3
    assert retained_k(0.75, 30) == 22    # 22.5 -> 22
    assert retained_k(0.25, 18) == 4     # 4.5 -> 4
    assert retained_k(0.5, 11) == 6      # 5.5 -> 6
