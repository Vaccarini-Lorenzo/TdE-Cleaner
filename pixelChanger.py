from PIL import Image
import fitz
import os
import multiprocessing
import time

def joinPDF():
    os.chdir("outputDir")
    print("joining PDFs...")
    finalPDF = fitz.open()
    print(os.listdir())
    orderedPDFList = sorted(os.listdir(), key=str.lower)
    print(orderedPDFList)
    for pdf in orderedPDFList:
        with fitz.open(pdf) as mfile:
            finalPDF.insert_pdf(mfile)
            os.remove(pdf)
    finalPDF.save("TdE.pdf")

def singleProcess(numDone, pdfName, offset, blockSize, remainder):
    pageProcessing(pdfName, offset, blockSize, remainder)
    numDone.value += 1

def pageProcessing(pdfName, offset, blockSize, remainder):
    zoom = 3
    mat = fitz.Matrix(zoom, zoom)
    inputDoc = inputDoc = fitz.open(pdfName)
    outDoc = fitz.open()
    os.chdir("outputDir")
    r = offset + blockSize
    if(remainder != -1):
        r = offset + remainder - 1
    for pageIndex in range(offset, r):
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

    if offset < 10:
        outDoc.save("TdE0" + str(offset) + ".pdf")
    else:
        outDoc.save("TdE" + str(offset) + ".pdf")


if __name__ == '__main__':
    startTime = time.time()
    path = "."          # Change here
    pdfName = "test.pdf"   # Change here
    os.chdir(path)
    inputDoc = inputDoc = fitz.open(pdfName)
    os.mkdir("outputDir")
    numPages = inputDoc.page_count
    blockSize = numPages // 5
    remainder = numPages % 5
    manager = multiprocessing.Manager()
    numDone = manager.Value('i', 0)
    processList = []
    for i in range (0, 5):
        p = multiprocessing.Process(target = singleProcess, args = (numDone, "test.pdf", i*blockSize, blockSize, -1))
        processList.append(p)
        p.start()

    if (remainder != 0):
        p = multiprocessing.Process(target = singleProcess, args = (numDone, "test.pdf", 5*blockSize, blockSize, remainder))
        processList.append(p)
        p.start()

    numThread = 5 if remainder != 0 else 4

    while(numDone.value < numThread):
        time.sleep(1)

    joinPDF()

    for p in processList:
        p.join()

    finalTime = time.time()
    print("Total time = ", finalTime - startTime)
