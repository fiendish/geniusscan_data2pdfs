import os
import re
import sqlite3
import sys

import img2pdf


def main(db_path='database.db', image_dir=''):
    if not os.path.exists(db_path) or not os.path.isfile(db_path):
        print("Database file not found: " + db_path)
        return
    if not os.path.exists(image_dir) or not os.path.isdir(image_dir):
        print("Image directory not found: " + image_dir)
        return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    documents = {}

    for row in c.execute(
        'SELECT document.title, images.uuid FROM page'
        + ' JOIN images ON images.id == page.warpedImage_id'
        + ' JOIN document ON document.id == page.document_id'
        + ' ORDER BY page.document_id, page."order"'
    ):
        if row[0] not in documents:
            documents[row[0]] = []

        documents[row[0]].append(os.path.join(image_dir, row[1] + ".jpg"))

    for doc, images in documents.items():

        doc = re.sub(r'[/\\:*?"<>|]', '_', doc) + ".pdf"

        print("Writing", doc)
        with open(doc, "wb") as pdf:
            pdf.write(img2pdf.convert(images))
        print("done")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Input arguments must be <path_to_database.db> <path_to_images_directory>")
        exit()

    main(sys.argv[1], sys.argv[2])
