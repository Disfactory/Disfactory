import zipfile
XLSname = "./11001.xlsx"

EmbeddedFiles = zipfile.ZipFile(XLSname).namelist()
ImageFiles = [F for F in EmbeddedFiles if F.count('.jpg') or F.count('.jpeg')]

for Image in ImageFiles:
    zipfile.ZipFile(XLSname).extract(Image)
