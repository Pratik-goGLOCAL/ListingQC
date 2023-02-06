import pandas as pd
from excel_checks import QC_check1

data = pd.read_csv('DataStore/ScrapedData_pg_v1.csv')
data.fillna('NULL',inplace=True)
res = QC_check1(data)
