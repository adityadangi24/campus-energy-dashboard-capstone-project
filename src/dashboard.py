import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
from pathlib import Path

class MeterReading:
    def __init__(self, timestamp, kwh):
        self.timestamp = timestamp
        self.kwh = kwh

class Building:
    def __init__(self, name):
        self.name = name
        self.meter_readings = []

    def add_reading(self, reading):
        self.meter_readings.append(reading)

    def calculate_total_consumption(self):
        return sum(r.kwh for r in self.meter_readings)

class BuildingManager:
    def __init__(self):
        self.buildings = {}

    def add_building(self, b):
        self.buildings[b.name] = b

def ingest_data():
    base = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(base,"data")
    df_list=[]
    for file in Path(data_path).glob("*.csv"):
        df=pd.read_csv(file,parse_dates=['timestamp'])
        df['building']=file.stem
        df_list.append(df)
    return pd.concat(df_list,ignore_index=True)

def aggregate(df):
    daily=df.resample("D",on="timestamp")['kwh'].sum()
    weekly=df.resample("W",on="timestamp")['kwh'].sum()
    summary=df.groupby("building")['kwh'].agg(['mean','min','max','sum'])
    return daily,weekly,summary

def create_dashboard(df):
    base = os.path.dirname(os.path.dirname(__file__))
    out=os.path.join(base,"output")
    os.makedirs(out,exist_ok=True)

    fig,ax=plt.subplots(1,3,figsize=(15,5))

    daily=df.resample("D",on="timestamp")['kwh'].sum()
    ax[0].plot(daily.index,daily.values)
    ax[0].set_title("Daily Trend")

    weekly=df.resample("W",on="timestamp")['kwh'].mean()
    ax[1].bar(range(len(weekly)),weekly.values)
    ax[1].set_title("Weekly Avg Comparison")

    ax[2].scatter(df['timestamp'],df['kwh'])
    ax[2].set_title("Peak Load Scatter")

    plt.savefig(os.path.join(out,"dashboard.png"))
    plt.close()

def save_outputs(df,summary):
    base = os.path.dirname(os.path.dirname(__file__))
    out=os.path.join(base,"output")
    df.to_csv(os.path.join(out,"cleaned_energy_data.csv"),index=False)
    summary.to_csv(os.path.join(out,"building_summary.csv"))

    total=df['kwh'].sum()
    peak=df.loc[df['kwh'].idxmax()]
    high_building=summary['sum'].idxmax()

    txt=f"Total: {total}\nPeak Time: {peak['timestamp']}\nHighest Building: {high_building}"
    with open(os.path.join(out,"summary.txt"),"w") as f: f.write(txt)

def main():
    df=ingest_data()
    daily,weekly,summary=aggregate(df)
    create_dashboard(df)
    save_outputs(df,summary)
    print("Capstone Complete")

if __name__=="__main__":
    main()
