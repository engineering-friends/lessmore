import numpy as np


""" Find maximum profit. You have to take at least k losses, but can't go negative.

If can't - return -1

"""


def dp(
    prev_profits: list[int],
    new_profits: list[int],
    pnl: list[int],
    i: int,
    k: int,
) -> int:
    # - edge cases
    if i == 0:
        if k == 0:
            if pnl[0] >= 0:
                return pnl[0]
            else:
                return -1
        elif k == 1:
            if pnl[0] >= 0:
                return -1
            else:
                return 0

    if i <= k - 2:
        return -1  # can't take k losses in less than k days

    # - Main logic

    if pnl[i] >= 0:
        if new_profits[i - 1] == -1:
            return -1
        else:
            return new_profits[i - 1] + pnl[i]
    else:
        # try to take upper ones
        new_values = []
        if new_profits[i - 1] == -1:
            new_values.append(-1)
        else:
            new_values.append(new_profits[i - 1])

        if prev_profits[i - 1] == -1:
            new_values.append(-1)
        else:
            new_values.append(prev_profits[i - 1] + pnl[i])

        return max(new_values + [-1])


def get_max_profit(pnl: list[int], k: int) -> int:
    """Find maximum profit. We have to take at least k losses, but can't go negative.

    If can't - return -1

    """
    print("Pnl:", pnl, "k:", k)
    debug_values = [pnl]
    debug_values += [[0] * len(pnl)]
    prev_profits = [0] * len(pnl)
    new_profits = [0] * len(pnl)
    for _k in range(k + 1):
        for i in range(len(pnl)):
            new_profits[i] = dp(prev_profits=prev_profits, new_profits=new_profits, pnl=pnl, i=i, k=_k)
        prev_profits = new_profits.copy()
        new_profits = [0] * len(pnl)
        debug_values.append(prev_profits)

    print(np.array(debug_values).T)
    return max(prev_profits)


def test():
    # - Final function

    print(get_max_profit(pnl=[1, 2, 3, 4, 5], k=2))
    print(get_max_profit(pnl=[1, 2, 3, -3, -2], k=2))
    print(get_max_profit(pnl=[-1, 1, 2, 3, -3, -2], k=2))


if __name__ == "__main__":
    test()
