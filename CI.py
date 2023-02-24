#Import Libarires
import streamlit as st
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns 
import datetime as dt
import warnings
warnings.filterwarnings('ignore')
from plotly.offline import init_notebook_mode,iplot
init_notebook_mode(connected=True)
from IPython.display import display, HTML
import plotly.graph_objs as go
import plotly.express as px
from plotly.offline import init_notebook_mode,iplot
init_notebook_mode(connected=True)
warnings.filterwarnings("ignore")
plt.rcParams["patch.force_edgecolor"] = True
plt.style.use('fivethirtyeight')
color = sns.color_palette()
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy import stats
from mpl_toolkits import mplot3d
from yellowbrick.cluster import KElbowVisualizer
from plotly.subplots import make_subplots

from streamlit_option_menu import option_menu
st.set_page_config(page_title='CRM Improvement', layout= 'wide')

ED = pd.read_csv('E:/Class/Third/Project/data.csv',encoding='unicode_escape',dtype ={'CustomerID' : str , 'InvoiceID' : str})
ED['InvoiceDate'] = pd.to_datetime(ED['InvoiceDate'])
ED.dropna(axis = 0, subset = ['CustomerID'], inplace = True)
ED['CustomerID'] = ED['CustomerID'].astype('int64')
ED = ED.loc[(ED['Quantity'] > 0) | (ED['UnitPrice'] >= 0)]
ED['amount_spent'] = ED['Quantity'] * ED['UnitPrice']
ED_new = ED[['InvoiceNo','InvoiceDate','StockCode','Description',
                    'Quantity','UnitPrice','amount_spent','CustomerID','Country']]

ED_new.insert(loc=2, column='year_month', value=ED_new['InvoiceDate'].map(lambda x: 100*x.year + x.month))
ED_new.insert(loc=3, column='month', value=ED_new.InvoiceDate.dt.month)
# +1 to make Monday=1.....until Sunday=7
ED_new.insert(loc=4, column='day', value=(ED_new.InvoiceDate.dt.dayofweek)+1)
ED_new.insert(loc=5, column='hour', value=ED_new.InvoiceDate.dt.hour)
   
with st.sidebar : 
    selected = option_menu(
        menu_title="Main Menu",options=['BI','Customer Segmentation','Recommended system'],menu_icon='cast',
        default_index=0
    )


if selected == 'BI':
    st.title(f"You have selected {selected}")
    
    st.header('This app created by Dysphoria team')
    st.title('Welcome to _Customer Improvement_ application :sunglasses:')
    st.subheader('Hello, *Welcome to this application!* ')
    with st.expander('Click here to read more about this application.'):
        st.write('In this app, we first have a view of the customers information - then we divide the customers into categories and cluster the customers and propose the products needed by each cluster to hold targeted campaigns according to the customer categories.')
    st.subheader(' ')
    st.subheader(' ')
    st.subheader('Visualization of customer data')
    st.markdown('Visualization of top 10 ')
    
    #How many orders made by the customers?
    most_sold_prodQ = ED.groupby(['Description'])['Quantity'].sum().sort_values(ascending=False)[:10]
    data1 = [go.Bar(x=most_sold_prodQ.index, 
                y=most_sold_prodQ.values)]
    layout1 = go.Layout(title="TOP 10 most sold products(Quantity)", title_x=0.5)
    fig1 = go.Figure(data=data1, layout=layout1)

    most_sold_prodT = ED.groupby(['Description'])['amount_spent'].sum().sort_values(ascending=False)[:10]
    data2 = [go.Bar(x=most_sold_prodT.index, 
                y=most_sold_prodT.values)]
    layout2 = go.Layout(title="TOP 10 most sold products(Total Price)", title_x=0.5)
    fig2 = go.Figure(data=data2, layout=layout2)

    most_sold_country = ED.groupby(['Country'])['amount_spent'].sum().sort_values(ascending=False)[:10]
    data3 = [go.Bar(x=most_sold_country.index, 
                y=most_sold_country.values)]
    layout3 = go.Layout(title="TOP 10 most sold Country(Total Price)", title_x=0.5 )
    fig3 = go.Figure(data=data3, layout=layout3)

    st.subheader(' ')
    tab1, tab2, tab3 = st.tabs(["TOP 10 most sold products(Quantity)","TOP 10 most sold products(Total Price)",
                                "TOP 10 most sold Country(Total Price)"])
    with tab1:
        st.plotly_chart(fig1,use_container_width=True)
    with tab2:
        st.plotly_chart(fig2,use_container_width=True)
    with tab3:
        st.plotly_chart(fig3,use_container_width=True)

    st.subheader(' ')
    st.subheader(' ')
    col1,col2 = st.columns(2)
    total_sales = int(ED['amount_spent'].sum())
    total_sales_mean = int(ED['amount_spent'].mean())
    with col1 :
        st.header('total sales of all years')
        st.subheader(f"US $ {total_sales:,}")
    with col2 :
        st.header('total sales mean of all years')
        st.subheader(f"US $ {total_sales_mean:,}")    
    st.subheader(' ')
    st.subheader(' ')

    temp = ED[['CustomerID', 'InvoiceNo', 'Country']].groupby(['CustomerID', 'InvoiceNo', 'Country']).count()
    temp = temp.reset_index(drop = False) 
    countries = temp['Country'].value_counts()

    data4 = dict(type='choropleth', locations = countries.index, locationmode = 'country names', z = countries, text = countries.index,
                colorbar = {'title':'Order nb.'},
                colorscale=[[0, 'rgb(224,255,255)'],
                [0.01, 'rgb(166,206,227)'], [0.02, 'rgb(31,120,180)'],
                [0.03, 'rgb(178,223,138)'], [0.05, 'rgb(51,160,44)'],
                [0.10, 'rgb(251,154,153)'], [0.20, 'rgb(255,255,0)'],
                [1, 'rgb(227,26,28)']], reversescale = False)
    #_______________________
    layout4 = dict(title='Number of orders per country', geo = dict(showframe = True, projection={'type':'mercator'}))
    #______________
    choromap = go.Figure(data = [data4], layout = layout4)
    st.plotly_chart(choromap)

    st.subheader(' ')
    st.subheader(' ')

    
    """"
    ax = ED_new.groupby('InvoiceNo')['year_month'].unique().value_counts().sort_index()
    data5 = [go.Bar(x=ax.index, 
                y=ax.values)]
    layout5 = go.Layout(title="Total orders in years_month", title_x=0.5)
    fig5 = go.Figure(data=data5, layout=layout5)
    st.plotly_chart(fig5)
    """
    most_sold = ED_new.groupby(['year_month'])['amount_spent'].sum().sort_values(ascending=False)[:10]

    data6 = [go.Bar(x=most_sold.index, 
                y=most_sold.values,)]

    layout6 = go.Layout(title="TOP 10 most sold products(Quantity)", title_x=0.5)

    fig6 = go.Figure(data=data6, layout=layout6)
    st.plotly_chart(fig6)
    st.dataframe(ED_new.head())



    # Layout (Sidebar)
    st.sidebar.markdown("## Settings")
    startdate = st.sidebar.date_input("start date",ED_new['InvoiceDate'].min())
    enddate = st.sidebar.date_input("end date",ED_new['InvoiceDate'].max())
    customersid = st.sidebar.selectbox('CustomerID', options= ED_new['CustomerID'].sort_values().unique())
    countryid = st.sidebar.multiselect('Country name',options= ED_new['Country'].unique(),default=ED_new['Country'].unique())
    yearmonthid = st.sidebar.multiselect('yearmonth', ED_new['year_month'].unique(),default=ED_new['year_month'].unique())
    monthid = st.sidebar.multiselect('month', ED_new['month'].unique(),default=ED_new['month'].unique())
    dayid = st.sidebar.multiselect('day', ED_new['day'].unique(),default=ED_new['day'].unique())
    ED_selection = ED_new.query(
        "CustomerID == @customersid & Country == @countryid & year_month == @yearmonthid & month== @monthid & day == @dayid"
    )
    sales_by_customer=ED_selection.groupby(by=['year_month']).sum()[['amount_spent']]
    fig_customer = px.line(sales_by_customer,x=sales_by_customer.index,y='amount_spent')
    st.plotly_chart(fig_customer)

if selected == 'Customer Segmentation' :
    st.title(f"You have selected {selected}")
    st.header('Welecome to this page')    
    st.subheader('RFM Grouping Customers')
    with st.expander('Click here to read more about RFM.'):
        st.write('RFM analysis is a marketing technique used to quantitatively rank and group customers based on the recency, frequency and monetary total of their recent transactions to identify the best customers and perform targeted marketing campaigns.')
    ED_new['InvoiceDate'].max()
    now = dt.datetime(2011,12,10)
    rfm = ED_new.groupby('CustomerID').agg({'InvoiceDate' : lambda day : (now - day.max()).days,
                                     'InvoiceNo' : lambda num :len(num),
                                     'amount_spent' : lambda price : price.sum()})
    col_list = ['Recency', 'Frequency', 'Monetary']
    rfm.columns = col_list
    rfm["R"] = pd.qcut(rfm['Recency'], 5 , labels = [5, 4, 3, 2, 1])
    rfm["F"] = pd.qcut(rfm['Frequency'], 5 , labels = [5, 4, 3, 2, 1])
    rfm["M"] = pd.qcut(rfm['Monetary'], 5 , labels = [5, 4, 3, 2, 1])

    rfm['RFM_Score'] = rfm["R"].astype(str)+rfm["F"].astype(str)+rfm["M"].astype(str)
    seg_map = {
    r'[1-2][1-2]': 'Hibernating',
    r'[1-2][3-4]' : 'At Risk',
    r'[1-2]5' : 'Can\'t Lose',
    r'3[1-2]' : 'About to Sleep',
    r'33' : 'Need Attention',
    r'[3-4][4-5]' : 'Loyal Customers',
    r'41' : 'Promising',
    r'51' : 'New Customers',
    r'[4-5][2-3]' : 'Potential Loyalists',
    r'5[4-5]' : 'Champions'
    }
    rfm['Segment'] = rfm['R'].astype(str) + rfm['F'].astype(str)
    rfm['Segment'] = rfm['Segment'].replace(seg_map, regex = True)
    rfm.reset_index(inplace=True)
    st.dataframe(rfm[['CustomerID','Segment']])
    segments_count = rfm.groupby("Segment").agg({"CustomerID": "count"})
    segments_count.reset_index(inplace=True)
    segments_count.columns = ['segment', 'count']
    Segment_map = rfm.Segment.value_counts()
    fig7 = px.treemap(Segment_map, path=[Segment_map.index], values=Segment_map)
    fig7.update_layout(title_text='Distribution of the RFM Segments', title_x=0.5,
                  title_font=dict(size=20))
    fig7.update_traces(textinfo="label+value+percent root")
    st.plotly_chart(fig7)
    result = pd.merge(ED_new, rfm, on="CustomerID", how="outer")
    st.dataframe(result)
    
    countryid2 = st.sidebar.multiselect('Country name',options= result['Country'].unique(),default=result['Country'].unique())
    segmentid2 = st.sidebar.multiselect('Segment name',options= result['Segment'].unique(),default=result['Segment'].unique())
    result_selection = result.query( "Country == @countryid2 & Segment == @segmentid2 ")
                                    
    #sales_by_customer=ED_selection.groupby(by=['year_month']).sum()[['amount_spent']]
    #fig_customer = px.line(sales_by_customer,x=sales_by_customer.index,y='amount_spent')
    #st.plotly_chart(fig_customer)
    
    most_sold_Segment = result_selection.groupby(['Segment'])['amount_spent'].sum().sort_values(ascending=False)
    
    data8 = [go.Bar(x=most_sold_Segment.index, 
               y=most_sold_Segment.values)]

    layout8 = go.Layout(title="sold products(Total Price) By customer grouping", title_x=0.5 )

    fig8 = go.Figure(data=data8, layout=layout8)
    st.plotly_chart(fig8)
    st.subheader('download RFM grouping customer')
    st.write('click button to download')
    def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

    csv = convert_df(rfm)

    st.download_button(
        label="Download rfm as CSV",
        data=csv,
        file_name='rfm.csv',
        mime='text/csv',
    )
    st.subheader('Clustering(k-means) Grouping Customers')
    with st.expander('Click here to read more about k-means.'):
        st.write('customer clustering analysis is the use of a mathematical model to discover groups of similar customers based on finding the smallest variations among customers within each group. These homogeneous groups are known as “customer archetypes” or “personas”.')
    
    ED_clustering = ED_new.groupby('CustomerID').agg({'InvoiceDate': lambda InvoiceDate: (now - InvoiceDate.max()).days,
                                     'InvoiceNo'    : 'nunique',
                                     'amount_spent' : 'sum'})

    ED_clustering.columns = ['Recency', 'Frequency', 'Monetary']
    std_scaler = StandardScaler()
    ED_scaled = std_scaler.fit_transform(ED_clustering)
    ED_scaled = pd.DataFrame(ED_scaled,columns=['Recency', 'Frequency', 'Monetary'])
    ED_scaled["CustomerID"] = ED_clustering.index
    ED_scaled = ED_scaled.set_index("CustomerID",drop=True)
    model = KMeans()
    visualizer = KElbowVisualizer(model, k=(1,11), timings= False)
    visualizer.fit(ED_scaled)        
    visualizer.show()  
    import sklearn.metrics as metrics
    import sklearn.cluster as cluster
    SK = range(3,11)
    sil_score = []
    for i in SK:
        labels=cluster.KMeans(n_clusters=i,init="k-means++",random_state=200).fit(ED_scaled).labels_
        score = metrics.silhouette_score(ED_scaled,labels,metric="euclidean",sample_size=1000,random_state=200)
        sil_score.append(score)
        print ("Silhouette score for k(clusters) = "+str(i)+" is "
            +str(metrics.silhouette_score(ED_scaled,labels,metric="euclidean",sample_size=1000,random_state=200)))
        
    sil_centers = pd.DataFrame({'Clusters' : SK, 'Sil Score' : sil_score})
    Optimiazation_Center=sil_centers.loc[sil_centers['Sil Score'].idxmax()]
    print(Optimiazation_Center)
    Optimiazation_Center['Clusters']
    kmeans = KMeans(n_clusters=4, n_init = 15, random_state=1)
    kmeans.fit(ED_scaled)
    centroids = kmeans.cluster_centers_
    centroid_df = pd.DataFrame(centroids, columns = list(ED_scaled) )
    df_labels = pd.DataFrame(kmeans.labels_ , columns = list(['labels']))
    df_labels['labels'] = df_labels['labels'].astype('category')
    df_kmeans = ED_clustering.copy()
    df_kmeans['labels'] = df_labels['labels'].values
    result_Kmeans = pd.merge(ED, df_kmeans, on="CustomerID", how="outer")
    st.dataframe(result_Kmeans)
    """segment_option = result['Segment'].unique().tolist()
    date_option = result['year_month'].unique().tolist() 
    date = st.selectbox('which date would you like to see',date_option,100)
    segmentaion = st.multiselect('which date would you like to see',segment_option)
    result = result[result['Segment'].isin(Segment)]
    fig9 = px.bar(result,x='Segment',)"""
    
#vars_cont = ED_new['CustomerID'].sort_values(ascending=False).unique()
#vars_cont2 = ED_new['year_month'].unique()
#cat_selected = st.sidebar.selectbox('Categorical Variables', vars_cont)
#cont_multi_selected = st.multiselect('Correlation Matrix', vars_cont2,
#                                     default=vars_cont2)
#st.dataframe(ED)




