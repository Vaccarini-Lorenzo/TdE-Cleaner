from PIL import Image
import fitz
import os
import time

path = "."          # Change here
pdfFile = "test.pdf"   # Change here
os.chdir(path)
inputDoc = fitz.open(pdfFile)
outDoc = fitz.open()
os.mkdir("outputDir")
os.chdir("outputDir")

zoom = 3
mat = fitz.Matrix(zoom, zoom)

initial = time.time()

for pageIndex in range(0, inputDoc.page_count):
    page = inputDoc.load_page(pageIndex)
    pix = page.get_pixmap(matrix = mat)
    outputName = "page" + str(pageIndex) + ".png"
    pix.save(outputName)
    picture = Image.open(outputName)
    width, height = picture.size

    # Overwriting blue pixels
    for w in range(0, width):
        for h in range(0, height):
            r, g, b = picture.getpixel((w, h))
            R = r / 255
            G = g / 255
            B = b / 255
            maxV = max(R, G, B)
            minV = min(R, G, B)
            lightness = (maxV + minV) / 2
            delta = maxV - minV
            temp = 1 - abs(2 * lightness -1)
            saturation = 0
            if(temp != 0):
                saturation = delta / temp
            if (saturation > 0.08):
                picture.putpixel((w, h), (254, 254, 254))

    picture.save(outputName)


    # Deleting tmp img and appending to final PDF
    img = fitz.open(outputName)
    rect = img[0].rect
    pdfbytes = img.convert_to_pdf()
    img.close()
    imgPDF = fitz.open("pdf", pdfbytes)
    page = outDoc.new_page(width = rect.width,
                       height = rect.height)
    page.show_pdf_page(rect, imgPDF, 0)
    os.remove(outputName)

outDoc.save("TdE.pdf")

final = time.time()

print(final - initial)
