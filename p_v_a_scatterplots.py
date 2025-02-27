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

# data_plan = data_plan[data_plan["source"] == 'June24_plan']

# Filter rows
# plan_refs = data_plan["planning_ref"].isin(["E.B.35", # cancer 62d
#                                             "E.B.27", # cancer fds
#                                             "E.B.28" # diagnostics 6ww
#                                             ])
# orgs_only = (
#     data_plan["icb_code"] != data_plan["org_code"]
#     ) | (
#     data_plan["planning_ref"] == "E.B.28"
#     ) # diagnostics is at ICB level
# pc_only = data_plan["measure_type"] == "Percentage"

# data_plan = data_plan[plan_refs & orgs_only & pc_only]

# Filter columns
# data_plan = data_plan[
#     ["org_code", "dimension_name", "planning_ref", "metric_value"]
#     ]

# Create calculated field for plans and actuals, and drop old columns
data_plan['plan_value'] = data_plan['numerator'] / data_plan['denominator']
data_plan = data_plan.drop(['numerator', 'denominator'], axis=1)
data_actuals['actual_value'] = data_actuals['numerator'] / data_actuals['denominator']
data_actuals = data_actuals.drop(['numerator', 'denominator'], axis=1)


# Rename value column
# data_plan.rename(columns={'metric_value': 'plan'}, inplace=True)

# # Flip diagnostics around so it's the 95% target
# data_plan.loc[data_plan['planning_ref'] == "E.B.28", 'plan'] = 100 - data_plan['plan']

# # Bring in actuals data
# data_actuals = pd.read_csv("data/current_actuals.csv")

# Set metric standards
# standard = {
#     "E.B.35": 70, # cancer 62d
#     "E.B.27": 77, # cancer fds
#     "E.B.28": 95 # diagnostics 6ww
# }


# # Filter rows
# plan_refs = data_actuals["planning_ref"].isin(["E.B.35", # cancer 62d
#                                             "E.B.27", # cancer fds
#                                             "E.B.28" # diagnostics 6ww
#                                             ])
# # Rename diagnostics plan ref
# data_actuals = data_actuals.replace('E.B.28a', 'E.B.28')
# orgs_only = (
#     data_actuals["icb_code"] != data_actuals["org_code"]
#     ) | (
#     data_actuals["planning_ref"] == "E.B.28"
#     ) # diagnostics is at ICB level
# pc_only = data_actuals["measure_type"] == "Percentage"
# # orgs_only = data_actuals["icb_code"] != data_actuals["org_code"]
# # pc_only = data_actuals["measure_type"] == "Percentage"

# data_actuals = data_actuals[plan_refs & orgs_only & pc_only]

# # Filter columns
# data_actuals = data_actuals[
#     ["org_code", "dimension_name", "planning_ref", "metric_value"]
#     ]

# # Rename value column
# data_actuals.rename(columns={'metric_value': 'actual'}, inplace=True)

# data_actuals.loc[data_actuals['planning_ref'] == "E.B.28", 'actual'] = 100 - data_actuals['actual']

# Merge data_plan and data_actuals
data = pd.merge(data_plan, data_actuals, 
on=["org_code", "dimension_name", "planning_ref"])

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

# Rename planning_refs to friendly names
# data["planning_ref"].replace(
#     {'E.B.35':
#     "Cancer 62-day pathways. Total patients seen, and of which those seen " +
#     "within 62 days", 
#     'E.B.27': 
#     'Cancer 28 day waits (faster diagnosis standard)', 
#     'E.B.28':
#     "Diagnostics 6ww %"},
#     inplace=True
#     )

# Remove duplicates which exist for some reason
data = data.drop_duplicates()

# Reset index to ensure proper indexing
data.reset_index(drop=True, inplace=True)

# Create chart outputs using fig, ax, split by planning_ref
unique_refs = data["planning_ref"].unique()

# Create chart template area
fig, axs = plt.subplots(len(unique_refs), 1, figsize=(10, 18), sharey=True)

# Ensure axs is always iterable
if len(unique_refs) == 1:
    axs = [axs]

# Create charts (one per metric)
for i, ref in enumerate(unique_refs):
    subset_data = data[data["planning_ref"] == ref]
    axs[i].scatter(subset_data["plan_var"], subset_data["standard_var"], 
    c="blue")
    axs[i].set_xlabel("Variance from plan (percentage points)")
    axs[i].set_ylabel("Variance from target (percentage points)")
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
