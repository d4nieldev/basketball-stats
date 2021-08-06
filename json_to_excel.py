import xlwt
from xlwt import Workbook
import os
import json
import pprint


def excel_from_dict(d):
    """'Write all relevant data to excel file'

    Args:
        d (dict): a dict that constructed from averages.py
    """
    wb = Workbook()

    idx = 0
    p3_bmi = wb.add_sheet('3P per BMI')
    # 3P per BMI
    p3_bmi.write(0, 0, "BMI")
    p3_bmi.write(0, 1, "3P")
    for key, val in d["3P"]["bmis"].items():
        if val != 0:
            # no zeros
            p3_bmi.write(idx + 1, 0, key)
            p3_bmi.write(idx + 1, 1, val)
            idx += 1
    
    idx = 0
    p3_height = wb.add_sheet('3P per height')
    # 3P per height
    p3_height.write(0, 0, "Height")
    p3_height.write(0, 1, "3P")
    for key, val in d["3P"]["heights"].items():
        if val != 0:
            # no zeros
            p3_height.write(idx + 1, 0, key)
            p3_height.write(idx + 1, 1, val)
            idx += 1

    idx = 0
    p3pc_bmi = wb.add_sheet('3P% per BMI')
    # 3P% per BMI
    p3pc_bmi.write(0, 0, "BMI")
    p3pc_bmi.write(0, 1, "3P%")
    for key, val in d["3P%"]["bmis"].items():
        if val != 0:
            # no zeros
            p3pc_bmi.write(idx + 1, 0, key)
            p3pc_bmi.write(idx + 1, 1, val)
            idx += 1

    idx = 0
    p3pc_height = wb.add_sheet('3P% per height')
    # 3P% per height
    p3pc_height.write(0, 0, "Height")
    p3pc_height.write(0, 1, "3P%")
    for key, val in d["3P%"]["heights"].items():
        if val != 0:
            # no zeros
            p3pc_height.write(idx + 1, 0, key)
            p3pc_height.write(idx + 1, 1, val)
            idx += 1

    idx = 0
    drb_height = wb.add_sheet('DRB per height')
    # DRB per height
    drb_height.write(0, 0, "Height")
    drb_height.write(0, 1, "DRB")
    for key, val in d["DRB"]["heights"].items():
        if val != 0:
            # no zeros
            drb_height.write(idx + 1, 0, key)
            drb_height.write(idx + 1, 1, val)
            idx += 1
    
    idx = 0
    orb_height = wb.add_sheet('ORB per height')
    # ORB per height
    orb_height.write(0, 0, "Height")
    orb_height.write(0, 1, "ORB")
    for key, val in d["ORB"]["heights"].items():
        if val != 0:
            # no zeros
            orb_height.write(idx + 1, 0, key)
            orb_height.write(idx + 1, 1, val)
            idx += 1
    
    wb.save('averages.xls')

# get the averages
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "static/data", "averages.json")
data = json.load(open(json_url))

excel_from_dict(data)

