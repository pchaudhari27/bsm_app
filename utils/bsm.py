import pandas as pd
import numpy as np
import scipy as sp
import argparse
import typing as tp


def bsm_model(
    strike_price: float,
    spot_price: float,
    risk_free_rate: float,
    volatility: float,
    time_to_maturity: float,
) -> tp.Tuple[pd.DataFrame, pd.DataFrame]:
    spots = np.arange(spot_price * 0.8, spot_price * 1.2, (spot_price * 0.04))
    strikes = np.arange(strike_price * 0.8, strike_price * 1.2, (strike_price * 0.04))

    # basic BSM
    # save sigma * sqrt(t) to not redo
    sigma_rtt = volatility * np.sqrt(time_to_maturity)

    # calculate d1 first
    d1s = np.log(spots.reshape(-1, 1) / strikes)
    d1s += time_to_maturity * (risk_free_rate + (volatility * volatility / 2))
    d1s /= sigma_rtt

    # d2 = d1 - sigma * sqrt(t)
    d2s = d1s - sigma_rtt

    # take standard normal cdf of both d1 and d2
    nd1s = sp.stats.norm.cdf(d1s)
    nd2s = sp.stats.norm.cdf(d2s) * np.exp(-risk_free_rate * time_to_maturity)

    # need to make indices line up correctly
    calls = nd1s * spots.reshape(-1, 1) - nd2s * strikes

    # use put call parity
    puts = (
        calls
        - spots.reshape(-1, 1)
        + np.exp(-risk_free_rate * time_to_maturity) * strikes
    )

    return (
        pd.DataFrame(calls, index=spots, columns=strikes),
        pd.DataFrame(puts, index=spots, columns=strikes),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    today = pd.Timestamp("today")

    # take initial arguments
    parser.add_argument(
        "strike_price",
        help="strike price of the option",
        type=float,
    )
    parser.add_argument(
        "spot_price",
        help="spot price of the option",
        type=float,
    )
    parser.add_argument(
        "risk_free_rate",
        help="risk free rate of the option",
        type=float,
    )
    parser.add_argument(
        "volatility",
        help="volatility of the option",
        type=float,
    )
    parser.add_argument(
        "time_to_maturity",
        help="time to maturity of the option",
        type=float,
    )

    # option arguments
    parser.add_argument(
        "-o",
        "--output_names",
        help="give two file names, both ending in .csv",
        nargs=2,
        default=[
            f"call_{today}.csv",
            f"put_{today}.csv",
        ],
    )

    args, unknown_args = parser.parse_known_args()

    try:
        assert (
            args.output_names[0][-4:] == ".csv" and args.output_names[1][-4:] == ".csv"
        )
    except AssertionError:
        raise ValueError("file names in --output_names must end in .csv")

    try:
        assert args.strike_price > 0
    except AssertionError:
        raise ValueError("strike_price must be > 0")

    try:
        assert args.spot_price > 0
    except AssertionError:
        raise ValueError("spot_price must be > 0")

    try:
        assert args.time_to_maturity > 0
    except AssertionError:
        raise ValueError("time_to_maturity must be > 0")

    try:
        assert args.volatility > 0
    except AssertionError:
        raise ValueError("volatility must be > 0")

    call_prices, put_prices = bsm_model(
        args.strike_price,
        args.spot_price,
        args.risk_free_rate,
        args.volatility,
        args.time_to_maturity,
    )

    call_prices.to_csv(args.output_names[0])
    put_prices.to_csv(args.output_names[1])
