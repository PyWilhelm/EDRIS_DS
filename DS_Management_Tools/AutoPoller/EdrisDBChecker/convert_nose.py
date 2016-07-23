import re

import xlwt
import xml.etree.ElementTree as ETree


get_message = lambda x : x.getchildren()[0].attrib['message']
get_path = lambda x : get_filepath(get_message(x))
get_name = lambda x : x.attrib['name']
def convert_nose(nose_filename='nosetests.xml', xls_name='nose.xls'):
    et = ETree.ElementTree(file=nose_filename)
    root = et.getroot()
    tc_err = [t for t in root.findall('testcase') if t.getchildren() != []]

    header = [['Path (click the hyperlink to navigate', 'error types', 'warning types',]]
    content =  [[get_path(tc), parse_message(tc)['error_msg'], parse_message(tc)['warning_msg'] ] for tc in tc_err]
    listdata = header + content
   
    book = xlwt.Workbook(encoding="utf-8")
    sheet = book.add_sheet("Sheet 1")

    for i, l in enumerate(listdata):
        for j, col in enumerate(l):
            sheet.write(i, j, col)

    book.save(xls_name)

def parse_message(node):
    msg = get_message(node)

    if u'Error' in msg.split('\n')[2]:
        error_msg = msg.split('\n')[4]
        warning_msg = msg.split('\n')[8]
    else:
        error_msg = msg.split('\n')[8]
        warning_msg = msg.split('\n')[4]

    return dict(error_msg=error_msg, warning_msg=warning_msg)
        
def get_filepath(message):
    filepath = message.split('\n')[3]
    escaped_path = re.sub(r'\\', r'/', re.sub('file:///', '', filepath))
    return xlwt.Formula(u'HYPERLINK("{0}";"{0}")'.format(escaped_path))

if __name__=='__main__':
    convert_nose()
