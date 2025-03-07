import pandas as pd
import dash
from dash import dcc, html
import plotly.graph_objects as go
import base64
import dash.dependencies as dd
import io
from datetime import datetime
import os

# Current data from the sheet
DATA = """Date,Value
12/31/15,6.1403
3/31/16,12.162
6/30/16,11.0909
9/30/16,11.45
12/31/16,9.8059
3/31/17,10.3306
6/30/17,11.0793
9/30/17,11.4353
12/31/17,11.0004
3/31/18,12.2839
6/30/18,13.5906
9/30/18,12.5345
12/31/18,16.5534
3/31/19,14.6615
6/30/19,14.064
9/30/19,13.4716
12/31/19,12.3025
3/31/20,14.7086
6/30/20,13.9079
9/30/20,14.1174
12/31/20,13.7566
3/31/21,14.9758
6/30/21,16.1742
9/30/21,17.0009
12/31/21,15.5105
3/31/22,15.7077
6/30/22,16.4159
9/30/22,14.129
12/31/22,12.7491
3/31/23,13.9667
6/30/23,15.7544
9/30/23,15.2208
12/31/23,17.6384
3/31/24,14.8147
6/30/24,14.3514
9/30/24,14.9211
12/31/24,13.8734
3/4/25,12.9881"""

def prepare_dataframe(data):
    """Convert string data to DataFrame with error handling"""
    try:
        print("Attempting to create DataFrame...")
        df = pd.read_csv(io.StringIO(data))
        print("DataFrame columns:", df.columns.tolist())
        # Specify the date format explicitly
        df["date"] = pd.to_datetime(df["Date"], format="%m/%d/%y")
        df["wacc"] = df["Value"]
        df.sort_values("date", inplace=True)
        print(f"Successfully created DataFrame with {len(df)} rows")
        return df
    except Exception as e:
        print(f"Error in prepare_dataframe: {e}")
        print("Raw data received:", data)
        raise

# Initial data load
print("Starting initial data load...")
df = prepare_dataframe(DATA)

# Encode background Goose GIF and Star marker GIF
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    goose_gif = os.path.join(script_dir, "goose.gif")
    print(f"Looking for goose.gif at: {goose_gif}")
    
    with open(goose_gif, 'rb') as f:
        encoded_goose = base64.b64encode(f.read()).decode('ascii')
        print("Successfully loaded goose.gif")
except FileNotFoundError as e:
    print(f"Warning: Could not find goose.gif: {e}")
    encoded_goose = ""
except Exception as e:
    print(f"Warning: Error loading goose.gif: {e}")
    encoded_goose = ""

# Dash app setup
app = dash.Dash(__name__)

# Animation settings
animation_speed = 150  # Much faster updates (150ms interval)
pause_duration = 15000  # Pause for 15 seconds at the end

# Background style with semi-transparent overlay
background_style = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "width": "100%",
    "height": "100%",
    "background": f"url('data:image/gif;base64,{encoded_goose}')" if encoded_goose else "black",
    "backgroundSize": "cover",
    "backgroundPosition": "center",
    "opacity": "0.8",  # Increased opacity from 0.5 to 0.8
    "zIndex": -1
}

app.layout = html.Div([
    # Background div
    html.Div(style=background_style),
    
    # Content div
    html.Div(
        style={
            "height": "100vh",
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "flexDirection": "column",
            "padding": "20px",
            "position": "relative",
            "zIndex": 1
        },
        children=[
            html.Div(
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "marginBottom": "20px",
                    "background": "rgba(0,0,0,0.5)",  # More transparent overlay
                    "padding": "20px",
                    "borderRadius": "10px"
                },
                children=[
                    html.H1(
                        "WACC Dashboard",
                        style={
                            "color": "yellow",
                            "fontSize": "32px",
                            "textShadow": "3px 3px 10px black",
                            "margin": 0
                        },
                    ),
                ],
            ),
            html.Div(
                style={
                    "width": "90%",
                    "background": "rgba(0,0,0,0.5)",  # More transparent overlay
                    "padding": "20px",
                    "borderRadius": "10px"
                },
                children=[
                    dcc.Graph(
                        id="wacc-chart",
                        config={"displayModeBar": False},
                        style={"width": "100%", "height": "70vh"},
                    ),
                ]
            ),
            dcc.Interval(
                id="interval-component",
                interval=animation_speed,
                n_intervals=0,
                max_intervals=len(df),
            ),
            dcc.Interval(
                id="pause-replay",
                interval=pause_duration,
                n_intervals=0,
                max_intervals=1,
                disabled=True,
            ),
        ],
    )
])

# Animation Callback (Updates Chart)
@app.callback(
    dd.Output("wacc-chart", "figure"),
    [dd.Input("interval-component", "n_intervals")]
)
def update_graph(n):
    if n >= len(df):  # Stop updating at the last data point
        return dash.no_update
    
    sub_df = df.iloc[: n + 1]  # Progressive data points
    fig = go.Figure()

    # WACC Line (Main Line - White)
    fig.add_trace(
        go.Scatter(
            x=sub_df["date"],
            y=sub_df["wacc"],
            mode="lines+markers",
            line=dict(color="white", width=3, shape="spline"),  # Smooth curve
            marker=dict(size=8, color="white"),
            name="WACC",
        )
    )

    # Highlight the Last Data Point for WACC Only
    if not sub_df.empty:
        last_x = sub_df["date"].iloc[-1]
        last_y = sub_df["wacc"].iloc[-1]
        fig.add_trace(
            go.Scatter(
                x=[last_x],
                y=[last_y],
                mode="markers+text",
                marker=dict(size=18, color="yellow", line=dict(color="red", width=3)),
                text=[f"{last_y:.2f}%"],
                textfont=dict(
                    size=20,
                    color="yellow",
                ),
                textposition="bottom center",
                showlegend=False,
            )
        )

    fig.update_layout(
        title="",
        xaxis_title="Date",
        yaxis_title="WACC (%)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0.2)",  # More transparent background
        font=dict(size=14, color="white"),
        margin=dict(l=50, r=50, t=50, b=50),
        template="plotly_dark",
        # Improve the grid and tick colors
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.1)",
            tickcolor="white",
            tickfont=dict(color="white"),
            showgrid=True,
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.1)",
            tickcolor="white",
            tickfont=dict(color="white"),
            showgrid=True,
        ),
    )

    return fig

# Pause & Replay Callback
@app.callback(
    [dd.Output("interval-component", "n_intervals"),
     dd.Output("interval-component", "disabled"),
     dd.Output("pause-replay", "disabled")],
    [dd.Input("interval-component", "n_intervals"),
     dd.Input("pause-replay", "n_intervals")],
)
def control_animation(n, replay_signal):
    if n >= len(df):  # Stop at the last value and enable pause timer
        return n, True, False  # Disable animation, enable 15s pause
    if replay_signal == 1:  # Restart after pause
        return 0, False, True  # Reset animation and disable pause timer
    return n, False, True  # Continue normal animation

if __name__ == "__main__":
    app.run_server(debug=True)