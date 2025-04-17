import random
import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
app.title = 'Real-Time Drone Telemetry'

app.layout = dbc.Container([
    html.H2("🚁 Drone Telemetry Dashboard", className="text-center text-light mb-4"),
    dbc.Row([
        dbc.Col([
            daq.Gauge(
                id='battery-gauge',
                label='Battery Voltage (V)',
                min=0, max=12,
                showCurrentValue=True,
                units="V",
                color={"gradient":True, "ranges":{"green":[8,12], "orange":[4,8], "red":[0,4]}},
                value=0
            ),
            html.Div(id='connection-health', className='mt-3 text-center')
        ], width=4),

        dbc.Col([
            daq.Indicator(
                id="temp-indicator",
                label="Temperature (°C)",
                color="blue",
                value=True
            ),
            dcc.Graph(id='altitude-graph'),
        ], width=4),

        dbc.Col([
            daq.LEDDisplay(
                id='gps-display',
                label="GPS (Lat, Long)",
                value="0.0000, 0.0000",
                size=30,
                color="#00FF00"
            ),
            dcc.Graph(id='imu-orientation'),
        ], width=4)
    ]),

    dcc.Interval(id='interval-component', interval=1000, n_intervals=0)
], fluid=True)


def generate_telemetry():
    return {
        "voltage": round(random.uniform(7.5, 12.0), 2),
        "temperature": round(random.uniform(25.0, 45.0), 2),
        "altitude": round(random.uniform(10, 120), 2),
        "imu": {
            "roll": random.uniform(-180, 180),
            "pitch": random.uniform(-90, 90),
            "yaw": random.uniform(0, 360),
        },
        "gps": {
            "lat": round(random.uniform(10.0, 11.0), 4),
            "lon": round(random.uniform(76.0, 78.0), 4)
        },
        "connection": random.choice(["Good", "Poor"])
    }

@app.callback(
    Output('battery-gauge', 'value'),
    Output('temp-indicator', 'color'),
    Output('altitude-graph', 'figure'),
    Output('gps-display', 'value'),
    Output('imu-orientation', 'figure'),
    Output('connection-health', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_dashboard(n):
    data = generate_telemetry()
    temp_color = "red" if data['temperature'] > 40 else "blue"

    altitude_fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = data['altitude'],
        title = {'text': "Altitude (m)"},
        gauge = {'axis': {'range': [None, 150]}, 'bar': {'color': "cyan"}}
    ))

    imu_fig = go.Figure(
        data=go.Scatter3d(
            x=[0, data['imu']['roll']],
            y=[0, data['imu']['pitch']],
            z=[0, data['imu']['yaw']],
            marker=dict(size=5),
            line=dict(color='lime', width=6)
        )
    )
    imu_fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        scene=dict(
            xaxis_title='Roll',
            yaxis_title='Pitch',
            zaxis_title='Yaw'
        )
    )

    status_text = dbc.Badge(f"Connection: {data['connection']}",
                            color="success" if data['connection'] == "Good" else "danger",
                            className="p-2")

    return data['voltage'], temp_color, altitude_fig, f"{data['gps']['lat']}, {data['gps']['lon']}", imu_fig, status_text

if __name__ == '__main__':
    app.run_server(debug=True)
