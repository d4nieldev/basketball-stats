import xlwt
from xlwt import Workbook
import os
import json
import pprint


def excel_from_dict(d):
    wb = Workbook()

    p3_bmi = wb.add_sheet('3P per BMI')
    # 3P per BMI
    p3_bmi.write(0, 0, "BMI")
    p3_bmi.write(0, 1, "3P")
    for idx, (key, val) in enumerate(d["3P"]["bmis"].items()):
        p3_bmi.write(idx + 1, 0, key)
        p3_bmi.write(idx + 1, 1, val)

    p3_height = wb.add_sheet('3P per height')
    # 3P per height
    p3_bmi.write(0, 0, "Height")
    p3_bmi.write(0, 1, "3P")
    for idx, (key, val) in enumerate(d["3P"]["heights"].items()):
        p3_height.write(idx + 1, 0, key)
        p3_height.write(idx + 1, 1, val)
    
    wb.save('test.xls')

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "static/data", "averages.json")
data = json.load(open(json_url))

excel_from_dict(data)

