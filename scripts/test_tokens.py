import requests

r = requests.get(
    "https://graph.facebook.com/v23.0/me/permissions",
    params={"access_token": """EAAT6uaTZA1wIBRofV0xZAexN4ATdWp8eXOZCMurQw3uO0XBGsKiualMr7qiXFVCZASWdcBIk9g7wrhi1QexCZAvCxPZBPBKXfrcUC9MG54XS8R312tiZA6yPjxlTcfFUvcVwbqZAXMksAvZB6uVv0wfgX1NYR1TYff5DIeeiv1WIyekE1isxuHzZCpSUKT6W28CVJX3lc8ka1pWGnEMVQSyNaOkAqz4CAFE7eAMiF49U3siSOa3njrma91vZBD8BxiEHKV5wHpGdlYx634Wc2yN"""}
)

print(r.json())