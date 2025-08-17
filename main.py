import streamlit as st
import pandas as pd
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt

from utils.bsm import bsm_model

import matplotlib as mpl

mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica"],
        "font.size": 14,
        "figure.figsize": (15, 10),
    }
)

bsm_palette = sns.diverging_palette(
    250,
    15,
    s=75,
    l=40,
    center="dark",
    as_cmap=True,
)


def sidebar_inputs():
    spot = 10
    strike = 10
    rfr = 5
    sigma = 30
    tau = 1
    tau_units = "years"
    day_count_convention = 360
    show_pl = False

    with st.sidebar.expander("Option Characteristics"):
        f = st.form("char_form")
        spot_val = f.number_input("Spot Price", value=spot, min_value=1)
        strike_val = f.number_input("Strike Price", value=strike, min_value=1)
        rfr_val = f.number_input("Risk Free Rate (%)", value=rfr, min_value=1)
        sigma_val = f.number_input("Volatility (%)", value=sigma, min_value=1)
        tau_val = f.number_input("Time to Maturity", value=tau, min_value=1)
        tau_units_val = f.selectbox(
            "Units of Time to Maturity",
            [
                "years",
                "months",
                "days",
            ],
        )

        if tau_units_val == "days":
            day_count_convention = f.selectbox(
                "Day Count Convention", [360, 365, "actual"]
            )

        with f.expander("Advanced"):
            show_pl_val = st.checkbox("Show P&L")

        applied = f.form_submit_button("Apply")
        if applied:
            spot = spot_val
            strike = strike_val
            rfr = rfr_val
            sigma = sigma_val
            tau = tau_val
            tau_units = tau_units_val
            show_pl = show_pl_val

    match tau_units:
        case "days":
            if day_count_convention == "actual":
                start_maturity = pd.Period(
                    pd.Timestamp("today"),
                    freq="Y",
                )
                end_maturity = pd.Period(
                    pd.Timestamp("today") + pd.DateOffset(days=tau),
                    freq="Y",
                )

                years = end_maturity.year - start_maturity.year + 1

                # assert to get rid of warnings/errors
                assert isinstance(start_maturity, pd.Period)
                assert isinstance(end_maturity, pd.Period)

                # use average num of days in the years encasing time_to_maturity
                units_divider = (
                    len(
                        pd.date_range(
                            start_maturity.start_time,
                            end_maturity.end_time,
                            freq="D",
                        )
                    )
                    / years
                )
            else:
                units_divider = int(day_count_convention)
        case "months":
            units_divider = 12
        case "years":
            units_divider = 1
        case _:
            units_divider = 0

    rfr /= 100
    sigma /= 100
    tau /= units_divider

    return (strike, spot, rfr, sigma, tau, show_pl)


def raw_calls_and_puts(calls, puts, strike, spot):
    st.header("Call Option Pricing")
    fig, ax = plt.subplots(
        1,
        1,
    )
    calls_fmt = calls.map(lambda x: f"${x:,.2f}" if x > 0 else "$0.00")
    sns.heatmap(
        calls,
        ax=ax,
        annot=calls_fmt,
        fmt="",
        cmap=bsm_palette,
        cbar=False,
        center=calls.loc[np.round(spot, 2), np.round(strike, 2)],
    )
    st.pyplot(fig)

    st.header("Put Option Pricing")
    fig, ax = plt.subplots(
        1,
        1,
    )
    puts_fmt = puts.map(lambda x: f"${x:.2f}" if x > 0 else "$0.00")
    sns.heatmap(
        puts,
        ax=ax,
        annot=puts_fmt,
        fmt="",
        cmap=bsm_palette,
        cbar=False,
        center=puts.loc[np.round(spot, 2), np.round(strike, 2)],
    )
    st.pyplot(fig)


def pl_calls_and_puts(
    calls,
    puts,
):
    st.header("Call Option Pricing - P&L")
    fig, ax = plt.subplots(
        1,
        1,
    )
    calls_fmt = calls.map(lambda x: f"${x:,.2f}")
    sns.heatmap(
        calls,
        ax=ax,
        annot=calls_fmt,
        fmt="",
        cmap=bsm_palette,
        cbar=False,
        center=0,
    )
    st.pyplot(fig)

    st.header("Put Option Pricing - P&L")
    fig, ax = plt.subplots(
        1,
        1,
    )
    puts_fmt = puts.map(lambda x: f"${x:.2f}")
    sns.heatmap(
        puts,
        ax=ax,
        annot=puts_fmt,
        fmt="",
        cmap=bsm_palette,
        cbar=False,
        center=0,
    )
    st.pyplot(fig)


def main_app():
    strike, spot, rfr, sigma, tau, show_pl = sidebar_inputs()

    calls, puts = bsm_model(
        strike,
        spot,
        rfr,
        sigma,
        tau,
    )

    # if user sets advanced option, do P&L
    if show_pl:
        calls = calls - calls.loc[np.round(strike, 2), np.round(spot, 2)]
        puts = puts - puts.loc[np.round(strike, 2), np.round(spot, 2)]

        pl_calls_and_puts(
            calls,
            puts,
        )
    else:
        raw_calls_and_puts(calls, puts, strike, spot)

    # calls = calls.reset_index().melt(id_vars=["Spot Price"])
    # puts = puts.reset_index().melt(id_vars=["Spot Price"])


if __name__ == "__main__":
    main_app()
