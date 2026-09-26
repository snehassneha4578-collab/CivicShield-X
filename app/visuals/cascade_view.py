import plotly.graph_objects as go

NODE_POSITIONS = {
    "WATER-01": (0, 1.0),
    "BRIDGE-01": (1, 0.78),
    "ROAD-01": (2, 0.56),
    "FIRE-01": (3, 0.82),
    "HOSP-01": (4, 0.62),
    "RES-01": (5, 0.38),
}

def impact_color(impact):
    if impact >= 75:
        return "#ff1744"
    if impact >= 60:
        return "#ff9100"
    if impact >= 45:
        return "#ffd600"
    return "#00e676"

def build_cascade_figure(cascade_df):
    fig = go.Figure()

    # Propagation connections follow the actual cascade stages.
    edge_x = []
    edge_y = []

    rows = cascade_df.sort_values("stage").to_dict("records")

    for previous, current in zip(rows, rows[1:]):
        source = previous["node"]
        target = current["node"]

        if source in NODE_POSITIONS and target in NODE_POSITIONS:
            x0, y0 = NODE_POSITIONS[source]
            x1, y1 = NODE_POSITIONS[target]

            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

    fig.add_trace(
        go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(width=5, color="#536dfe"),
            hoverinfo="none",
            name="Crisis propagation",
        )
    )

    node_x = []
    node_y = []
    node_colors = []
    node_text = []
    hover_text = []

    for row in rows:
        node_id = row["node"]
        impact = float(row["impact"])
        x, y = NODE_POSITIONS.get(node_id, (0, 0))

        node_x.append(x)
        node_y.append(y)
        node_colors.append(impact_color(impact))
        node_text.append(str(node_id))

        hover_text.append(
            f"<b>Stage {int(row['stage'])} - {row['name']}</b><br>"
            f"Impact: {impact:.1f}/100<br>"
            f"Status: {row['status']}<br>"
            f"Cause: {row['cause']}"
        )

    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            marker=dict(
                size=46,
                color=node_colors,
                line=dict(width=3, color="white"),
            ),
            text=node_text,
            textposition="bottom center",
            textfont=dict(size=12, color="white"),
            hovertext=hover_text,
            hoverinfo="text",
            name="Infrastructure",
        )
    )

    fig.update_layout(
        title=dict(
            text="? Crisis Propagation Network",
            font=dict(size=24),
        ),
        template="plotly_dark",
        height=620,
        showlegend=False,
        xaxis=dict(
            visible=False,
            range=[-0.7, 5.7],
        ),
        yaxis=dict(
            visible=False,
            range=[0, 1.35],
        ),
        margin=dict(l=20, r=20, t=80, b=20),
        paper_bgcolor="#050914",
        plot_bgcolor="#050914",
    )

    return fig

