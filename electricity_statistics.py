import pandas as pd
import streamlit as st
import plotly.express as px
from astropy import units as u
from astroquery.nasa_exoplanet_archive import NasaExoplanetArchive
import time
import numpy as np
import os
import my_function
import plotly.graph_objs as go
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

postal_code_dict = {"台北市":["100","103","104","105","106","108","110","110","111","112","114","115","116"],
                    "新北市":["207","208","220","221","222","223","224","226","227","228","231","232","233","234","235",
                              "236","237","238","239","241","242","243","244","247","248","249","251","252","253"],
                    "桃園市":["320","324","325","326","327","328","330","333","334","335","336","337","338"],
                    "台中市":["400","401","402","403","404","406","407","408","411","412","413","414","420","421","422",
                              "423","424","426","427","428","429","432","433","434","435","436","437","438","439"],
                    "台南市":["710","711","712","713","714","715","716","717","718","719","720","721","722","723","724",
                              "725","726","727","730","731","732","733","734","735","736","737","741","742","743","744",
                              "745","700","701","702","704","708","709"],
                    "高雄市":["800","801","802","803","804","805","806","807","811","812","813","814","815","820","821",
                              "822","823","824","825","826","827","828","829","830","831","832","833","840","842","843",
                              "844","845","846","847","848","849","851","852"],
                    "新竹縣市":["300","302","303","304","305","306","307","308","310","311","312","313","314","315"],
                    "澎湖縣":["880","881","882","883","884","885"],
                    "金門縣":["890","891","892","893","894","896"],
                    "連江縣":["209","210","211","212"]}

def reload_electricity_data():
    start_time = time.time()
    data_df = pd.DataFrame()
    for i in range(104, 112):
        filename = r"用電統計資料/{}.csv".format(str(i))
        file_exist = os.path.isfile(filename)
        if file_exist == True:
            try:
                temp_df = pd.read_csv(filename, encoding='Big5')
            except:
                temp_df = pd.read_csv(filename, encoding='UTF8')
            data_df = pd.concat([data_df, temp_df])

    data_df["年度"] = data_df["年度"].apply(lambda x: int(x) + 1911)
    data_df["月份"] = data_df["月份"].apply(lambda x: int(x))
    data_df["郵遞區號"] = data_df["郵遞區號"].apply(lambda x: str(x))
    data_df["用電種類"] = data_df["用電種類"].apply(lambda x: ''.join([i.strip() for i in x if not i.isdigit()]))

    def convert_to_int(x):

        if (x.replace(",", "").isdigit()) == True:
            return int(x.replace(",", ""))
        else:
            return 0

    data_df["用戶數"] = data_df["用戶數"].apply(lambda x: convert_to_int(x))
    data_df["售電度數(當月)"] = data_df["售電度數(當月)"].apply(lambda x: convert_to_int(str(x)))
    use_type_list = ['表燈非營業用', '表燈營業用', '高壓電力']
    results = []

    for year in range(2015, 2023):
        for month in range(1, 13):

            fillter_1 = data_df["年度"] == year
            fillter_2 = data_df["月份"] == month

            for area in postal_code_dict.keys():
                postal_code_list = postal_code_dict[area]
                fillter_3 = data_df["郵遞區號"].isin(postal_code_list)

                for use_type in use_type_list:
                    fillter_4 = data_df["用電種類"] == use_type

                    temp_df = data_df[fillter_1 & fillter_2 & fillter_3 & fillter_4]

                    number_of_households = temp_df["用戶數"].sum()
                    use_electricity = temp_df["售電度數(當月)"].sum()

                    date = str(year) + "-" + str(month)
                    results.append([year, month, use_type, date, area, number_of_households, use_electricity])
    results_df = pd.DataFrame(results, columns=["Year", "Month", "Type", "Date", "Area", "Number of Households", "Use Electricity"])
    my_function.save_obj(results_df,"用電統計暫存資料\\用電統計")

    end_time = time.time()
    spent_time = "{} s".format(round(end_time - start_time), 2)
    st.title('暫存檔完成 ' + spent_time)

    return results_df


def show_用電戶數統計數據():
    st.title('用電戶數統計數據')
    electricity_data_df = my_function.load_obj(r"用電統計暫存資料/用電統計.pkl")
    city_list = ['台北市', '新北市', '桃園市', '台中市', '台南市', '高雄市', '新竹縣市']
    use_type_list = ['表燈非營業用','表燈營業用','高壓電力']

    for use_type in use_type_list:
        df = pd.DataFrame()
        for city in city_list:
            b = electricity_data_df["Area"] == city
            c = electricity_data_df["Type"] == use_type
            d = electricity_data_df["Number of Households"] != 0
            dd = electricity_data_df[b & c & d][["Date","Number of Households"]]
            dd = dd.rename(columns={'Number of Households': city})

            if len(df) == 0:
                df = dd
            else:
                df = pd.merge(df,dd,on="Date")

        fig = px.line(df, x='Date', y=city_list,title='用電戶數({})'.format(use_type))

        fig.update_xaxes(dtick="M3",ticklabelmode="period")
        # fig.show()

        layout = go.Layout(
            title='用電戶數({})'.format(use_type),
            xaxis={'title': '日期'},
            yaxis={'title': '戶數'},
            showlegend=True,
            font={
                'size': 14,
            },
        )
        fig.layout = layout

        st.plotly_chart(fig, use_container_width=True)
    return None

def show_使用電量():
    st.title('使用電量統計數據')
    electricity_data_df = my_function.load_obj(r"用電統計暫存資料/用電統計.pkl")
    city_list = ['台北市', '新北市', '桃園市', '台中市', '台南市', '高雄市', '新竹縣市']
    use_type_list = ['表燈非營業用','表燈營業用','高壓電力']

    for use_type in use_type_list:
        df = pd.DataFrame()
        for city in city_list:
            b = electricity_data_df["Area"] == city
            c = electricity_data_df["Type"] == use_type
            d = electricity_data_df["Use Electricity"] != 0
            dd = electricity_data_df[b & c & d][["Date","Use Electricity"]]
            dd = dd.rename(columns={'Use Electricity': city})

            if len(df) == 0:
                df = dd
            else:
                df = pd.merge(df,dd,on="Date")

        fig = px.line(df, x='Date', y=city_list,title='使用電量({})'.format(use_type))

        fig.update_xaxes(dtick="M3",ticklabelmode="period")
        # fig.show()

        layout = go.Layout(
            title='使用電量({})'.format(use_type),
            xaxis={'title': '日期'},
            yaxis={'title': '戶數'},
            showlegend=True,
            font={
                'size': 14,
            },
        )
        fig.layout = layout

        st.plotly_chart(fig, use_container_width=True)
    return None

def show_path():
    st.title(os.path.dirname(os.path.abspath(__file__)))

    filename = "用電統計資料"
    file_exist = os.path.isdir(filename)
    st.header(str(file_exist))

    filename = "用電統計資料"
    file_exist = os.path.exists(filename)
    st.header(str(file_exist))

    filename = r"用電統計資料/104.csv"
    file_exist = os.path.exists(filename)
    st.header(str(file_exist))
