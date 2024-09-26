import requests

class NHSTrusts:
    def __init__(self):
        self.url = "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations"
        self.params = {
            "PrimaryRoleId": "RO197",  # Role ID for NHS Trusts
            "Limit": 100  # Number of results to return
        }
        self.trusts = []

    def fetch_trusts(self):
        response = requests.get(self.url, params=self.params)
        if response.status_code == 200:
            data = response.json()
            self.trusts = [
                {
                    "short_name": org.get('OrgName', 'N/A'),
                    "ods_code": org.get('OrgId', 'N/A')
                }
                for org in data['Organisations']
            ]
        else:
            print(f"Failed to retrieve data: {response.status_code}")

    def get_trusts(self):
        if not self.trusts:
            self.fetch_trusts()
        return self.trusts

# Example usage
if __name__ == "__main__":
    nhs_trusts = NHSTrusts()
    trusts = nhs_trusts.get_trusts()
    for trust in trusts:
        print(f"Short Name: {trust['short_name']}, ODS Code: {trust['ods_code']}")
