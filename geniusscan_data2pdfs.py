import os
import re
import sqlite3
import sys
from collections import defaultdict

import numpy as np

import cv2
import img2pdf


# Adrian Rosebrock, 4 Point OpenCV getPerspective Transform Example,
# https://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/
# accessed on 28 July 2019
def four_point_transform(image, rect):
    # obtain a consistent order of the points and unpack them
    # individually
    tl, tr, br, bl = rect

    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    # return the warped image
    return warped


def warp_file_from_quadstring(path, quadstring):
    corners = quadstring.split("/")
    corners = list(zip(corners[0::2], corners[1::2]))
    corners[2], corners[3] = corners[3], corners[2]
    image = cv2.imread(path)
    height, width, _ = image.shape
    rect = np.float32(corners) * np.float32([width, height])
    return four_point_transform(image, rect)


def image_files_to_pdf(type, title, path_list):
    doc = type + "_" + re.sub(r'[/\\:*?"<>|]', "_", title) + ".pdf"
    print("Writing", doc)
    with open(doc, "wb") as pdf:
        pdf.write(img2pdf.convert(path_list))
    print("done")


def main(db_path="database.db", image_dir=""):
    if not os.path.exists(db_path) or not os.path.isfile(db_path):
        print("Database file not found: " + db_path)
        return
    if not os.path.exists(image_dir) or not os.path.isdir(image_dir):
        print("Image directory not found: " + image_dir)
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    original_docs = defaultdict(list)
    modified_docs = defaultdict(list)
    quads = {}

    for row in c.execute(
        "SELECT document.title, im1.uuid original_uuid, im2.uuid warped_uuid, "
        "page.originalImage_id, page.warpedImage_id, page.quadrangle2 FROM "
        "page JOIN images im2 ON im2.id == page.warpedImage_id JOIN images im1"
        " ON im1.id == page.originalImage_id JOIN document ON document.id == "
        "page.document_id ORDER BY page.document_id, page.\"order\""
    ):
        r = dict(row)
        title = r["title"]
        original = r["original_uuid"]
        final = r["warped_uuid"]
        quadrangle = r["quadrangle2"]

        original_path = os.path.join(image_dir, original + ".jpg")
        final_path = os.path.join(image_dir, final + ".jpg")

        original_docs[title].append(original_path)
        modified_docs[title].append(final_path)
        quads[original_path] = (original, quadrangle)

    # put all the originals into a PDF
    for title, image_files in original_docs.items():
        image_files_to_pdf("original", title, image_files)

    # # put all the modified versions into a PDF
    # for title, image_files in modified_docs.items():
    #     image_files_to_pdf("modified", title, image_files)

    # recover the geometric warping without color changes
    os.makedirs(os.path.join(image_dir, "warped"), exist_ok=True)
    warped_docs = {}
    for fpath, (uuid, quadstring) in quads.items():
        if quadstring != "0.0/0.0/1.0/0.0/0.0/1.0/1.0/1.0":
            warped_file = os.path.join(
                image_dir, "warped", "warped_" + uuid + ".jpg"
            )
            warped_docs[fpath] = warped_file
            if not os.path.isfile(warped_file):
                print(f"Writing {warped_file}")
                warped = warp_file_from_quadstring(fpath, quadstring)
                cv2.imwrite(warped_file, warped)
            else:
                print(f"{warped_file} already exists")

    for title, image_files in original_docs.items():
        image_files = [warped_docs.get(f, f) for f in image_files]
        image_files_to_pdf("warped", title, image_files)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Input arguments must be <path_to_database.db> <path_to_images_directory>")
        exit()

    main(sys.argv[1], sys.argv[2])
