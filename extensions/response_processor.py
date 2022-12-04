import gspread

gc = gspread.service_account()

sh = gc.open("Extension request: BAIM 3220 (Responses)")

print(sh.sheet1.get('A1'))