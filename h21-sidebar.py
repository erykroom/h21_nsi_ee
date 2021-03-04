import streamlit as st
import pandas as pd
import networkx as nx
import altair as alt
from vega_datasets import data
# import matplotlib.pyplot as plt


def valik(df_x):
    cn6 = df_x['cn6'].unique()
    make_choice = st.sidebar.selectbox('Select the product category:', cn6)
    df = df_x.loc[(df_x['cn6'] == make_choice)]
    return df
 

def heat_valik(x):
    cn6 = x['cn6'].unique()
    fl = x['FLOW'].unique()
    with st.beta_expander("Filter and select data"):
        cn6_choice = st.selectbox('Select the product category:', cn6)
        x = x[x["cn6"] == cn6_choice]
        flow_choice = st.selectbox('Select import or export', fl) 
    flow = x[x['FLOW'] == flow_choice]
    return flow


def tulbad_valik(x):
    cn6 = x['cn6'].unique()
    dec = x['DECLARANT'].unique()
    #cn6 = pd.Series(["All"]).append(x['cn6'], ignore_index=True).unique()
    #dec = pd.Series(["All"]).append(x['FLOW'], ignore_index=True).unique()
    #if cn6_choice != 'All':
    #    x = x[x["cn6"] == cn6_choice]
    #else:
    #    x = x
    with st.beta_expander("Filter and select data"):
        cn6_choice = st.selectbox('Select the product category:', cn6, key = "tulbad_selector")
        x = x[x["cn6"] == cn6_choice]
        dec_choice = st.selectbox('Select the declarant country', dec, key = "tulbad_selector") 
    flow = x[x['DECLARANT'] == dec_choice]
    return flow

def remap_cn6(x):
    di = {380894: "Disinfectants",
          220710: "Undenatured ethyl alcohol, strength >= 80%",
          220890: 'Ethyl alcohol, strength < 80%',
          284700: 'Hydrogen peroxide',
          152000: 'Glycerol',
          392330: 'Carboys, bottles, flasks',
          392350: 'Stoppers, lids, caps and other closures and similar articles',
          }
    x = x.replace({"cn6": di})
    return x


def tulbad_2():
    x = pd.read_csv('data/production19_long.csv', sep =';')
    x = x[(x['PRODUCT'] == 20201490) & ((x['COUNTRY'] == 'Estonia'))]
    source = x
    chart = (alt.Chart(source).mark_bar().encode(
        x=alt.X('VALUE', title='VALUE IN EUR'),
        y=alt.Y('FLOW:O', title=''),
        tooltip=[
            alt.Tooltip('VALUE', title='VALUE IN EUR')
        ]
    ))
    st.altair_chart(chart)


def jooned_m():
    x = pd.read_csv('data/jooned.csv', sep=';')
    x = x[(x['cn6'] == 380894) & ((x['DECLARANT'] == 'EE')) & (((x['FLOW'] == 'Export')))]
    source = x

    chart = (alt.Chart(source).mark_line(point=True, strokeWidth=5).encode(
        x='MONTH:O',
        y=alt.Y('SUM1000', title='FLOW SUM IN THOUSANDS EUROS'),
        color=alt.Color('YEAR:O', scale=alt.Scale(scheme='category10')),
        tooltip=[
            alt.Tooltip('SUM1000:O', title='FLOW SUM')
        ]
    ).properties(width=500, height=500))
    st.altair_chart(chart)
    #return chart


def jooned_y():
    #chart1 = jooned_m()
    x = pd.read_csv('data/tulbad.csv', sep=';', decimal=',')
    x = remap_cn6(x)
    source = tulbad_valik(x) 
    chart2 = alt.Chart(source).mark_line(point=True, strokeWidth=5).encode(
        x='YEAR:O',
        y=alt.Y('PROPORTION:Q', title = 'PROPORTION OF PRODUCT IN COUNTRY TOTAL (%)'),
        color=alt.Color('FLOW:N', scale=alt.Scale(scheme='category10')),
        tooltip=[
            alt.Tooltip('PROPORTION', title='Proportion (%)')
        ]
    ).properties(width=500, height=500)
    #chart = alt.hconcat(chart1, chart2).resolve_scale(color='shared')
    st.altair_chart(chart2)


def heatmap():
    x = pd.read_csv('data/heatmap1.csv', sep=';')
    x['FLOWSUM'] = x['FLOWSUM'].astype(int)
    x = remap_cn6(x)
    source = heat_valik(x)
    base = alt.Chart(source).encode(
        alt.X('DECLARANT:O', scale=alt.Scale(paddingInner=0)),
        alt.Y('MONTH:O', scale=alt.Scale(paddingInner=0)),
        tooltip=[alt.Tooltip('FLOWSUM', title='Flow sum (EUR)')])
    heatmap = base.mark_rect().encode(
        color=alt.Color('PARTNER:O', scale=alt.Scale(scheme='category20'), legend=None))
    text = base.mark_text(baseline='middle').encode(text='PARTNER:O')
    chart = (heatmap + text).properties(width=700, height=500)
    st.altair_chart(chart)


def kaart_plot():
    df = pd.read_csv('data/edges_puhastus2019.csv', sep=';')
    df = remap_cn6(df)
    countries = pd.read_csv('countries.csv', sep=';')
    world = alt.topo_feature(data.world_110m.url, 'countries')

    conns = valik(df)
    # Create mouseover selection
    select_country = alt.selection_single(
        on="mouseover", nearest=True, fields=["origin"], empty="none"
    )
    lookup_data = alt.LookupData(countries, key="country", fields=["name", "latitude", "longitude"])
    background = alt.Chart(world).mark_geoshape(fill="lightgray",
                                                stroke="white"
                                                ).properties(width=1000,
                                                            height=800
                                                ).project(type='naturalEarth1')
    connections = alt.Chart(conns).mark_rule(opacity=0.35).encode(
        latitude="latitude:Q",
        longitude="longitude:Q",
        latitude2="lat2:Q",
        longitude2="lon2:Q"
    ).transform_lookup(
        lookup="origin",
        from_=lookup_data
    ).transform_lookup(
        lookup="destination",
        from_=lookup_data,
        as_=["country", "lat2", "lon2"]
    ).transform_filter(
        select_country
    )
    points = alt.Chart(conns).mark_circle().encode(
        latitude="latitude:Q",
        longitude="longitude:Q",
        size=alt.Size("connections:Q", scale=alt.Scale(range=[0, 400]), legend=None),
        order=alt.Order("connections:Q", sort="descending"),
        tooltip=["origin:N", "connections:Q"]
    ).transform_aggregate(
        connections="count()",
        groupby=["origin"]
    ).transform_lookup(
        lookup="origin",
        from_=lookup_data
    ).add_selection(
        select_country
    )
    st.altair_chart((background + connections + points).configure_view(stroke=None).resolve_scale())


def main():
    st.set_page_config(
        page_title="h21-NSI-EE",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.sidebar.title('BD Hackathon 2021 Estonia')
    st.sidebar.markdown(
        """
This page is a dashboard prototype that shows international trade flows connected to EU. The example data is focused to
a product category that has shown increase during the time of pandemic: disinfectants. To illustrate possible supply
chains connected to the production of disinfectants several other products that are needed in the production of
disinfectants are also shown in the graphs.
"""
    )
    st.subheader("International trade flows to and from Europe in 2019")
    kaart_plot()
    st.markdown(
       """
International trade flows to and from EU in 2019. The size of the country node
shows the number of trade flows to and from other countries. Data: Comext yearly data.
"""
    )

    st.subheader("The most important partner country by trade flow in 2020")
    heatmap()
    st.markdown(
        """
The heatmap presents the most important partner country for each declarant country in 2020. Importance is measured in trade value in EUR: flow sum in the given product category. Data: Comext monthly data
"""
    )

# Tabeli pealkiri
# Number of trade connections (degree) by country, product and flow.
# Tabeli selgitus
# International trade flows to and from EU in 2019. Data: Comext yearly data.
#
# Joondiagramm 1 pealkiri (see, mille teljel on kuu)
# Export/import value in 2020
# Joondiagrammi 1 selgitus
# The graph presents trade values in EUR by flow, country and product in 2020. Data: Comext montly data
#
# Joondiagramm 2 pealkiri (see, mille teljel on aastad)
# Proportion (in %) of the selected product in the country’s total export or import value
# Joondiagrammi 2 selgitus
# The graph compares trade values of the chosen product to total trade value (by flow, country) in the years 2015-2019. Data: Comext yearly data
#
# Tulpdiagramm
# Export, import and production in 2019 (value in EUR)
# The graph shows the export, import and production values for the chosen country and product in 2019. Data: PRODCOM

    st.subheader("Export/import value in 2020")
    jooned_m()
    st.markdown(
    """
The graph presents trade values in EUR by flow, country and product in 2020. Data: Comext montly data.
"""
    )

    st.subheader("Proportion (in %) of the selected product in the country’s total export or import value")
    jooned_y()
    st.markdown(
    """
The graph compares trade values of the chosen product to total trade value (by flow, country) in the years 2015-2019.
Data: Comext yearly data.
"""
    )

    tulbad_2()
    #st.balloons()


if __name__ == '__main__':
    main()
