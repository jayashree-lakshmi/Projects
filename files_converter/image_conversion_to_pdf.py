#!/usr/bin/env python3
#filename:image_conversion_to_pdf.py
#Description: Converting jpg,jpeg,bmp,png, tif,tiff files to pdf
#Python3
#Usage: Used as a module to convert images to pdf.If required pass the parameter 
#such as start page and end page details in a function to convert the required pages.
#python image_conversion_to_pdf.py filename

import logging as logger
import os
import sys
from PIL import Image,ImageSequence, ImageFile

def converting_image_pdf(filename,
                         new_filename=None,
                         start_page=None,
                         end_page=None):
    '''
    Converting jpg,jpeg,bmp,png files to pdf as well as  tiff file to pdf
    :param filename:
    :return:
    '''
    try:
        file_extension = filename.split(".")[1].lower()
        if not new_filename:
            new_filename = filename.split('.')[0] + ".pdf"
        if file_extension in ('jpg', 'jpeg', 'bmp', 'png'):
            logger.info("converting image in to pdf ")
            im = Image.open(filename)
            if im.mode == "RGBA":
                im = im.convert("RGB")
            if not os.path.exists(new_filename):
                im.save(new_filename, "pdf", resolution=100.0)
        if file_extension in ('tif', 'tiff'):
            try:
                image = Image.open(filename)
                pages = []
                page_iterators = list(ImageSequence.Iterator(image))
                if not start_page or not end_page:
                    start_page = 1
                    end_page = len(page_iterators)
                page_iterators = []
                for index, page in enumerate(ImageSequence.Iterator(image)):#page_iterators:
                    if index == end_page:
                        break
                    pages.append(page.convert("L"))

                pages[start_page-1].save(new_filename, save_all=True, append_images=pages[start_page:end_page])
                pages = []
            except OSError as ose:
                logger.warning(ose)
                tiff_to_pdf(filename, new_filename)

        return new_filename
    except Exception as error:
        logger.error(error)

def tiff_to_pdf(filename, new_filename):
    """
   :param filename: original tiff filename to be converted
   :param new_filename: converted filename to be saved with
    """

    try:
        file_extension = filename.split(".")[1].lower()

        if file_extension in ('tif','tiff'):
            logging.info("Converting... .... TiFF file to PDF")

            cmd = [
                "tiff2pdf", "{}".format(filename), "-o", "{}".format(new_filename), "-p", "A4"
            ]

            result = sp.run(cmd)

            if result.returncode == 0:
                logger.info(
                    "Converted {} to {} successfully".format(filename, new_filename))
            elif result.returncode == 2:
                logger.info(
                    "PDF could not be genrated from {}".format(filename))
    except Exception as error:
        logger.info(
            "Exception occured {} while converting tiff to pdf")


filename=sys.argv[1]
converting_image_pdf(filename,
                         new_filename=None,
                         start_page=None,
                         end_page=None)