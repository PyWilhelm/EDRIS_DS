#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xlsxwriter


def html_table_to_excel(table):
    """ html_table_to_excel(table): Takes an HTML table of data and formats it so that it can be inserted into an Excel Spreadsheet.
    """

    data = {}

    table = table[table.index('<tr>'):table.index('</table>')]

    rows = table.strip('\n').split('</tr>')[:-1]
    for (x, row) in enumerate(rows):
        if row.strip('\n').find('<th>') >= 0:
            columns = row.strip('\n').split('</th>')[:-1]
        else:
            columns = row.strip('\n').split('</td>')[:-1]
        data[x] = {}
        for (y, col) in enumerate(columns):
            data[x][y] = col.replace('<tr>', '').replace('<td>', '').replace('<th>', '').strip()

    return data


def export_to_xls(data, title='Sheet1', filename='export.xls'):
    """ export_to_xls(data, title, filename): Exports data to an Excel Spreadsheet.
    Data should be a dictionary with rows as keys; the values of which should be a dictionary with columns as keys; the value should be the value at the x, y coordinate.
    """

    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet(title)
    worksheet.set_column('A:C', 40)

    format = workbook.add_format()
    format.set_font_size(13)
    format.set_text_wrap()

    for x in sorted(data.iterkeys()):
        for y in sorted(data[x].iterkeys()):
            try:
                if float(data[x][y]).is_integer():
                    worksheet.write(x, y, int(float(data[x][y])), format)
                else:
                    worksheet.write(x, y, float(data[x][y]), format)
            except ValueError:
                worksheet.write(x, y, data[x][y], format)

    workbook.close()

    return

if __name__ == '__main__':

    string = '''<table border="1">
      <tr>
        <th>Berlin</th>
        <th>Hamburg</th>
        <th>M&uuml;nchen</th>
      </tr>
      <tr>
        <td>Milj&oumlaaaaaaaaaaaaaaaaaaaaaa;h</td>
        <td>Kiez</td>
        <td>Bierdampf</td>
      </tr>
      <tr>
        <td>Buletten</td>
        <td>Frikadellen</td>
        <td>Fleischpflanzerl</td>
      </tr>
    </table>
    '''

    export_to_xls(html_table_to_excel(string))
