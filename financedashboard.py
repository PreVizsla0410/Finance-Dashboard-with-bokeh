import pandas as pd
import yfinance as yf #yahoofinance

from bokeh.io import curdoc #pip install bokeh
from bokeh.models import ColumnarDataSource, Select, DataTable, TableColumn
from bokeh.layouts import column, Row
from bokeh.plotting import figure, show

DEFAULT_TICKERS = ["AAPL", "GOOG", "MSFT", "NFLX", "TSLA"] #Die Aktienkürzel, einmal nur wenige verwednet "Tickers"
START, END = "2018-01-01", "2021-01-01" # DAtum

def load_ticker(tickers):
    df = yf.download(tickers, start=START, end=END)
    return df["Close"].dropna()

static_data = load_ticker(DEFAULT_TICKERS)

def get_data(t1, t2):
    d = load_ticker(DEFAULT_TICKERS)
    df = d[[t1, t2]]
    returns = df.pct_change().add_suffix("_returns")
    df = pd.concat([df, returns], axis=1)
    df.rename(columns={t1:"t1", t2:"t2", 
    t1+"_returns":"t1_returns", t2+"_returns":"t2_returns"}, inplace=True)
    return df.dropna()

def nix(val, lst):
    return [x for x in lst if x!= val] #Schleife ohne Wiederholung 
tickers1 = Select(value="AAPL", options = nix("GOOG", DEFAULT_TICKERS))
tickers2 = Select(value="GOOG", options = nix("AAPL", DEFAULT_TICKERS))

# Source Data
data = get_data(tickers1.value, tickers2.value)
source = ColumnarDataSource(data=data)

#Descriptive Stats
stats = round(data.describe().reset_index(), 2)
stats_source = ColumnarDataSource(data=source)
stats_columns = [TableColumn(field=col, title=col) for col in stats.columms]
data_table = DataTable(source=stats_source, columns=stats_columns, width = 350, height=350, index_position=None)

#Plots
corr_tools = "pan, wheel_zoom, box_select, reset"
tools = "pan, wheel_zoom, xbox_select, reset"

corr = figure(width=350, height=350, tools=corr_tools)
corr.circle("t1_returns", "t2_returns", size=2, source=source,
selection_color="firebrick", alpha=0.6, nonselection_alpha=0.1, selection_alpha=0.4)

#show(corr)

ts1 = figure(width=700, height=250, tools=tools, x_axis_type="dateime", active_drag="xbox_select")
ts1.line("Date", "t1", source=source)
ts1.circle("Date", "t1", size=1, source=source, color=None, selection_color="firebrick")

ts2  =figure(width=700, height=200, tools=tools, x_axis_type="datetime",
active_drag="xbox_select")
ts2.x_range = ts1.x_range
ts2.line("Date", "t2", source=source)
ts2.circle("Date", "t2", size=1, source=source, color=None, selection_color="firebrick")

#show(column(ts1, ts2))

#Callbacks

def ticker1_change(attrname, old, new):
    tickers2.options = nix(new, DEFAULT_TICKERS)
    update()

def ticker2_change(attrname, old, new):
    tickers1.options = nix(new, DEFAULT_TICKERS)
    update()

def update():
    t1, t2 = tickers1.value, tickers2.value
    df = get_data(t1,t2)
    source.data = df
    stats_source.data = round(df.describe().reset_index(), 2)
    corr.title.text = "%s returns vs. %s return" % (t1, t2)
    ts1.title.text, ts2.title.text = t1, t2

tickers1.on_change('value', ticker1_change)
tickers2.on_change('value', ticker2_change)

#Layouts
widgets = column(tickers1, tickers2. data_table)
main_row = row(corr, widgets)
series = column(ts1, ts2)
layout = column(main_row, series)

#show(layout)

#Bokeh Server
curdoc().add_root(layout)
curdoc().title = "Stock Dashboard"

# Tutorial from https://www.youtube.com/watch?v=OJNxE1FjtXU