"""
! /usr/bin/env python3
# Filename:docx_pdfconverter.py
# Description: Converting docx file to pdf

#   Use Cases:
#
#           => Input: docx file
#
#           => Output: pdf file

# Usage: python docx_pdf.py filename.docx

"""
import logging as logger
import os
import platform
import subprocess as sp
import sys


try:
    from comtypes import client
except ImportError:
    client = None

def doc2pdf(doc, new_doc_name=None):
    """
    convert a doc/docx document to pdf format
    :param doc: path to document
    """
    doc = os.path.abspath(doc) 
    name, ext = os.path.splitext(doc)
    if not new_doc_name:
        new_doc_name = "converted_{}.pdf".format(os.path.basename(name))

    if platform.system() == 'Linux':
        new_doc_name = doc2pdf_linux(doc, new_doc_name)
        return new_doc_name
    try:
        word = client.CreateObject('Word.Application')
        worddoc = word.Documents.Open(doc)
        worddoc.SaveAs(new_doc_name, FileFormat=17)
    except Exception as error:
        logger.error(error)
    finally:
        worddoc.Close()
        word.Quit()
    return os.path.basename(new_doc_name)

def doc2pdf_linux(doc, new_doc_name):
    """
    convert a doc/docx document to pdf format (linux only, requires libreoffice)
    :param doc: path to document
    """
    try:
        cmd= 'libreoffice --convert-to pdf'.split() + [doc]
        p = sp.Popen(cmd, stderr=sp.PIPE, stdout=sp.PIPE)
        stdout, stderr = p.communicate()
        filename_pdf = "{}.pdf".format(os.path.basename(doc).split('.')[0])
        if os.path.isfile(filename_pdf):
            os.rename(filename_pdf, new_doc_name)
            return new_doc_name
        else:
            return
    except Exception as error:
        logger.error(error)

def main():
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        new_filename = doc2pdf(filename)
        logger.info("Converted filename: {}".format(new_filename))
    else:
        logger.info("Usage: python docx_pdfconverter.py <filename>")
        exit(1)

if __name__ == '__main__':
    main()