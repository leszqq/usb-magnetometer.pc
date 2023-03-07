from plotly.subplots import make_subplots
import plotly.graph_objects as go
from pandas import DataFrame

_FILE_COLUMN_NAMES = ['t [s]', 'Bx [mT]', 'By [mT]', 'Bz [mT]']




df = DataFrame(data={_FILE_COLUMN_NAMES[0]: [0.0, 0.1, 0.2],
                     _FILE_COLUMN_NAMES[1]: [1,2,3],
                     _FILE_COLUMN_NAMES[2]: [2,5,7],
                     _FILE_COLUMN_NAMES[3]: [3,2,1]})

fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
fig.add_trace(go.Scattergl(x=df['t [s]'], y=df['Bx [mT]'], name='Bx [mT]'), row=1, col=1)
fig.add_trace(go.Scattergl(x=df['t [s]'], y=df['By [mT]'], name='By [mT]'), row=1, col=1)
fig.add_trace(go.Scattergl(x=df['t [s]'], y=df['Bz [mT]'], name='Bz [mT]'), row=1, col=1)

fig.update_layout(title_text="Magnetic Flux Density B [mT]")
fig.update_xaxes(title_text="Time [s]", row=1, col=1)
fig.update_yaxes(title_text="Magnetic Flux Density B [mT]", row=1, col=1)


_PLOT_CONFIG = dict({'scrollZoom': True})
fig.show(config=_PLOT_CONFIG)
