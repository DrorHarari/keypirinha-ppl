import datetime
from shutil import copyfile
from typing import Dict, Tuple, Sequence
from dateutil import parser as date_parser
import vobject
import contact

class VcardFile(object):
    filename: str
    source_name: str
    source: str
    reload_delta: datetime.timedelta
    next_reload: datetime.datetime
    contacts: Sequence

    def __init__(self, filename, source_name="", source="", reload_delta = 60):
        self.filename = filename
        self.source = source
        self.source_name = source_name
        self.reload_delta = reload_delta
        self.contacts = []

    def add_attribute(self, vo, contact, attribute):
        if attribute in vo.contents.keys():
            setattr(contact,attribute, vo.contents[attribute][0].value)

    def add_email(self, vo, contact, attribute, idx = 0):
        if attribute in vo.contents.keys():
            setattr(contact,attribute, vo.contents[attribute][idx].value)

    def make_contact(self, vo):
        name = None
        if 'fn' in vo.contents.keys():
            name = vo.contents['fn'][0].value
        elif 'n' in vo.contents.keys():
            n = vo.contents['n'][0].value
            name = f"{n.prefix} {n.given} {n.additional} {n.family} {n.suffix}".replace("  ","").strip()
        else:
            return None

        contact = Contact(name)
        if contact:
            self.contacts.append(contact)

        self.add_attribute(vo, contact, "title")
        self.add_attribute(vo, contact, "nickname")
        self.add_attribute(vo, contact, "note")
        self.add_attribute(vo, contact, "org")

        if 'bday' in vo.contents.keys():
            contact.birthday = date_parser.parse(vo.contents['bday'][0].value)

        if 'email' in vo.contents.keys():
            for email in vo.contents['email']:
                type = "other"
                if 'TYPE' in email.params:
                    type = email.params['TYPE'][-1]
                contact.mailboxes[type] = email.value

            if 'INTERNET'in contact.mailboxes and not 'HOME' in contact.mailboxes:
                contact.mailboxes['HOME'] = contact.mailboxes['INTERNET']
                contact.mailboxes.pop('INTERNET')

        if 'tel' in vo.contents.keys():
            for tel in vo.contents['tel']:
                type = "other"
                if 'TYPE' in tel.params:
                    type = tel.params['TYPE'][-1]
                contact.phones[type] = tel.value

            # if 'INTERNET'in contact.mailboxes and not 'HOME' in contact.mailboxes:
                # contact.mailboxes['HOME'] = contact.mailboxes['INTERNET']
                # contact.mailboxes.pop('INTERNET')

        return contact

    def load(self):
        with open(self.filename, "r", encoding='utf-8') as f:
            vcfdata = f.read()
            vc = vobject.readComponents(vcfdata)
            vo = next(vc, None)
            while vo is not None:
                contact = self.make_contact(vo)
                vo = next(vc, None)

    def load_vcard_file(self):
        with open(self.filename, "r", encoding='utf-8') as vcf:
            contact = None
            one_vcard = ""
            for line in vcf:               
                if one_vcard == "" and "BEGIN:VCARD\n" == line:
                    
                    contact = {} #Contact()
                    contact[self.AD_ATTR_PHONE] = ""
                    contact[self.AD_ATTR_MOBILE] = ""
                    contact[self.AD_ATTR_HOME] = ""
                    contact[self.AD_ATTR_MAIL] = ""
                    contact[self.AD_ATTR_TITLE] = ""
                    continue
                elif "END:VCARD\n" == line:
                    if contact:
                        self.contacts.append(contact)
                    contact = None
                    continue

                parts = line.strip().rsplit(':', 1)
                if "FN" == parts[0]:
                    contact["name"] = parts[1]
                elif parts[0].startswith("TEL;") and parts[0].endswith("WORK"):
                    contact[self.AD_ATTR_PHONE] = parts[1]
                elif parts[0].startswith("TEL;") and parts[0].endswith("CELL"):
                    contact[self.AD_ATTR_MOBILE] = parts[1]
                elif parts[0].startswith("TEL;") and parts[0].endswith("HOME"):
                    contact[self.AD_ATTR_HOME] = parts[1]
                elif parts[0].startswith("EMAIL;"):
                    contact[self.AD_ATTR_MAIL] = parts[1]
                elif parts[0].startswith("TITLE"):
                    contact[self.AD_ATTR_TITLE] += parts[1]
                elif parts[0].startswith("NICKNAME"):
                    contact[self.AD_ATTR_TITLE] += parts[1]
                elif parts[0].startswith("NOTE"):
                    contact[self.AD_ATTR_TITLE] += parts[1]


if False:
    onevcard = """
BEGIN:VCARD
VERSION:3.0
FN:John Doe
N:Doe;John;;;
NICKNAME:Johnchuk
TITLE:Manager
ORG:Acme\, Inc.;North Division;Sales
item2.TITLE:Chief Sparrow
item2.X-ABLabel:Avatar
NOTE:Gender: Male
BDAY:19751021
item1.ORG:ABC\, Inc.;North American Division;Marketing
item2.X-ABLabel:Fake
X-PHONETIC-FIRST-NAME:ג'ון
X-PHONETIC-LAST-NAME:דו
URL:www.שבצק.com
ADR;TYPE=HOME:;somewhere;;;;;
ADR;TYPE=WORK:;;13 Eckers;Tinan;;;Spain
TEL;TYPE=CELL:+952 12-126-7463
TEL;TYPE=WORK:1-700-701-011
TEL;TYPE=HOME:1-700-701-019
TEL;TYPE=MAIN:04-631-6124
item1.TEL:+952 71-801-3624
item1.X-ABLabel:Fax
EMAIL;TYPE=INTERNET;TYPE=HOME:john.doe@gmail.com
EMAIL;TYPE=INTERNET;TYPE=WORK:john.doe@acme.com
item1.EMAIL;TYPE=INTERNET:dot.gofer@alberti.com
item1.X-ABLabel:Info
END:VCARD
"""
    vo = vobject.readOne(onevcard)
    vo.prettyPrint()

#>>> vo.prettyPrint()
# VCARD
#    VERSION: 3.0
#    FN: John Doe
#    N:  John  Doe
#    NICKNAME: Johnchuk
#    TITLE: Manager
#    TITLE: Chief Sparrow
#    ORG: ['Acme, Inc.', 'North Division', 'Sales']
#    ORG: ['ABC, Inc.', 'North American Division', 'Marketing']
#    X-ABLABEL: Avatar
#    X-ABLABEL: Fake
#    X-ABLABEL: Fax
#    X-ABLABEL: Info
#    NOTE: Gender: Male
#    BDAY: 19751021
#    X-PHONETIC-FIRST-NAME: ג'ון
#    X-PHONETIC-LAST-NAME: דו
#    URL: www.שבצק.com
#    ADR: somewhere
#,
#    params for  ADR:
#       TYPE ['HOME']
#    ADR: 13 Eckers
#Tinan,
#Spain
#    params for  ADR:
#       TYPE ['WORK']
#    TEL: +952 12-126-7463
#    params for  TEL:
#       TYPE ['CELL']
#    TEL: 1-700-701-011
#    params for  TEL:
#       TYPE ['WORK']
#    TEL: 1-700-701-019
#    params for  TEL:
#       TYPE ['HOME']
#    TEL: 04-631-6124
#    params for  TEL:
#       TYPE ['MAIN']
#    TEL: +952 71-801-3624
#    EMAIL: john.doe@gmail.com
#    params for  EMAIL:
#       TYPE ['INTERNET', 'HOME']
#    EMAIL: john.doe@acme.com
#    params for  EMAIL:
#       TYPE ['INTERNET', 'WORK']
#    EMAIL: dot.gofer@alberti.com
#    params for  EMAIL:
#       TYPE ['INTERNET']