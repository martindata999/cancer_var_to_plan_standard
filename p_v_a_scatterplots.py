import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Given dictionary of NHS Trusts
nhs_trusts = {
    'RN7': 'Dartford',
    'RVV': 'E Kent',
    'RWF': 'Maidstone',
    'RPA': 'Medway',
    'RDU': 'Frimley',
    'RXC': 'E Sussex',
    'RPC': 'Q Victoria',
    'RYR': 'UH Sussex',
    'RN5': 'Hampshire Hospitals',
    'R1F': 'Isle Of Wight',
    'RHU': 'Portsmouth',
    'RHM': 'Southampton Univ',
    'RXQ': 'Buckinghamshire',
    'RTH': 'Oxford Univ',
    'RHW': 'Ryl Berkshire',
    'RTK': 'Ashford',
    'RA2': 'Ryl Surrey',
    'RTP': 'Surrey & Sussex'
}

# Create a dictionary for quick lookup
trust_dict = nhs_trusts

# Import data
data_plan = pd.read_csv("C:/Users/martin.bloyce/OneDrive - NHS/Documents - " +
                "Regional Analytics - South East/South East/Analysis" +
                "/Planning/2024-25/Plan_vs_Actual/data_csvs/Plans_2425.csv"
                )

# Filter rows
plan_refs = data_plan["planning_ref"].isin(["E.B.35","E.B.27"])
orgs_only = data_plan["icb_code"] != data_plan["org_code"]
pc_only = data_plan["measure_type"] == "Percentage"

data_plan = data_plan[plan_refs & orgs_only & pc_only]

# Filter columns
data_plan = data_plan[["org_code", "dimension_name", "planning_ref", "metric_value"]]

# Rename value column
data_plan.rename(columns={'metric_value': 'plan'}, inplace=True)

# Bring in actuals data
data_actuals = pd.read_csv("C:/Users/martin.bloyce/OneDrive - NHS/Documents - " +
                "Regional Analytics - South East/South East/Analysis" +
                "/Planning/2024-25/Plan_vs_Actual/data_csvs/current_actuals.csv"
                )

# Filter rows
plan_refs = data_actuals["planning_ref"].isin(["E.B.35","E.B.27"])
orgs_only = data_actuals["icb_code"] != data_actuals["org_code"]
pc_only = data_actuals["measure_type"] == "Percentage"

data_actuals = data_actuals[plan_refs & orgs_only & pc_only]

# Filter columns
data_actuals = data_actuals[["org_code", "dimension_name", "planning_ref", "metric_value"]]

# Rename value column
data_actuals.rename(columns={'metric_value': 'actual'}, inplace=True)

# Merge data_plan and data_actuals
data = pd.merge(data_plan, data_actuals, 
on=["org_code", "dimension_name", "planning_ref"])

# Change dimension_name to dates and filter for latest month
data["dimension_name"] = pd.to_datetime(data["dimension_name"], format="%b-%y")
latest_date = data["dimension_name"].max()
data = data[data["dimension_name"] == latest_date]

# Create calculated columns to show distance from plan and distance from target
data["plan_var"] = data["actual"] - data["plan"]
data['standard_var'] = data.apply(lambda row: 70 - row['actual'] 
if row['planning_ref'] == 'E.B.35' else 77 - row['actual'], axis=1)

# Rename planning_refs to friendly names
data["planning_ref"].replace(
    {'E.B.35':'Cancer 62-day pathways. Total patients seen, and of which those seen within 62 days', 'E.B.27': 'Cancer 28 day waits (faster diagnosis standard)'}, inplace=True)

# Reset index to ensure proper indexing
data.reset_index(drop=True, inplace=True)

# Create chart outputs using fig, ax, split by planning_ref
unique_refs = data["planning_ref"].unique()

# Create chart template area
fig, axs = plt.subplots(1, len(unique_refs), figsize=(15, 6), sharey=True)

# Ensure axs is always iterable
if len(unique_refs) == 1:
    axs = [axs]

# Create charts (one per metric)
for i, ref in enumerate(unique_refs):
    subset_data = data[data["planning_ref"] == ref]
    axs[i].scatter(subset_data["plan_var"], subset_data["standard_var"], 
    c="blue")
    axs[i].set_xlabel("Variance from plan")
    axs[i].set_ylabel("Variance from standard")
    axs[i].set_title(f"{ref}")
    
    for j in range(len(subset_data)):
        ods_code = subset_data["org_code"].iloc[j]
        short_name = trust_dict.get(ods_code, short_name)  # Use ODS code if short name not found
        axs[i].annotate(short_name, 
                        (subset_data["plan_var"].iloc[j], subset_data["standard_var"].iloc[j]), 
                        xytext=(5, 5), textcoords='offset points')

    # Draw vertical and horizontal lines at zero
    axs[i].axvline(0, color='gray', linestyle='--')
    axs[i].axhline(0, color='gray', linestyle='--')

# Layout and show charts
plt.tight_layout()
plt.show()
