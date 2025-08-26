import streamlit as st
import pandas as pd
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt

from utils import bsm_model, cmaps, option_norm

st.set_page_config(
    page_title="BSM - Manual Inputs",
)

SESSION_DEFAULTS = {
    "spot": 10.0,
    "strike": 10.0,
    "rfr": 5.0,
    "sigma": 30.0,
    "tau": 1.0,
    "tau_units": "years",
    "show_pl": False,
    "call_price": None,
    "put_price": None,
    "chosen_palette": "Red-Blue",
    "day_count_convention": 360,
    "last_vals": {
        "spot": 10.0,
        "strike": 10.0,
        "rfr": 10.0,
        "sigma": 30.0,
        "tau": 1.0,
    },
}

for key in SESSION_DEFAULTS:
    if key not in st.session_state:
        st.session_state[key] = SESSION_DEFAULTS[key]


def reset_initial_state():
    for key in SESSION_DEFAULTS:
        st.session_state[key] = SESSION_DEFAULTS[key]


def reset_call_and_put_state():
    st.session_state["call_price_value"] = None
    st.session_state["put_price_value"] = None


def sidebar_inputs(
    strike=10.0,
    spot=10.0,
    rfr=5.0,
    sigma=30.0,
    tau=1.0,
    tau_units="years",
    show_pl=False,
    call_price=1.42,
    put_price=0.93,
    chosen_palette="Red-Blue",
    day_count_convention=360,
):
    with st.sidebar.expander("Option Characteristics"):
        f = st.form("settings")
        spot_val = f.number_input("Spot Price", min_value=1.0, key="spot")
        strike_val = f.number_input("Strike Price", min_value=1.0, key="strike")
        rfr_val = f.number_input("Risk Free Rate (%)", min_value=1.0, key="rfr")
        sigma_val = f.number_input("Volatility (%)", min_value=1.0, key="sigma")
        tau_val = f.number_input("Time to Maturity", min_value=1.0, key="tau")
        tau_units_val = f.selectbox(
            "Units of Time to Maturity",
            [
                "years",
                "months",
                "days",
            ],
            key="tau_units",
        )

        if tau_units_val == "days":
            day_count_convention = f.selectbox(
                "Day Count Convention",
                [360, 365, "actual"],
                key=("day_count_convention"),
            )

        with f.expander("Advanced"):
            show_pl_val = st.checkbox("Show P&L", key="show_pl")
            call_price_val = st.number_input(
                "Call Price",
                value=None,
                min_value=0.0,
                key="call_price",
            )
            put_price_val = st.number_input(
                "Put Price",
                value=None,
                min_value=0.0,
                key="put_price",
            )

            chosen_palette_val = st.selectbox(
                "Color palette",
                [
                    "Red-Blue",
                    "Red-Green",
                    # "Black-White",
                    "Orange-Seafoam",
                ],
                key="palette",
            )

        applied = f.form_submit_button("Apply")
        if applied:
            spot = spot_val
            strike = strike_val
            rfr = rfr_val
            sigma = sigma_val
            tau = tau_val
            tau_units = tau_units_val
            show_pl = show_pl_val
            chosen_palette = chosen_palette_val
            call_price = call_price_val
            put_price = put_price_val

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

    if (
        spot != st.session_state.last_vals["spot"]
        or strike != st.session_state.last_vals["strike"]
        or rfr != st.session_state.last_vals["rfr"]
        or sigma != st.session_state.last_vals["sigma"]
        or tau != st.session_state.last_vals["tau"]
    ):
        reset_call_and_put_state()

        return (
            strike,
            spot,
            rfr,
            sigma,
            tau,
            show_pl,
            None,
            None,
            chosen_palette,
        )

    return (
        strike,
        spot,
        rfr,
        sigma,
        tau,
        show_pl,
        call_price,
        put_price,
        chosen_palette,
    )


def raw_calls_and_puts(
    calls,
    puts,
    call_price,
    put_price,
    cmap,
):
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
        cmap=cmap,
        cbar=False,
        norm=option_norm(calls, price=call_price),
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
        cmap=cmap,
        cbar=False,
        norm=option_norm(puts, price=put_price),
    )
    st.pyplot(fig)


def pl_calls_and_puts(
    calls,
    puts,
    cmap,
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
        cmap=cmap,
        cbar=False,
        norm=option_norm(calls, show_pl=True),
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
        cmap=cmap,
        cbar=False,
        norm=option_norm(puts, show_pl=True),
    )
    st.pyplot(fig)


def main_app():
    st.sidebar.button(
        "Restore defaults", on_click=reset_initial_state, key="reset_button"
    )

    strike, spot, rfr, sigma, tau, show_pl, call_price, put_price, palette = (
        sidebar_inputs()
    )

    st.session_state.last_vals = {
        "strike": strike,
        "spot": spot,
        "rfr": rfr,
        "sigma": sigma,
        "tau": tau,
    }

    if palette == "Red-Green":
        st.markdown(
            ":red[Warning: red-green color palettes are not color blind friendly]"
        )

    calls, puts = bsm_model(strike, spot, rfr, sigma, tau)
    if not call_price:
        call_price = calls.loc[np.round(spot, 2), np.round(strike, 2)]
    if not put_price:
        put_price = puts.loc[np.round(spot, 2), np.round(strike, 2)]

    # if user sets advanced option, do P&L
    if show_pl:
        calls = calls - call_price
        puts = puts - put_price

        pl_calls_and_puts(calls, puts, cmap=cmaps[palette])
    else:
        raw_calls_and_puts(calls, puts, call_price, put_price, cmap=cmaps[palette])

    # calls = calls.reset_index().melt(id_vars=["Spot Price"])
    # puts = puts.reset_index().melt(id_vars=["Spot Price"])


if __name__ == "__main__":
    main_app()
