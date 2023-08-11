import time

from dataclasses import dataclass
from typing import Optional

import pandas as pd
import pytest


@dataclass
class Lap:
    start_at: float
    stop_at: Optional[float] = None


class StopWatch:
    """Time measurement of any code piece."""

    def __init__(
        self,
        max_laps_per_key=100_000,
    ):
        self.max_laps_per_key = max_laps_per_key
        self.laps_by_key = {}  #  # {key: [(start_time, end_time), ...]}

        self.enabled = True

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def reset(self):
        self.laps_by_key = {}

    def start(self, key: str = "default") -> "StopWatch":
        # - Return if disabled

        if not self.enabled:
            return self

        # - Start key

        t = time.time()

        if key in self.laps_by_key.keys():
            if self.laps_by_key[key][-1].stop_at is None:
                raise Exception(f"Clock {key} is already running")
            else:
                # - Add new lap

                self.laps_by_key[key].append(Lap(start_at=t))

                # - Remove old laps if needed

                self.laps_by_key[key] = self.laps_by_key[key][-self.max_laps_per_key :]
        else:
            self.laps_by_key[key] = [Lap(start_at=t)]

        return self

    def stop(self, key: Optional[str] = None) -> "StopWatch":
        # - Return if disabled

        if not self.enabled:
            return self

        # - Stop all if key is None and return

        if key is None:
            for key in self.laps_by_key.keys():
                self.stop(key)
            return self

        # - Stop non-None key

        t = time.time()

        if key not in self.laps_by_key:
            # not started

            return self
        elif self.laps_by_key[key][-1].stop_at is None:
            # stop last lap

            self.laps_by_key[key][-1] = Lap(
                start_at=self.laps_by_key[key][-1].start_at,
                stop_at=t,
            )

        return self

    def stats(self) -> pd.DataFrame:
        # - Stop

        self.stop()

        # - Empty clock

        if not self.laps_by_key:
            return pd.DataFrame(index=["count", "mean", "sum", "max", "min"])

        # - Compute stats

        df = pd.concat(
            [
                pd.DataFrame({key: [lap.stop_at - lap.start_at for lap in laps]})
                for key, laps in self.laps_by_key.items()
            ],
            ignore_index=True,
            axis=1,
        )
        df.columns = self.laps_by_key.keys()
        stats_df = df.agg(["count", "mean", "sum", "max", "min"])
        return stats_df

    def __getitem__(self, item):
        return self.stats().T["sum"][item]


# global clock instance
clock = StopWatch()


@pytest.mark.slow
def test():
    # Usage 1
    clock = StopWatch()

    print(clock.stats())

    # Start clock
    clock.start("first")
    time.sleep(0.1)

    # Stop clock
    clock.stop("first")

    clock.start("second")
    time.sleep(0.2)
    clock.stop("second")

    # This will add statistics to the 'first' key
    clock.start("first")
    time.sleep(0.1)
    clock.stop("first")

    print(clock.stats())

    # Check max laps
    clock = StopWatch(max_laps_per_key=3)
    for i in range(10):
        clock.start("a")
        time.sleep(0.01 * i)
        clock.stop("a")
    print(clock.stats())


if __name__ == "__main__":
    test()
