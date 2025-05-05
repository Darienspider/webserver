from PyPDF2 import PdfFileReader, PdfReader, PdfWriter  # Updated for PyPDF2 v3.0.0+
pdf_file =  open('0- DnD Basic Rules 2018.pdf', 'rb')
reader = PdfReader(pdf_file)

page1 = reader.pages[0]
print(page1.extract_text())