from functools import cache

""" Find maximum profit. You have to take at least k losses, but can't go negative.

If can't - return -1

       Time: 0 .. T 
losses:    0 
           .
           .
           K
           
"""


@cache
def dp(
    pnl: tuple,
    t: int,
    losses: int,
) -> int:
    # - Edge case

    if t == 0:
        if losses == 0:
            if pnl[0] >= 0:
                return pnl[0] # take the profit
            else:
                return 0 # skip the loss
        else:
            # can't go negative
            return -1

    # - Main logic

    if pnl[t] >= 0:
        if dp(pnl, t - 1, losses) == -1:
            return -1
        return dp(pnl, t - 1, losses) + pnl[t] # add the profit
    elif pnl[t] < 0:
        return max(dp(pnl, t - 1, losses - 1) + pnl[t] if dp(pnl, t - 1, losses - 1) != -1 and dp(pnl, t - 1, losses - 1) + pnl[t] >= 0 else -1, # take the loss
                   dp(pnl, t - 1, losses)) # skip the loss


def test():
    # - Final function

    print(dp(pnl=(1, 2, 3, 4, 5), t=4, losses=0))
    print(dp(pnl=(1, 2, 3, -3, -2), t=4, losses=2))
    print(dp(pnl=(-1, 1, 2, 3, -3, -2), t=5, losses=2))

if __name__ == "__main__":
    test()
