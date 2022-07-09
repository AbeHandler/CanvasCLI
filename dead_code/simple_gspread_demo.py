import gspread

### https://gspread.readthedocs.io/en/latest/oauth2.html#oauth-client-id
gc = gspread.oauth()

# This needs to exist already 
sh = gc.open("Quiz correction (Responses)")

print(sh)