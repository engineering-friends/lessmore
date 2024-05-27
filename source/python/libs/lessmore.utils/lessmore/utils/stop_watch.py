import time

from dataclasses import dataclass
from typing import Callable, Literal, Optional

import pandas as pd
import pytest


@dataclass
class Lap:
    start_at: float
    stop_at: Optional[float] = None


class StopWatch:
    """Simple profiler with stop watch mechanism"""

    def __init__(
        self,
        max_laps_per_key: int = 100_000,
        time_func: Callable = time.perf_counter,
    ):
        self.max_laps_per_key = max_laps_per_key
        self.laps_by_key: dict[str, list[Lap]] = {}
        self.enabled = True
        self.time_func = time_func

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def reset(self):
        self.laps_by_key = {}

    def start(self, key: str = "") -> "StopWatch":
        # - Return if disabled

        if not self.enabled:
            return self

        # - Init key with empty list if not exists

        self.laps_by_key.setdefault(key, [])

        # - Start new lap if last lap is stopped or not exists

        if not self.laps_by_key[key] or self.laps_by_key[key][-1].stop_at is not None:
            self.laps_by_key[key].append(Lap(start_at=self.time_func()))

        # - Remove oldest laps if max_laps_per_key is reached

        self.laps_by_key[key] = self.laps_by_key[key][-self.max_laps_per_key :]

        # - Return

        return self

    def stop(
        self,
        key: Optional[str] = None,  # stop all if None
    ) -> "StopWatch":
        # - Return if disabled

        if not self.enabled:
            return self

        # - Stop all if key is None and return

        if key is None:
            for laps in self.laps_by_key.values():
                if laps[-1].stop_at is None:
                    laps[-1].stop_at = self.time_func()
            return self

        # - Return if not started

        if key not in self.laps_by_key or self.laps_by_key[key][-1].stop_at is not None:
            # not started
            return self

        # - Stop last lap

        self.laps_by_key[key][-1].stop_at = self.time_func()

        # - Return

        return self

    def stats(self) -> pd.DataFrame:
        # - Stop all

        self.stop(key=None)

        # - Empty stop_watch

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
        return df.agg(["count", "mean", "sum", "max", "min"])


# global stop_watch instance
stop_watch = StopWatch()


@pytest.mark.slow
def test():
    stop_watch = StopWatch()
    for i in range(10):
        stop_watch.start(key=str(i % 2))
        time.sleep(0.01)
        stop_watch.stop(key=str(i % 2))
    print(stop_watch.stats())


if __name__ == "__main__":
    test()
