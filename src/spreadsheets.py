from xlsxwriter import Workbook


def set_headers(ws: Workbook.worksheet_class, headers):
    for col, header in enumerate(headers):
        ws.write(0, col, header)


def add_measurement(ws: Workbook.worksheet_class, values: tuple, row: int):
    for col, value in enumerate(values):
        ws.write(row + 1, col, value)
