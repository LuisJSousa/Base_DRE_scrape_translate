# -*- coding: utf-8 -*-
"""
Parse base.gov PDF docs
"""

import pdfplumber
from pathlib import Path
import argparse

def append_fieldTEXT(txtdic,line):
    if not txtdic.get("fieldTEXT"):
        txtdic["fieldTEXT"]=""
    if "Diário da República" in line and "Anúncio" in line and "Página" in line:
        line=line.split("Diário da República")[0]
    txtdic["fieldTEXT"]+=line+"\n"
    return txtdic

def append_FT(FT,txtdic):
    if txtdic!={} and txtdic.get("fieldID"):
        FT.append(txtdic)
    return FT    

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def getText(fn):    
    pdftxt = ""
    with pdfplumber.open(fn) as pdf:
        for page in pdf.pages:
            pdftxt += page.extract_text()    
        return {"file":fn,"text":pdftxt}

def parse_pdf_list(pdfs):
    # extract text
    pdfstxt=[]
    for fn in pdfs:
        pdfstxt.append(getText(fn))
        
    AllPDFs = []        
    # split in fields
    maxcampos = 20

    for txtd in pdfstxt:
        txt=txtd["text"]
        fn=txtd["file"]
        FT = []
        txtdic={}
        curi = 0
        lines = txt.split("\n")
        for line in lines:
            if " - " in line:
                # Char before " - " should be numeric.
                els = line.split(" - ")
                if len(els) >= 2 and is_number(els[0]):
                    hid = float(els[0])
                    
                    if hid == int(hid):
                        hid=int(hid)
                    if hid-curi<=maxcampos:
                        #new fields
                        #store previous field
                        FT=append_FT(FT, txtdic)
                        #start new field
                        txtdic={}
                        txtdic["fieldID"] = str(hid)
                        t = els[1]
                        
                        txtdic["fieldDESC"] = t.split("Diário da República")[0]
                        curi=hid
                    else:
                        #row starts with a number but that number is larger than expected (ie increment exceeds maxfields) 
                        #do not create a new field
                        #Append text line to existing field
                        txtdic = append_fieldTEXT(txtdic, line)
                else:
                   #row has " - " but no new field structure. ID is not numeric;
                    #add text line to existing field
                    txtdic = append_fieldTEXT(txtdic, line)
            else:
                #Line does not have " - "
                #add text line to existing field
                txtdic = append_fieldTEXT(txtdic, line)
        
        FT=append_FT(FT, txtdic)
        AllPDFs.append({"file":str(fn),"data":FT})
    return AllPDFs


def parse_file(pdf_file):
    pdfs = [pdf_file]
    pdf_file = Path(pdf_file)
    assert pdf_file.exists() and pdf_file.is_file()
    return parse_pdf_list(pdfs)
    
def parse_folder(pdf_folder):
    pdf_folder = Path(pdf_folder)
    assert pdf_folder.exists() and pdf_folder.is_dir()
    pdfs = list(pdf_folder.glob('*.pdf'))
    return parse_pdf_list(pdfs)
                
def pretty_print(d):
    import json
    return json.dumps(d,sort_keys=False, indent=4,ensure_ascii=False)

if __name__ == "__main__":    
    parser = argparse.ArgumentParser(description='Introduce PDF path to process:', formatter_class=argparse.RawDescriptionHelpFormatter,epilog="""Modo de utilização:
python pdfparse.py -f "C:\path\...\pdfsbase_gov" """)
    parser.add_argument('-f', '--pdf_folder', type = str, default = r"C:pdfdump", help="Path PDF to processs")
    args = parser.parse_args()
    pdf_folder = args.pdf_folder
    
    # pdf_folder = Path("C:pdfsbase_gov")
    a=parse_folder(pdf_folder)
    
    
    print(pretty_print(a))
    