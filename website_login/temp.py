import xlwings as xw
wb = xw.Book(r'C:\Users\610161178\Downloads\current_pec_review.xlsm')
sh = wb.sheets['Review']
sh['B2'].value = "R240N"