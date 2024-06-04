# ========================================================================================
# ! /usr/bin/env python
# Filename: check_pdf_scan_or_text.py

# Description: Check if  file is a PDF or scan based file

# Usage: python check_pdf_scan_or_text.py <PDF File> <output_filename.txt> <stream/lattice>
# Example: python check_pdf_scan_or_text.py r1.pdf

# Use Cases:
#   => Input: PDF file (banks statements)
#   => output: A TSV file with base extract from documents also stating the type of document
# ==========================================================================================

#pip instal tabula-py
import os
import glob
import shutil
import subprocess as sp
import tabula
import time
import platform

from PyPDF2 import PdfFileReader
from utils.logger_settings import *
from utils import tools

# Local RUn should always be false in  Production
#LOCAL_RUN = False
LOCAL_RUN = True
FILE_ENCRYPTED = False
FILE_PASSWORD_PROTECTED = False
PDF_FONT = 3

def get_pypdf_object(local_filename):
    """
    Get the Page count of a PDF file
    :param local_filename:
    :return:
    """
    try:
        pdf = PdfFileReader(open(local_filename, 'rb'), strict=False)
        return pdf
    except Exception as error:
        error_msg = "Unable to read PDF object due to `{}`:".format(error)
        logger.error(error_msg)

def convert_pdf_into_text(pdf_object,
                          local_filename,
                          output_filename,
                          output_format,
                          encoding,
                          type_file=None,
                          pages=None):
    """
    Converts PDF into plain Text
    :param fname:
    :return:
    """
    logger.info("Checking the PDF: `{}` if it's Text based or Scan based PDF".format(local_filename))
    # Delimiters are not known, Converting it to TSV format
    try:
        if type_file:
            tabula.convert_into(local_filename,
                                output_filename,
                                output_format=output_format,
                                pages=pages,
                                encoding=encoding,
                                type_file=True)
            return output_filename, None
        else:
            pdf_object = get_pypdf_object(local_filename)
            if pdf_object.isEncrypted:
                pdf_object.decrypt('')
            logger.info("PDF Object is {}".format(pdf_object.documentInfo))
            os_type = platform.system()
            # check out the fonts in the PDF
            if os_type == 'Linux':
                pdffonts_command = 'pdffonts "{}" | wc -l'.format(local_filename)
            if os_type == 'Windows':
                pdffonts_command = 'pdffonts "{}" | find \{} \{} ""'.format(local_filename, 'c', 'v')

            cmd = sp.Popen(pdffonts_command, shell=True, stdout=sp.PIPE)
            output, error = cmd.communicate()
            if output:
                output = eval(output.strip())
                logger.info(" `{}` fonts have been detected for the PDF: {}".format(output, local_filename))
                # Check if the pdfonts returns any fonts greater than 2, 1 will be header, 1 will be line separator, and rest below will be font-data
                if output < PDF_FONT:
                    logger.info("The PDF: `{}` detected only `{}` fonts using pdffonts, which classifies into Scan PDF".format(local_filename, output))
                    open(output_filename, 'w').close()
                    return pdf_object.documentInfo, output
            try:
                if pdf_object.isEncrypted:
                    # If encrypted then run conversion without lattice
                    tabula.convert_into(local_filename,
                                        output_filename,
                                        output_format=output_format,
                                        pages=pages,
                                        encoding=encoding)

                if pdf_object.documentInfo:
                    # Extract the metadata of the PDF: Creator, Producer, Title
                    pdf_creator_type = pdf_object.documentInfo.get('/Creator',
                                                                   'Others').strip().lower()
                    pdf_producer_type = pdf_object.documentInfo.get('/Producer',
                                                                    'Others').strip().lower()
                    pdf_title_type = pdf_object.documentInfo.get('/Title',
                                                                 'Others').strip().lower()
                    pdf_encryption = pdf_object.isEncrypted

                    # Check if Scanned PDF got some fonts due when creator is of:  ('Kodak', canon)
                    if pdf_creator_type.strip().lower() in ('canon', 'kodak', 'smart touch', 'xerox', 'greypad ccm platform', 'jasperreports (fullstatementrpt)'):
                        logger.info("The PDF: `{}` has been detected as a `Scan based PDF` and will be converted to a text file using OCR technology".format(local_filename))
                        open(output_filename, 'w').close()

                    # Check if Scanned PDF got some fonts due when producer is of: ('canon', 'kodak', 'smart touch', 'xerox')
                    elif pdf_producer_type.strip().lower() in ('canon', 'kodak', 'smart touch', 'xerox'):
                        logger.info("The PDF: `{}` has been detected as a `Scan based PDF` and will be converted to a text file using OCR technology".format(local_filename))
                        open(output_filename, 'w').close()

                    elif 'pdfium' in pdf_creator_type and 'pdfium' in pdf_producer_type.lower():
                        # if both creator and producer are  both pdfium type
                        #logger.info("The PDF: `{}` has been detected as a `Scan based PDF` and will be converted to a text file using OCR technology".format(local_filename))
                        #open(output_filename, 'w').close()

                        #Run conversion with stream=True
                        tabula.convert_into(local_filename, output_filename,
                                            output_format=output_format,
                                            pages=pages,
                                            encoding=encoding,
                                            stream=True)

                    elif 'mergedfile' in pdf_title_type and 'pdf-tools' in pdf_producer_type.lower():
                        # Run conversion with lattice= True
                        tabula.convert_into(local_filename, output_filename,
                                            output_format=output_format,
                                            pages=pages,
                                            encoding=encoding,
                                            lattice=True)

                    elif 'others' in pdf_creator_type and 'itext 2.1' in pdf_producer_type.lower():
                        # Run conversion with no lattice param
                        tabula.convert_into(local_filename, output_filename,
                                            output_format=output_format,
                                            pages=pages,
                                            encoding=encoding)
                    elif 'others' in pdf_creator_type and 'lowgie' in pdf_producer_type.lower():
                        # Run conversion with no lattice param
                        tabula.convert_into(local_filename, output_filename,
                                            output_format=output_format,
                                            pages=pages,
                                            encoding=encoding,
                                            lattice=True)

                    elif 'others' in pdf_creator_type and 'itext 2.1' in pdf_producer_type.lower():
                        # Run conversion with no lattice param
                        tabula.convert_into(local_filename, output_filename,
                                            output_format=output_format,
                                            pages=pages,
                                            encoding=encoding)

                    else:
		        # Run conversion with no lattice param
                        tabula.convert_into(local_filename, output_filename,
                                            output_format=output_format,
                                            pages=pages,
                                            encoding=encoding)

                elif not pdf_object.documentInfo:
                    # if no documentinfo retrieved then stream = True
                    tabula.convert_into(local_filename, output_filename,
                                        output_format=output_format,
                                        pages=pages,
                                        encoding=encoding,
                                        stream=True)
                else:
                    # Run conversion with no lattice param
                    logger.warning("The PDF: `{}`  will be converted to text using OCR technology".format(local_filename))
                    open(output_filename, 'w').close()
                    #tabula.convert_into(local_filename, output_filename,
                    #                    output_format=output_format,
                    #                    pages=pages,
                    #                    encoding=encoding)

                # return output, pdf_object.documentInfo
            except Exception as pdferror:
                logger.warning("The PDF: `{}` has detected some errors: `{}` and will be converted to a text file using OCR technology".format(local_filename, pdferror))
                open(output_filename, 'w').close()
            return pdf_object.documentInfo,output

    except IOError:
        logger.warning("The PDF: `{}`  not found, will be converted to text using OCR technology".format(local_filename))
        open(output_filename, 'w').close()

    except Exception as error:
        open(output_filename, 'w').close()
        error_msg = "The PDF: `{}` has encountered some errors: {}  and will be converted to text using OCR technology".format(local_filename, error)
        logger.warning(error_msg)

def concatenate_files(final_output_filename, file_extension):
    """
    Concatenate all temporary output files into a single PDF file
    :param final_output_filename:
    :param file_extension:
    :return:
    """
    logger.info("Concatenation of files for `{}` ".format(file_extension))
    try:
        with open(final_output_filename, 'wb') as outfile:
            for filename in glob.glob(file_extension):
                if filename == final_output_filename:
                    # don't want to copy the output into the output
                    continue
                with open(filename, 'rb') as readfile:
                    shutil.copyfileobj(readfile, outfile)
    except Exception as error:
        error_msg = "Unable to concatenate the file: {}".format(final_output_filename)
        logger.error(error_msg)

def check_scan_pdf(local_filename, output_filename, type_file):
    output_format = 'tsv'
    encoding = 'utf-8'
    max_page_buffer = 200
    try:
        # Get the Total page count of PDF
        pdf_obj = get_pypdf_object(local_filename)

        if pdf_obj.isEncrypted:
            pdf_obj.decrypt('')
            global FILE_ENCRYPTED
            FILE_ENCRYPTED = True
        try:
            try:
                page_count = pdf_obj.getNumPages()
            except Exception as some_error:
                page_count = pdf_obj.getNumPages()
                print(some_error)
        except Exception as error:
            FILE_PASSWORD_PROTECTED = True
            logger.critical("PDF File: {} is encrypted/Password Protected.".format(local_filename))
            open(output_filename, 'w').close()
            return output_filename, "Password_Protected_PDF", None, None

        # Split big files greater than 200 pages
        if page_count >= max_page_buffer:
            # Get the number of pages to iterate
            no_of_pages_iterate, left_out_pages = divmod(page_count, max_page_buffer)
            # If Left out pages are left then add one more iteration to CSV
            logger.info("The PDF `{}` has `{}` pages and has been split into `{}` iterations.".format(local_filename, page_count, no_of_pages_iterate))
            if left_out_pages:
                no_of_pages_iterate += 1
            for page in range(0, no_of_pages_iterate):
                logger.info("PDF Iteration page: `{}`".format(page))
                if page == 0:
                    page_start = 1
                    page_end = max_page_buffer
                else:
                    page_start = (page * max_page_buffer) + 1
                    page_end = (page_start + max_page_buffer) - 1
                pages = "{}-{}".format(page_start, page_end)
                paginated_output_filename = 'output_' + local_filename.split('.')[0] + \
                                   '_' + \
                                  str(page) +'.txt'
                output, filen = convert_pdf_into_text(pdf_obj,
                                      local_filename,
                                      paginated_output_filename,
                                      output_format,
                                      encoding, type_file, pages)

            # Concatenate all output files into a single output file
            concatenate_files(output_filename, file_extension="'*.txt'")

        else:
            # If the count of the pages is less than max_buffer_page=200,
            # then execute all pages of PDF into once
            output, filen = convert_pdf_into_text(pdf_obj,
                                  local_filename,
                                  output_filename,
                                  output_format,
                                  encoding,
                                  type_file,
                                  pages="all")

        # if no file is found create an empty file
        if not os.path.isfile(output_filename):
            logger.info("The PDF: `{}` has been detected as a `Scan based PDF` and will be converted to a text file using OCR technology".format(local_filename))
            open(output_filename, 'w').close()
            return output_filename, "Error", output, filen

        # Delete all temporary output files of a particular extension
        # tools.delete_files_with_extension('.', '.txt')

        file_empty_check = tools.check_file_is_empty(output_filename)
        if file_empty_check:
            pdf_type = "Scanned PDF"
            logger.info("The PDF: `{}` has been detected as a `Scan based PDF` and has been converted to a text file using OCR technology".format(local_filename))
            return output_filename, "Scanned_PDF", output, filen
        else:
            pdf_type = "Text based PDF"
            logger.info("The PDF: `{}` has been detected as a normal `Text based PDF` and has been converted to a text file using Tabula".format(local_filename))
            if FILE_ENCRYPTED:
                return output_filename, "Bank_Generated_Encrypted_PDF", output, filen
            else:
                return output_filename, "Bank_Generated_PDF", output, filen

    except Exception as error:
        logger.error(error)
        open(output_filename, 'w').close()
        return output_filename, "Error", "Error", "Error"

def main():
    if LOCAL_RUN:
        if len(sys.argv) == 3:
            local_filename = sys.argv[1]
            output_filename = sys.argv[2]
            type_file = None
        elif len(sys.argv) == 4:
            local_filename = sys.argv[1]
            output_filename = sys.argv[2]
            type_file = sys.argv[3] #stream or lattice
        output_filename, data_type, metadata, font = check_scan_pdf(local_filename, output_filename, type_file=type_file)
        logger.info("The file: {} has been detected as  `{}`".format(output_filename, data_type))

if __name__ == '__main__':
    main()
