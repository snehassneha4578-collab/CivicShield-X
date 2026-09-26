from __future__ import annotations

from typing import Any

import plotly.graph_objects as go


DISTRICT_POSITIONS = {
    "DIST-01": (0.0, 0.0),
    "DIST-02": (1.0, 1.0),
    "DIST-03": (2.0, 0.0),
}

NODE_POSITIONS = {
    "WATER-01": (0.15, 0.20),
    "BRIDGE-01": (0.65, 0.35),
    "HOSP-01": (0.95, 1.25),
    "FIRE-01": (1.45, 0.85),
    "ROAD-01": (1.75, 0.25),
    "POWER-01": (2.25, 0.15),
}

STATUS_SCORE = {
    "NORMAL": 1,
    "DEGRADED": 2,
    "AT RISK": 2,
    "STRESSED": 3,
    "CRITICAL": 4,
}

STATUS_SYMBOL = {
    "NORMAL": "circle",
    "DEGRADED": "diamond",
    "AT RISK": "diamond",
    "STRESSED": "triangle-up",
    "CRITICAL": "x",
}

STATUS_COLOR = {
    "NORMAL": "#00e676",
    "DEGRADED": "#ffd600",
    "AT RISK": "#ff9100",
    "STRESSED": "#ff9100",
    "CRITICAL": "#ff1744",
}


def _status_for_node(node: dict[str, Any], cascade_df) -> str:
    matches = cascade_df[cascade_df["node"] == node["id"]]

    if matches.empty:
        return "NORMAL"

    return str(matches.iloc[-1]["status"])


def _impact_for_node(node_id: str, cascade_df) -> float:
    matches = cascade_df[cascade_df["node"] == node_id]

    if matches.empty:
        return 0.0

    return float(matches.iloc[-1]["impact"])


def build_living_city_figure(city: dict[str, Any], cascade_df):
    fig = go.Figure()

    for district in city["districts"]:
        x, y = DISTRICT_POSITIONS[district["id"]]

        fig.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                mode="markers+text",
                marker=dict(
                    size=125,
                    opacity=0.12,
                    line=dict(width=1.5, color="rgba(120,180,255,0.35)"),
                ),
                text=[district["name"].upper()],
                textposition="middle center",
                textfont=dict(size=13, color="rgba(210,225,245,0.82)"),
                hovertemplate=(
                    f"<b>{district['name']} District</b><br>"
                    f"Population: {district['population']:,}<br>"
                    f"Risk profile: {district['risk_profile']}<extra></extra>"
                ),
                showlegend=False,
            )
        )

    for dependency in city["dependencies"]:
        source = dependency["source"]
        target = dependency["target"]

        if source not in NODE_POSITIONS or target not in NODE_POSITIONS:
            continue

        x1, y1 = NODE_POSITIONS[source]
        x2, y2 = NODE_POSITIONS[target]

        source_impact = _impact_for_node(source, cascade_df)
        target_impact = _impact_for_node(target, cascade_df)
        propagation = max(source_impact, target_impact)

        line_width = 1.2
        dash = "dot"
        line_color = "rgba(100,150,210,0.35)"

        if propagation >= 75:
            line_width = 3.5
            dash = "solid"
            line_color = "#ff1744"
        elif propagation >= 60:
            line_width = 2.5
            dash = "solid"
            line_color = "#ff9100"

        fig.add_trace(
            go.Scatter(
                x=[x1, x2],
                y=[y1, y2],
                mode="lines",
                line=dict(width=line_width, dash=dash, color=line_color),
                customdata=[
                    [
                        source,
                        target,
                        dependency["strength"],
                        dependency["mechanism"],
                    ],
                    [
                        source,
                        target,
                        dependency["strength"],
                        dependency["mechanism"],
                    ],
                ],
                hovertemplate=(
                    "<b>Dependency Propagation</b><br>"
                    "Source: %{customdata[0]}<br>"
                    "Target: %{customdata[1]}<br>"
                    "Dependency strength: %{customdata[2]:.0%}<br>"
                    "Mechanism: %{customdata[3]}<extra></extra>"
                ),
                showlegend=False,
            )
        )

        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2

        fig.add_trace(
            go.Scatter(
                x=[mid_x],
                y=[mid_y],
                mode="markers",
                marker=dict(
                    size=9,
                    symbol="triangle-right",
                    color=line_color,
                    line=dict(width=0),
                ),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    for node in city["infrastructure"]:
        node_id = node["id"]
        x, y = NODE_POSITIONS[node_id]

        status = _status_for_node(node, cascade_df)
        impact = _impact_for_node(node_id, cascade_df)

        score = STATUS_SCORE.get(status, 1)
        color = STATUS_COLOR.get(status, STATUS_COLOR["NORMAL"])
        symbol = STATUS_SYMBOL.get(status, "circle")

        size = 22 + score * 5

        fig.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                mode="markers+text",
                marker=dict(
                    size=size,
                    symbol=symbol,
                    line=dict(width=2.5, color=color),
                ),
                text=[node["name"]],
                textposition="bottom center",
                textfont=dict(size=11, color="#e8f0ff"),
                customdata=[
                    [
                        node_id,
                        node["type"],
                        node["district"],
                        node["capacity"],
                        status,
                        impact,
                    ]
                ],
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "ID: %{customdata[0]}<br>"
                    "Type: %{customdata[1]}<br>"
                    "District: %{customdata[2]}<br>"
                    "Capacity: %{customdata[3]}<br>"
                    "Status: %{customdata[4]}<br>"
                    "Modeled impact: %{customdata[5]:.1f}<br>"
                    f"<span style='color:{color}'><b>{status}</b></span>"
                    "<extra></extra>"
                ),
                showlegend=False,
            )
        )

    fig.update_layout(
        height=540,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(4,10,20,0.55)",
        xaxis=dict(
            visible=False,
            range=[-0.55, 2.75],
        ),
        yaxis=dict(
            visible=False,
            range=[-0.55, 1.75],
            scaleanchor="x",
            scaleratio=1,
        ),
        hoverlabel=dict(
            bgcolor="#0b1220",
            font=dict(size=13),
        ),
        showlegend=False,
    )

    return fig

