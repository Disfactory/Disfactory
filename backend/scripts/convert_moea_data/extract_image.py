#Importing the modules
import openpyxl
from openpyxl_image_loader import SheetImageLoader

#loading the Excel File and the sheet
pxl_doc = openpyxl.load_workbook('11001.xlsx')
sheet = pxl_doc['109年經勘查屬(新增)未登記工廠名單']

#calling the image_loader
image_loader = SheetImageLoader(sheet)
for name in image_loader._images.keys():
    print(name)
