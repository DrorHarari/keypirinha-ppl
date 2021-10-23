# The build.py script is assumed to be located in the package's etc folder
from pathlib import Path
import os
import zipfile

PACKAGE_NAME = "ppl"
PACKAGE_VERSION = f" (version {os.environ['PACKAGE_VERSION']})" \
    if "PACKAGE_VERSION" in os.environ else ""
FILES = ["ppl.py", "ppl.ini", "ppl.ico", "LICENSE", "etc/make_contacts.py", "etc/sample-contacts.vcf"]

# Following is common code
ETC_FOLDER = Path(__file__).parent
PACKAGE_FOLDER = ETC_FOLDER.parent
PACKAGE_FILE = Path.joinpath(PACKAGE_FOLDER, f"{PACKAGE_NAME}.keypirinha-package")

print(f"Creating package file {PACKAGE_FILE}")

try:
    zf = zipfile.ZipFile(PACKAGE_FILE,'w', zipfile.ZIP_DEFLATED)
    for f in FILES:
        if PACKAGE_VERSION and f == f"{PACKAGE_NAME}.ini":  # Replace {version} in package configuration template
            with open(Path.joinpath(Path('..'), f), "r", encoding="utf-8") as inif:
                ini = ''.join(inif.readlines())
                ini = cvtini.replace("{#version#}", PACKAGE_VERSION)
                zf.writestr(f, ini.encode())
            continue

        zf.write(Path.joinpath(Path('..'), f), f)

    zf.close()
except Exception as exc:
    # Package is corrupted - better delete it
    if zf:
        zf.close()
        os.remove(PACKAGE_FILE)
    print(f"Failed to create package {PACKAGE_NAME}. {exc}")
    os._exit(1)

print("Done")
