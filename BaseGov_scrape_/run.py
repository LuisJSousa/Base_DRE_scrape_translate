# -*- coding: utf-8 -*-

import argparse
import json
from utils.pdfparse import parse_folder,pretty_print,parse_file
from utils.base import ScrapeBase
from pathlib import Path

if __name__ == "__main__":    
    parser = argparse.ArgumentParser(description='path with PDF to process:', formatter_class=argparse.RawDescriptionHelpFormatter,epilog="""Modo de utilização:
1. Parse all PDFs in folder:
python run.py -d "C:\path\...\pdfsbase_gov"

2. Parse one PDF:
python run.py -f "C:\path\...\pdfsbase_gov\FICHEIRO.pdf"

3. Scrape base.gov and parse all gathered PDFs collected
python run.py -d "C:\path\...\pdfsbase_gov" -s
""")
    parser.add_argument('-s', '--scrape', action='store_true', help="Collect new data from base.gov?")
    parser.add_argument('-d', '--pdf_folder', type = str, default = "", help="Path of file with PDFs to process")
    parser.add_argument('-f', '--pdf_file', type = str, default = "", help="PDF file to process")

    args = parser.parse_args()
    pdf_folder = args.pdf_folder   
    pdf_file = args.pdf_file
    scrape = args.scrape
    
    if scrape:
        assert Path(pdf_folder).exists() and Path(pdf_folder).is_dir()
        if not pdf_file:
            print("Option -f ignored!")
        print("Scraping data to: {}".format(pdf_folder))
        ScrapeBase(pdf_folder)
    else:
        if not pdf_folder == "":
            a=parse_folder(pdf_folder)
        else:
            print(pdf_file)
            a=parse_file(pdf_file)
    
        print(pretty_print(a))    
        sep="*"*25
        print("{}\n{} files processed\n{}".format(sep,len(a),sep))
        with open('data_pdfs.json', 'w') as f:
            json.dump(a, f)