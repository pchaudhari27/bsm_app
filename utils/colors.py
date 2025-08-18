import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica"],
        "font.size": 14,
        "figure.figsize": (15, 10),
    }
)

red_blue_palette = LinearSegmentedColormap.from_list(
    "red_blue",
    ["#930400", "#efefef", "#0047bc"],
)

red_green_palette = LinearSegmentedColormap.from_list(
    "red_green",
    ["#930400", "#efefef", "#00642e"],
)

orange_seafoam_palette = LinearSegmentedColormap.from_list(
    "orange_yellow_seafoam",
    ["#ab3300", "#ffffeb", "#007272"],
)

cmaps = {
    "Red-Blue": red_blue_palette,
    "Red-Green": red_green_palette,
    "Orange-Seafoam": orange_seafoam_palette,
}


def option_norm(option_df, price=None, show_pl=False):
    if price is None and not show_pl:
        raise ValueError("either price must be given or show_pl must be set")

    vmax = option_df.max().max()
    if show_pl:
        vmin = option_df.min().min()

        if vmin == vmax:
            return TwoSlopeNorm(vmin=vmin, vcenter=vmin + 0.0001, vmax=vmin + 0.0002)

        if vmax <= 0:
            return TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=0.0001)

        if vmin >= 0:
            return TwoSlopeNorm(vmin=-0.0001, vcenter=0, vmax=vmax)

        return TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)

    assert isinstance(price, float)

    if 0 == price == vmax:
        return TwoSlopeNorm(vmin=0, vcenter=0.0001, vmax=0.0002)

    if price >= vmax:
        price = vmax - 0.0001
    elif price <= 0:
        price = 0.0001
    return TwoSlopeNorm(vmin=0, vcenter=price, vmax=vmax)
