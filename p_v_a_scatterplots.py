import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import streamlit as st

# Given dictionary of NHS Trusts
nhs_trusts = {
    'RHW': 'RBH'
    ,'RTH': 'OUH'
    ,'RXQ': 'BHT'
    ,'RDU': 'Frimley'
    ,'R1F': 'IOW'
    ,'RHM': 'UHS'
    ,'RHU': 'PHU'
    ,'RN5': 'HHFT'
    ,'RN7': 'DGT'
    ,'RPA': 'MFT'
    ,'RVV': 'EKH'
    ,'RWF': 'MTW'
    ,'RA2': 'RSCH'
    ,'RTK': 'ASP'
    ,'RTP': 'SASH'
    ,'RPC': 'QVH'
    ,'RXC': 'ESH'
    ,'RYR': 'UHSX'
    ,'QU9': 'BOB'
    ,'QNQ': 'Frim'
    ,'QRL': 'HIOW'
    ,'QKS': 'K&M'
    ,'QXU': 'SH'
    ,'QNX': 'SSX'
    ,'Y59': 'SE'
}

# Create a dictionary for quick lookup
trust_dict = nhs_trusts

# Import data
# data_plan = pd.read_csv("data/Plans_2425.csv")
data_plan = pd.read_excel("data/planvactual_testextract.xlsx",
                          sheet_name="plans")
data_actuals = pd.read_excel("data/planvactual_testextract.xlsx",
                          sheet_name="actuals")
data_targets = pd.read_excel("data/planvactual_testextract.xlsx",
                          sheet_name="targets")
data_metrics = pd.read_excel("data/planvactual_testextract.xlsx",
                          sheet_name="metrics")


# Create calculated field for plans and actuals, and drop old columns
data_plan['plan_value'] = data_plan['numerator'] / data_plan['denominator']
data_plan = data_plan.drop(['numerator', 'denominator'], axis=1)
data_actuals['actual_value'] = data_actuals['numerator'] / data_actuals['denominator']
data_actuals = data_actuals.drop(['numerator', 'denominator'], axis=1)

# Drop unnecessary columns from metrics lookup
data_metrics = data_metrics.drop(['MeasureSubject', 
                                 'MeasureType', 
                                 'Sentiment', 
                                 'NumberFormat'],
                                 axis=1)

# Merge data_plan and data_actuals
data = pd.merge(data_plan, data_actuals, 
                on=["org_code", "dimension_name", "planning_ref"])

# Merge to bring in metric names
data = pd.merge(data, data_metrics,
                on=["planning_ref"])

# Change dimension_name to dates and filter for latest month
data["dimension_name"] = pd.to_datetime(data["dimension_name"], format="%b-%y")
latest_date = data["dimension_name"].max()
data = data[data["dimension_name"] == latest_date]

# Create calculated columns to show distance from plan and distance from target
data["plan_var"] = data["actual_value"] - data["plan_value"]

# Bring in standards
# data['standard_var'] = data.apply(lambda row: row['actual'] - 
#                                   standard.get(row['planning_ref']), axis=1)
data = pd.merge(data, data_targets, on=["planning_ref"])

# Calculate distance from target
data["standard_var"] = data["actual_value"] - data["target"]

# Remove duplicates which exist for some reason
data = data.drop_duplicates()

# Reset index to ensure proper indexing
data.reset_index(drop=True, inplace=True)

# Create chart outputs using fig, ax, split by planning_ref
unique_refs = data["measure_name"].unique()

# create plot, based on what metric is chosen in the app
def plot_chart_1(chosen_metric):
    filtered_data = data[data["measure_name"] == chosen_metric]
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.scatter(filtered_data["plan_var"], filtered_data["standard_var"], c="blue")
    ax.set_xlabel("Variance from plan (percentage points)")
    ax.set_ylabel("Variance from target (percentage points)")
    ax.set_title(f"{chosen_metric}")

    for i in range(len(filtered_data)):
        ods_code = filtered_data["org_code"].iloc[i]
        short_name = trust_dict.get(ods_code, ods_code)
        ax.annotate(short_name, (filtered_data["plan_var"].iloc[i], filtered_data["standard_var"].iloc[i]), xytext=(5, 5), textcoords='offset points')

    ax.axvline(0, color='gray', linestyle='--')
    ax.axhline(0, color='gray', linestyle='--')

    ax.text(0.01, 0.99, 'Below plan, above standard', transform=ax.transAxes, ha='left', va='top', color='orange', alpha=0.4)
    ax.text(0.99, 0.99, 'Above plan & standard', transform=ax.transAxes, ha='right', va='top', color='green', alpha=0.4)
    ax.text(0.01, 0.01, 'Below plan & standard', transform=ax.transAxes, ha='left', va='bottom', color='red', alpha=0.4)
    ax.text(0.99, 0.01, 'Above plan, below standard', transform=ax.transAxes, ha='right', va='bottom', color='orange', alpha=0.4)

    plt.tight_layout()
    st.pyplot(fig)

# Define dataframe for use in streamlit app
def get_dataframe():
    return data