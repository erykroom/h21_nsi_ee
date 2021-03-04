import streamlit as st
import pandas as pd
import networkx as nx
import altair as alt
from vega_datasets import data

eu_dict = {
'AT':'Austria',
'BE':'Belgium',
'BG':'Bulgaria',
'HR':'Croatia',
'CY':'Cyprus',
'CZ':'Czech Republic',
'DK':'Denmark',
'EE':'Estonia',
'FI':'Finland',
'FR':'France',
'DE':'Germany',
'GR':'Greece',
'HU':'Hungary',
'IE':'Ireland',
'IT':'Italy',
'LV':'Latvia',
'LT':'Lithuania',
'LU':'Luxembourg',
'MT':'Malta',
'NL':'Netherlands',
'PL':'Poland',
'PT':'Portugal',
'RO':'Romania',
'SK':'Slovakia',
'SI':'Slovenia',
'ES':'Spain',
'SE':'Sweden'
}

def countrylist(opt):
    return eu_dict[opt]

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
    x = x.replace({"CN6": di})
    return x

def tabel(cn6_x, fl_x, decl_x):
    # Title
    st.subheader('Number of trade connections (degree) by country, product and flow.')
    x = pd.read_csv('data/app_data.csv', sep =';')
    x = remap_cn6(x)
    x = x[x['GRAPH'] == 'table_degree']
    x = x[x["CN6"] == cn6_x]

    tab = x[['COUNTRY','INDEGREE','OUTDEGREE','TOTAL_DEGREE']].set_index('COUNTRY')
    st.dataframe(tab)
    # Description
    st.markdown("""International trade flows to and from EU in 2019.
                Data: Comext [Comext](https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&dir=comext) yearly data.
                """)


def tulbad_2(cn6_x, decl_x):
    # Title
    st.subheader("Export, import and production in 2019 (value in EUR)")
    x = pd.read_csv('data/app_data.csv', sep =';')
    x = remap_cn6(x)
    x = x[x["CN6"] == cn6_x]
    x = x[x["CODE"] == decl_x]
    x = x[x["GRAPH"] == 'bar_production']
    source = x
    chart = (
        alt.Chart(source).mark_bar().encode(
            x=alt.X('VALUE', title='VALUE IN EUR'),
            y=alt.Y('FLOW:O', title=''),
            tooltip=[
                alt.Tooltip('VALUE', title='VALUE IN EUR')
            ]
)

    ).properties(width=950, height=200)
    st.altair_chart(chart)
    # Description
    st.write("""The graph shows the export, import and production values for the chosen country and product in 2019. Data:
    [PRODCOM](https://appsso.eurostat.ec.europa.eu/nui/show.do?query=BOOKMARK_DS-066341_QID_7C829C91_UID_-3F171EB0&layout=INDICATORS,C,X,0;DECL,L,Y,0;PRCCODE,B,Z,0;PERIOD,L,Z,1;&zSelection=DS-066341PERIOD,201852;DS-066341PRCCODE,07101000;&rankName1=PRCCODE_1_2_-1_2&rankName2=PERIOD_1_0_0_0&rankName3=INDICATORS_1_2_0_0&rankName4=DECL_1_2_0_1&sortR=DND_-1&prRK=FIRST&prSO=PROTOCOL&rLShi=0:13,1:22,2:8,3:15,4:32,5:10,6:7,7:12,8:26,9:11,10:4,11:20,12:33-1,14:31,15:30,17:21,16:25,19:9,18:38,21:18,20:16,23:6,22:24,25:19,24:29,27:5,26:27,29:14,31:36,30:39,34:0-1,32:35,33:37,38:3,39:2,36:17,37:23&rStp=&cStp=&rDCh=&cDCh=&rDM=true&cDM=true&footnes=false&empty=false&wai=false&time_mode=NONE&time_most_recent=false&lang=EN&cfo=%23%23%23%2C%23%23%23.%23%23%23&cxt_bm=1&lang=en)""")


def jooned_m(cn6_x, fl_x, decl_x):
    # Title
    st.subheader("Trade value in 2019-2020")
    x = pd.read_csv('data/jooned.csv', sep=';')
    x = remap_cn6(x)
    x = x[x["cn6"] == cn6_x]
    x = x[x["FLOW"] == fl_x]
    x = x[x["DECLARANT"] == decl_x]
    source = x

    chart = (alt.Chart(source).mark_line(point=True, strokeWidth=5).encode(
        x='MONTH:O',
        y=alt.Y('SUM1000', title='FLOW SUM IN THOUSANDS EUROS'),
        color=alt.Color('YEAR:O', scale=alt.Scale(scheme='category10')),
        tooltip=[
            alt.Tooltip('SUM1000:O', title='FLOW SUM')
        ]
    ).properties(width=1000, height=500))
    st.altair_chart(chart)
    # Description
    st.markdown("""
    The graph presents trade values in EUR by flow, country and product in 2019/20.
    Data: [Comext](https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&dir=comext) montly data.
                """)


def jooned_y(cn6_x, decl_x):
    # Title
    st.subheader("Proportion (in %) of the selected product in the country’s total export or import value")
    x = pd.read_csv('data/tulbad.csv', sep=';', decimal=',')
    x = remap_cn6(x)
    x = x[x["cn6"] == cn6_x]
    x = x[x["DECLARANT"] == decl_x]
    source = x
    chart2 = alt.Chart(source).mark_line(point=True, strokeWidth=5).encode(
        x='YEAR:O',
        y=alt.Y('PROPORTION:Q', title = 'PROPORTION OF PRODUCT IN COUNTRY TOTAL (%)'),
        color=alt.Color('FLOW:N', scale=alt.Scale(scheme='category10')),
        tooltip=[
            alt.Tooltip('PROPORTION', title='Proportion (%)')
        ]
    ).properties(width=1000, height=500)
    st.altair_chart(chart2)
    # Description
    st.markdown("""
    The graph compares trade values of the chosen product to total trade value (by flow, country) in the years 2015-2019.
    Data: [Comext](https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&dir=comext) yearly data.
                """)


def heatmap(cn6_x, fl_x):
    # Title
    st.subheader("The most important partner country by trade flow in 2020")
    x = pd.read_csv('data/heatmap1.csv', sep=';')
    x['FLOWSUM'] = x['FLOWSUM'].astype(int)
    x = remap_cn6(x)
    x = x[x["cn6"] == cn6_x]
    x = x[x["FLOW"] == fl_x]
    source = x
    base = alt.Chart(source).encode(
        alt.X('DECLARANT:O', scale=alt.Scale(paddingInner=0)),
        alt.Y('MONTH:O', scale=alt.Scale(paddingInner=0)),
        tooltip=[alt.Tooltip('FLOWSUM', title='Flow sum (EUR)')])
    heatmap = base.mark_rect().encode(
        color=alt.Color('PARTNER:O', scale=alt.Scale(scheme='category20'), legend=None))
    text = base.mark_text(baseline='middle').encode(text='PARTNER:O')
    chart = (heatmap + text).properties(width=940, height=500)
    st.altair_chart(chart)
    # Description
    st.markdown("""
    The heatmap presents the most important partner country for each declarant country in 2020.
    Importance is measured in trade value in EUR: flow sum in the given product category. Data:
    [Comext](https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&dir=comext) monthly data
                """)


def kaart_plot(cn6_x):
    # Title
    st.subheader("International trade flows to and from Europe in 2019")
    x = pd.read_csv('data/edges_puhastus2019.csv', sep=';')
    x = x.loc[:, ~x.columns.str.contains('^Unnamed')]
    x = remap_cn6(x)
    countries = pd.read_csv('countries.csv', sep=';')
    world = alt.topo_feature(data.world_110m.url, 'countries')
    x = x[x["cn6"] == cn6_x]
    conns = x
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
    # Description
    st.markdown("""
    International trade flows to and from EU in 2019. The size of the country node shows
    the number of trade flows to and from other countries. Data: 
    [Comext](https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&dir=comext) yearly data.
                """)


def main():
    st.set_page_config(
        page_title="h21-NSI-EE",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.sidebar.title('BD Hackathon 2021 Estonia')
    st.sidebar.markdown( """
    This page is a dashboard prototype that shows international trade flows connected to EU. The example data is focused to
    a product category that has shown increase during the time of pandemic: disinfectants. To illustrate possible supply
    chains connected to the production of disinfectants several other products that are needed in the production of
    disinfectants are also shown in the graphs.
                          """)
    cn6 = ["Disinfectants",
          "Undenatured ethyl alcohol, strength >= 80%",
          'Ethyl alcohol, strength < 80%',
          'Hydrogen peroxide',
          'Glycerol',
          'Carboys, bottles, flasks',
          'Stoppers, lids, caps and other closures and similar articles']
    cn6_choice = st.sidebar.selectbox('Select product category:', cn6)
    fl = ['Import', 'Export']
    fl_choice = st.sidebar.selectbox('Select import or export:', fl)
    decl_choice = st.sidebar.selectbox('Select country:', options=list(eu_dict.keys()), format_func=countrylist)
    kaart_plot(cn6_choice)
    tabel(cn6_choice, decl_choice, fl_choice)
    heatmap(cn6_choice, fl_choice)
    jooned_m(cn6_choice, fl_choice, decl_choice)
    jooned_y(cn6_choice, decl_choice)
    tulbad_2(cn6_choice, decl_choice)


if __name__ == '__main__':
    main()
