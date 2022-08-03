from math import ceil
from datetime import timedelta, datetime as dt

import pandas as pd
import streamlit as st
import altair as alt
from statsmodels.tsa.arima.model import ARIMA

wafr_countries = {
    "Benin": "BEN",
    "Burkina Faso": "BFA",
    "Cabo Verde": "CPV",
    "Cote d'Ivoire": "CIV",
    "Gambia": "GMB",
    "Ghana": "GHA",
    "Guinea": "GIN",
    "Guinea-Bissau": "GIN",
    "Liberia": "LBR",
    "Mali": "MLI",
    "Mauritania": "MRT",
    "Niger": "NER",
    "Nigeria": "NGA",
    "Senegal": "SEN",
    "Sierra Leone": "SLE",
    "Togo": "TGO",
}
ARIMA_ORDER = (1, 1, 3)
DAYS = 7


def get_sunday_date():
    weekday = dt.today().weekday()
    diff = abs(-1 - weekday)
    sunday = dt.today() - timedelta(days=diff)
    return sunday.isoformat()[:10]


def get_data(url, sunday):
    data = pd.read_csv(url)
    data = data.set_index(keys="Country/Region").drop(
        columns=["Province/State", "Lat", "Long"]
    )
    data.columns = pd.to_datetime(data.columns)
    wafr_data = data.loc[wafr_countries.keys()].loc[:, "2020-03-01" : sunday()]
    return wafr_data


@st.cache
def prepare_data_day(wafr_data):
    wafr_data = wafr_data.sum()
    wafr_data = (wafr_data - wafr_data.shift(1)).fillna(0)
    wafr_data[wafr_data < 0] = 0
    return wafr_data


@st.cache
def get_last_n_days_data(df, n=50, forecast=None):
    df = df.iloc[-n:].reset_index()
    df.columns = ["date", "deaths"]
    df["kind"] = "previous"
    if forecast is None:
        return df

    forecast = forecast.to_frame().reset_index()
    forecast.columns = ["date", "deaths"]
    forecast["kind"] = "forecast"

    join = df.iloc[-1].copy()
    join["kind"] = "forecast"

    df = df.append(join).append(forecast, ignore_index=True)
    return df


@st.cache
def make_forecast(df):
    model = ARIMA(df, order=ARIMA_ORDER).fit()
    forecast = model.forecast(DAYS)
    forecast = forecast.apply(lambda x: ceil(x))
    forecast[forecast < 0] = 0
    return forecast


# def altair_plot(base, fields):
#     highlight = alt.selection(
#         type="single", on="mouseover", fields=fields, nearest=True
#     )

#     points = (
#         base.mark_circle()
#         .encode(opacity=alt.value(0))
#         .add_selection(highlight)
#         .properties(width=600)
#     )

#     lines = base.mark_line().encode(
#         size=alt.condition(~highlight, alt.value(1), alt.value(3))
#     )

#     chart = points + lines
#     return st.altair_chart(chart, use_container_width=True)


def altair_plot(df, x, y, color):
    line = alt.Chart(df).mark_line().encode(x=x, y=y, color=color)

    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(
        type="single", nearest=True, on="mouseover", fields=[x[:-2]], empty="none"
    )

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = (
        alt.Chart(df)
        .mark_point()
        .encode(x=x, opacity=alt.value(0),)
        .add_selection(nearest)
    )

    # Draw points on the line, and highlight based on selection
    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    # Draw text labels near the points, and highlight based on selection
    text = line.mark_text(align="left", dx=5, dy=-5).encode(
        text=alt.condition(nearest, y, alt.value(" "))
    )

    # Draw a rule at the location of the selection
    rules = alt.Chart(df).mark_rule(color="gray").encode(x=x,).transform_filter(nearest)

    # Put the five layers into a chart and bind the data
    chart = alt.layer(line, selectors, points, rules, text).properties(
        width=600, height=300
    )
    return st.altair_chart(chart.interactive(), use_container_width=True)


def plot_forecast(df):
    return altair_plot(df, "date:T", "deaths:Q", "kind:N")


def plot_history_data(df):
    return altair_plot(df, x="Date:T", y="Deaths:Q", color="Country:N")
