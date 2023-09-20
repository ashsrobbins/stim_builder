import dash
# import dash_core_components as dcc
# import dash_html_components as html
from dash import dcc, html

from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from plotly.graph_objs import Figure
import numpy as np
import stim_builder as sb
from plotly.subplots import make_subplots
from aws_helper import save_to_s3


app = dash.Dash(__name__)

# List to store the commands
commands = []

app.layout = html.Div(style={'width':'80%', 'margin':'auto', 'padding': '20px'}, children=[
    dcc.Store(id='commands-store', data=[]),
    html.H1('Stim Waveform Creator', style={'textAlign':'center'}),

    html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '10px', 'alignItems': 'flex-end'}, children=[
        
        html.Div(style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'width': '30%'}, children=[
            html.Label('Neurons:', style={'font-weight':'bold'}),
            # dcc.Input(id='neuron_index', type='text', value='0,1,2'),
            dcc.Checklist(
                id='neuron_index',
                options=[
                    {'label': 'Neuron 0', 'value': 0},
                    {'label': 'Neuron 1', 'value': 1},
                    {'label': 'Neuron 2', 'value': 2},
                    {'label': 'Neuron 3', 'value': 3},
                    {'label': 'Neuron 4', 'value': 4}
                ],
                value=[0, 1, 2]
            ),

            html.Label('Amplitude (mV):', style={'font-weight':'bold'}),
            dcc.Input(id='amplitude', type='number', value=150),

            html.Label('Pulse-width (𝜇s):', style={'font-weight':'bold'}),
            dcc.Input(id='frames', type='number', value=int(200), step=50, min=50),

            html.Button('Add Stimulation', id='add-button', style={
                'width':'50%', 
                'height':'50px', 
                'background-color':'#28a745', 
                'color':'black', 
                'border':'none', 
                'cursor':'pointer', 
                'marginTop':'10px', 
                'borderRadius':'15px'
            }),
        ]),


        html.Div(style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'width': '30%'}, children=[
            html.Label('Delay ms:', style={'font-weight':'bold'}),
            dcc.Input(id='delay_frames', type='number', value=5*20),

            html.Button('Add Delay', id='delay-button', style={
                'width':'50%', 
                'height':'50px',
                'background-color':'#ffc107', 
                'color':'black', 
                'border':'none', 
                'cursor':'pointer', 
                'marginTop':'10px',
                'borderRadius':'15px'
            }),
        ]),

        # Add png of waveform
        html.Div(style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'space-between', 'width': '30%'}, children=[
            html.Img(src='/assets/pulse.png', style={'width':'100%', 'height':'auto'}),]),

        # html.Button('Next', id='next-button', style={'width':'30%', 'height':'50px', 'background-color':'#dc3545', 'color':'white', 'border':'none', 'cursor':'pointer'},
        #             disabled=True),
        html.Button('', id='next-button', style={'width':'30%', 'height':'50px', 'background-color':'white', 'color':'white', 'border':'none', 'cursor':'pointer'},
                    disabled=True),
    ]),
    html.Div(style={'marginBottom': '10px', 'textAlign':'center', 'width':'50%', 'margin':'auto'}, children=[
        html.Label('Length of Stim Cycle (s):', style={'font-weight':'bold', 'width':'100%'}),
        dcc.Slider(
            id='freq',
            min=.02,
            max=1,  # Adjust as needed
            step=.01,   # Adjust as needed
            value=1,
            marks={
                .02: '.02 seconds',
                .5: '.5 seconds',
                1: '1 seconds',
            }
        ),
        html.Div(id='freq-value', style={'textAlign':'center'}),

    ]),



    dcc.Graph(id='waveform-graph', config={'displayModeBar': False}),
    html.Div(style={'marginBottom': '10px', 'textAlign':'center'}
             , children=[
        html.Label('Name:', style={'font-weight':'bold'}),
        dcc.Input(id='name', type='text', value=''),
    ]),
    html.Div(style={'marginBottom': '10px', 'textAlign':'center'}
                , children=[
        html.Label('Click save to upload your file!',id='user-message', style={'font-weight':'bold'}),
                ]),

    html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '10px'}, children=[
        html.Button('Generate', id='generate-button', style={'width':'30%', 'height':'50px', 'background-color':'#007BFF', 'color':'white', 'border':'none', 'cursor':'pointer'}),
        html.Button('Save', id='save-button', style={'width':'30%', 'height':'50px', 'background-color':'#007BFF', 'color':'white', 'border':'none', 'cursor':'pointer'}),
        html.Button('Reset', id='reset-button', style={'width':'30%', 'height':'50px', 'background-color':'#6c757d', 'color':'white', 'border':'none', 'cursor':'pointer'}),
    ]),

    html.Div(id='commands-list', style={'marginTop':'20px', 'color':'black', 'font-size':'16px'})
])


callback_count1 = 0
callback_count2 = 0
callback_count3 = 0

@app.callback(
    [Output('freq-value', 'children'), Output('waveform-graph', 'figure'), Output('commands-list', 'children')],
    [Input('freq', 'value'), Input('commands-store', 'data')],
    [State('waveform-graph', 'figure')]
)
def update_output(freq, commands, current_fig):
    # global callback_count1
    # callback_count1 += 1
    freq = 1/freq
    freq_message = 'Current frequency: {:.1f} Hz'.format(freq)
    ctx = dash.callback_context

    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update
    else:
        input_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if input_id == 'freq':
        if current_fig:
            # Adjust the x-axis range based on the new frequency
            for i in range(len(current_fig['data'])):
                current_fig['layout']['xaxis'+str(i+1) if i > 0 else 'xaxis']['range'] = [0, freq]
            # return freq_message, current_fig, dash.no_update
    if input_id == 'commands-store' or input_id == 'freq':
        commands_inp = commands.copy()
        sig, t = sb._create_stim_pulse_sequence(commands_inp,freq, fs=fs_ms*1000)

        fig = make_subplots(rows=sig.shape[0], cols=1)  # Create a subplot for each trace

        for i in range(sig.shape[0]):
            fig.add_trace(go.Scatter(x=t, y=sig[i], mode='lines', name=f'Neuron {i}'), row=i+1, col=1)

        # Set the x-axis range to [0, 1/freq] for each subplot
        for i in range(sig.shape[0]):
            fig.update_xaxes(range=[0, 2/freq], visible=(i == sig.shape[0] - 1), title_text="Time (s)" if i == sig.shape[0] - 1 else None, row=i+1, col=1)
            if i == 2:
                fig.update_yaxes(title_text="Amplitude (mV)", row=i+1, col=1)

        output_commands = []
        for cmd in commands:
            if cmd[0] == 'stim':
                output_commands.append(html.Span(f'["stim", {cmd[1]}, {cmd[2]}, {cmd[3]}].', style={'color':'#28a745', 'display':'block', 'marginBottom':'10px'}))
            elif cmd[0] == 'delay':
                output_commands.append(html.Span(f'["delay", {cmd[1]}].', style={'color':'#ffc107', 'display':'block', 'marginBottom':'10px'}))
            elif cmd[0] == 'next':
                output_commands.append(html.Span('["next"],', style={'color':'#dc3545', 'display':'block', 'marginBottom':'10px'}))

        return freq_message, fig, output_commands

    return dash.no_update, dash.no_update, dash.no_update

@app.callback(
    [Output('user-message', 'children')],
    [Input('save-button', 'n_clicks')],
    [State('commands-store', 'data'), State('name', 'value')]
)
def save_commands(n_clicks, commands, name):
    ctx = dash.callback_context

    if not ctx.triggered:
        return dash.no_update
    else:
        input_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if input_id == 'save-button':
        if name:
            try:
                response = save_to_s3(name + '.txt',str(commands))
            except:
                # Save locally
                with open(name + '.txt', 'w') as f:
                    f.write(str(commands))
                response = True

        else:
            print('Please enter a name for the file')

    # Update user message

    if response:
        return ['Saved'] if input_id == 'save-button' else dash.no_update
    else:
        return ['Error saving to S3 with ' + name] if input_id == 'save-button' else dash.no_update

    


fs_ms = 1
@app.callback(
    Output('commands-store', 'data'),  # Update the Store
    [Input('add-button', 'n_clicks'),
     Input('delay-button', 'n_clicks'),
     Input('next-button', 'n_clicks'),
     Input('reset-button', 'n_clicks')],
    [State('neuron_index', 'value'),
     State('amplitude', 'value'),
     State('frames', 'value'),
     State('delay_frames', 'value'),
     State('commands-store', 'data')]  # Include the current store data as State
)
def update_commands_list(add_clicks, delay_clicks, next_clicks, reset_clicks, neuron_index, amplitude, frames, delay_frames, commands):
    ctx = dash.callback_context

    if not ctx.triggered:
        return commands  # Return current commands
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'add-button':
        if frames == None:
            return commands
        commands.append(('stim', neuron_index, amplitude, frames//50))
    elif button_id == 'delay-button':
        commands.append(('delay', delay_frames*fs_ms))
    elif button_id == 'next-button':
        commands.append(('next', None))
    elif button_id == 'reset-button':
        commands = []

    return commands  # Return updated commands





if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
