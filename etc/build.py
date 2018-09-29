# The build.py script is assumed to be located in the package's etc folder
from pathlib import Path
import os
import zipfile

PACKAGE_NAME="Ppl"
FILES=["ppl.py","ppl.ini","ppl.ico","LICENSE","etc/make_contacts.py"]

ETC_FOLDER=Path(__file__).parent
PACKAGE_FOLDER=ETC_FOLDER.parent
PACKAGE_FILE=Path.joinpath(PACKAGE_FOLDER, f"{PACKAGE_NAME}.keypirinha-package")

print(f"Creating package file {PACKAGE_FILE}")

try:
    zf = zipfile.ZipFile(PACKAGE_FILE,'w',zipfile.ZIP_DEFLATED)
    for f in FILES:
        zf.write(Path.joinpath(Path('..'), f), f)

    zf.close()
except Exception as exc:
    print(f"Failed to create package {PACKAGE_NAME}. {exc}")
    os._exit(1)

print(f"Done")
