#!/usr/bin/env python
# -*- coding: utf-8 -*-

from prettytable import from_html
import os
from conf import __conf__

import xhtml2pdf.pisa as pisa


def save_as_pdf(tid, tables_string, compname, filename, revision):
    pts = from_html(tables_string)
    dirpath = os.path.join(__conf__['outputPath'], 'tmp_report', 'report' + tid)
    if os.path.exists(dirpath) == False:
        os.makedirs(dirpath)

    print revision, compname, tables_string
    result_info = '<div STYLE="word-wrap: break-word">Subversion Revision Number: ' \
        + revision + '<br/><br/>' + compname + '<br/><br/></ div>' + tables_string
    pisa.CreatePDF(result_info, file(os.path.join(dirpath, filename), 'wb'))


def svn_commit(tid, html, compname, localpath, remotepath, commit, revision):
    try:
        # os.system('svn cleanup --username qxg2705 --password natsun01')
        save_as_pdf(tid, html, compname, localpath, revision)
        '''        os.system('svn delete -m \"' + 
          commit +'\" ' + 
          'https://lpintrae.muc:4756/svn/edris/' + 
          remotepath + 
          ' --username qxg2705 --password mu1m1n0k')
        os.system('svn import -m \"' + 
                  commit +'\" ' + 
                  localpath + 
                  ' https://lpintrae.muc:4756/svn/edris/' + 
                  remotepath + 
                  ' --username qxg2705 --password mu1m1n0k')'''
        return True
    except:
        import traceback
        print traceback.format_exc()
        return False

if __name__ == '__main__':
    save_as_pdf(html_string, r'C:\edris\EDRIS_Tools\automated_testing_EDRIS\EDRIS_Management\result.txt')
    svn_commit(r'C:\edris\EDRIS_Tools\automated_testing_EDRIS\EDRIS_Management\result.txt',
               'EDRIS_Tools/automated_testing_EDRIS/result.txt', 'li: import command test')
