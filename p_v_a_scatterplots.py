import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

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
}

# Create a dictionary for quick lookup
trust_dict = nhs_trusts

# Import data
data_plan = pd.read_csv("C:/Users/martin.bloyce/OneDrive - NHS/Documents - " +
                "Regional Analytics - South East/South East/Analysis" +
                "/Planning/2024-25/Plan_vs_Actual/data_csvs/Plans_2425.csv"
                )

data_plan = data_plan[data_plan["source"] == 'June24_plan']

# Filter rows
plan_refs = data_plan["planning_ref"].isin(["E.B.35","E.B.27"])
orgs_only = data_plan["icb_code"] != data_plan["org_code"]
pc_only = data_plan["measure_type"] == "Percentage"

data_plan = data_plan[plan_refs & orgs_only & pc_only]

# Filter columns
data_plan = data_plan[
    ["org_code", "dimension_name", "planning_ref", "metric_value"]
    ]

# Rename value column
data_plan.rename(columns={'metric_value': 'plan'}, inplace=True)

# Bring in actuals data
data_actuals = pd.read_csv("C:/Users/martin.bloyce/OneDrive - NHS/Documents -" +
                " Regional Analytics - South East/South East/Analysis" +
                "/Planning/2024-25/Plan_vs_Actual/data_csvs/current_actuals.csv"
                )

# Filter rows
plan_refs = data_actuals["planning_ref"].isin(["E.B.35","E.B.27"])
orgs_only = data_actuals["icb_code"] != data_actuals["org_code"]
pc_only = data_actuals["measure_type"] == "Percentage"

data_actuals = data_actuals[plan_refs & orgs_only & pc_only]

# Filter columns
data_actuals = data_actuals[
    ["org_code", "dimension_name", "planning_ref", "metric_value"]
    ]

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
# using March 2025 ambition -- 
data['standard_var'] = data.apply(lambda row: row['actual'] - 70
if row['planning_ref'] == 'E.B.35' else row['actual'] - 77, axis=1)

# Rename planning_refs to friendly names
data["planning_ref"].replace(
    {'E.B.35':
    "Cancer 62-day pathways. Total patients seen, and of which those seen " +
    "within 62 days", 
    'E.B.27': 
    'Cancer 28 day waits (faster diagnosis standard)'}, 
    inplace=True
    )

# Remove duplicates which exist for some reason
data = data.drop_duplicates()

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
    axs[i].set_xlabel("Variance from plan (percentage points)")
    axs[i].set_ylabel("Variance from Mar '25 interim target (percentage points)")
    axs[i].set_title(f"{ref}")
    
    for j in range(len(subset_data)):
        ods_code = subset_data["org_code"].iloc[j]
        # Use ODS code if short name not found
        short_name = trust_dict.get(ods_code, ods_code)  
        axs[i].annotate(short_name, 
                        (subset_data["plan_var"].iloc[j], 
                        subset_data["standard_var"].iloc[j]), 
                        xytext=(5, 5), textcoords='offset points')

    # Draw vertical and horizontal lines at zero
    axs[i].axvline(0, color='gray', linestyle='--')
    axs[i].axhline(0, color='gray', linestyle='--')

    # Add text to each corner of the current scatter plot
    axs[i].text(0.01, 0.99, 'Below plan, above standard', 
    transform=axs[i].transAxes, 
    ha='left', va='top', color='orange', alpha=0.4)

    axs[i].text(0.99, 0.99, 'Above plan & standard', 
    transform=axs[i].transAxes, 
    ha='right', va='top', color='green', alpha=0.4)

    axs[i].text(0.01, 0.01, 'Below plan & standard', 
    transform=axs[i].transAxes, 
    ha='left', va='bottom', color='red', alpha=0.4)
    
    axs[i].text(0.99, 0.01, 'Above plan, below standard', 
    transform=axs[i].transAxes, 
    ha='right', va='bottom', color='orange', alpha=0.4)                                                        

# Layout and show charts
plt.tight_layout()
plt.show()
