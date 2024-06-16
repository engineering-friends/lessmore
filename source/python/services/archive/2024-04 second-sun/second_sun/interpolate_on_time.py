import numpy as np


def interpolate_on_time(time_and_values: list, target_time: str) -> float:
    """
    Interpolate values on time.

    Inputs are day times, which are cyclic.

    Parameters
    ----------
    time_and_values : list[tuple]
        List of tuples with time (%H:%M) and value
    target_time : str
        Target time in %H:%M:%S format, for which to interpolate the value.
    """

    # - Prepare inputs, sort, convert to seconds, shift to start from 0

    # -- Sort

    time_and_values = sorted(time_and_values, key=lambda x: x[0])

    # -- Convert to seconds

    time_and_values = [
        [(int(time.split(":")[0]) * 3600 + int(time.split(":")[1]) * 60) % 86400, value]
        for time, value in time_and_values
    ]
    target_time = (int(target_time.split(":")[0]) * 3600 + int(target_time.split(":")[1]) * 60) % 86400

    # - Add full previous and next cycle so that interpolation works correctly

    time_and_values = (
        [[time - 86400, value] for time, value in time_and_values]
        + time_and_values
        + [[time + 86400, value] for time, value in time_and_values]
    )

    # - Return interpolated value

    return float(np.interp(target_time, [time for time, _ in time_and_values], [value for _, value in time_and_values]))


def test():
    assert interpolate_on_time(time_and_values=[["00:00", 0], ["01:00", 1]], target_time="00:30") == 0.5
    assert interpolate_on_time(time_and_values=[["23:30", 0], ["00:30", 1]], target_time="00:00") == 0.5


if __name__ == "__main__":
    test()
