# Export contacts from an organization's Active Directory (AD) into a
# VCF file contacts that can be used with the Keypirinha plugin Ppl
# (see http://github.com/DrorHarari/keypirinha-ppl)
#
# Prerequisites:
# 1. This program depends on the win32com Python package. Install
#    it with the command:
#      $ pip install pywin32
# 2. This program relies on the user's Windows Authentication to access AD.
# 3. Various companies use different attributes in their contacts objects
#    in AD. The attributes used here are defined in CONTACT_AD_ATTRS, your
#    organization may differ. The best tool to use to find what attributes
#    are used in your organization is the Microsoft ADExplorer.exe program
#    (see https://docs.microsoft.com/en-us/sysinternals/downloads/adexplorer)
# 4. The contacts.json generated by this program should be placed in 
#    Keypirinha's User folder ({Keypirinha-Root-Dir}\portable\Profile\User)
# 5. Note that the Ppl plugin will ignore contacts that do not at least the
#    first attribute (displayName here)
#
# Note: If you do not want to permanently install the pywin32 package in
# your environment, you can set a disposable virtual environment as follows:
# 
# # {ensure you have Python 3.6+ installed)
# $ python -m venv tempenv
# $ cd tempenv 
# $ .\Scripts\activate.bat
# $ pip install pywin32
# {now you can run make_contacts.py}
# {you may need to repeat after some edits...}
# {finally you can delete the virtual environment - unless you may want to repeat in future}
# $ cd ..
# $ rmdir /s /q tempenv
import win32com.client
import io
import os
import sys
import json
import datetime
import shutil

# Name of the VCF file created out of the AD entries
VCF_FILE = "ad-contacts.vcf"

# The Active Directory OU (organization unit) where the contacts are
# This may change between organizations 
CONTACTS_OU = "OU=Employees"

# Map between CN (common name) attributes (in order) and the equivalent VCF properties:
# (repeated occurances of the same VCF attribute are concatenated with the delimiter ;
AD_ATTR_MAP = {
    "displayName": "FN",
    "mail": "EMAIL;TYPE=INTERNET;TYPE=WORK",
    "company": "item1.ORG",
    "department": "item1.ORG",
    "title": "TITLE",
    "telephoneNumber": "TEL;TYPE=WORK",
    "mobile": "TEL;TYPE=CELL"
}

REQUIRED_ATTRS = ["mail", "telephoneNumber", "mobile"]

VCF_ESCAPES = str.maketrans({
    ",":    r"\,", 
    ";": r"\;", 
    "\\":   r"\\", 
    "\n":   r"\\n"})

def add_cn(adobj, entries):
    n_required = 0
    entry = {}
    for attr in AD_ATTR_MAP.keys():
        try:
            val = getattr(adobj,attr)
            if val != None:
                val = val.translate(VCF_ESCAPES)
                if AD_ATTR_MAP[attr] in entry:
                    entry[AD_ATTR_MAP[attr]] += ";"+val
                else:
                    entry[AD_ATTR_MAP[attr]] = val
        except Exception as exc:
            print(f"No attr {attr} for {adobj.cn}")
            pass
            
        if attr in REQUIRED_ATTRS:
            n_required += 1

    if n_required == len(REQUIRED_ATTRS):
        print(f"Adding {adobj.cn}")
        entries.append(entry)

def scan_ou_s(ldap_path, entries):
    global cnt
    print(f"Scanning LDAP path: LDAP://{ldap_path}")
    for o in win32com.client.GetObject(f"LDAP://{ldap_path}"):
        if o.cn == 'Active Directory Connections':
            continue
        elif o.cn is not None:
            add_cn(o, entries)
        elif o.ou != None:
            scan_ou_s(f"OU={o.ou},{ldap_path}", entries)

# This function tries to auto-discover the AD LDAP base location 
print("Finding your Active Directory LDAP base location...")
try:
    ldap_loc=win32com.client.GetObject('LDAP://rootDSE').Get("defaultNamingContext")
except Exception as exc:
    print(f"Failed to find LDAP base location. {exc}")
    sys.exit(1)

print(f"Found base location: LDAP://{ldap_loc}")

entries = []
scan_loc = ",".join([CONTACTS_OU, ldap_loc])
scan_ou_s(scan_loc, entries)

vcf_file = sys.argv[1] if len(sys.argv) > 1 else VCF_FILE
new_vcf_file = f"{vcf_file}-{str(datetime.datetime.now()).replace(' ','T').replace(':','.')}"

print(f"Writing contacts to {new_vcf_file}")
try:
    with io.open(new_vcf_file, 'w', encoding='utf8') as outfile:
        for entry in entries:
            outfile.write(f"BEGIN:VCARD\n")
            outfile.write(f"VERSION:3.0\n")
            for item in entry:
                outfile.write(f"{item}:{entry[item]}\n")   
            outfile.write(f"END:VCARD\n")
except Exception as exc:
    print(f"Failed to write new contact list {new_vcf_file}. {exc}")
    sys.exit(2)

print("Checking for new contact data")
try:
    with io.open(vcf_file, 'r') as old_file:
        old_data = old_file.readlines()
    with io.open(new_vcf_file, 'r') as new_file:
        new_data = new_file.readlines()
except Exception as exc:
    print(f"Failed to compare old and new contact list. {exc}")
    sys.exit(3)

if old_data == new_data:
    print(f"No contact changes found. No change performed.")
    try:
        os.remove(new_vcf_file)
    except:
        pass
    sys.exit(0)
else:
    try:
        shutil.copy(new_vcf_file, vcf_file)
    except Exception as exc:
        print(f"Failed to copy {new_vcf_file} over {vcf_file}. {exc}")
        sys.exit(2)

print(f"Done")
