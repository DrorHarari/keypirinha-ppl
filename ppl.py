#TODO - set action on item and use it instead of KP action
import keypirinha as kp
import keypirinha_util as kpu
import json
import re
from pathlib import Path
import os
import sys
import datetime
import pprint
from shutil import copyfile

# Main actions
# {CALL|HOME|CELL|WORK|MAIN} - dial a phone of given contact name (for CALL defaults to first number in contact)
# EMAIL - send an email to a given contact name
# INFO - copy contact card information of a given contact name


class Verb(object):
    name: str
    desc: str
    contact_field: str
    action: str
    
    def __init__(self, name, desc, contact_field, action):
        self.name = name
        self.desc = desc
        self.contact_field = contact_field
        self.action = action

class Contact(object):
    name: str
    mail: str
    description: str
    
    def __init__(self, name="", mail="", description=""):
        self.name = name
        self.mail = mail
        self.description = description

class VcfFile(object):
    filename: str
    source: str
    reload_delta: datetime.timedelta
    next_reload: datetime.datetime

    def __init__(self, filename="", source="", reload_delta = 60):
        self.filename = filename
        self.source = source
        self.reload_delta = reload_delta
        
class Ppl(kp.Plugin):
    vcf_tel_parser = re.compile(r'^TEL;TYPE=(?P<type>[a-zA-Z][a-zA-Z0-9]*)$')
    pp = pprint.PrettyPrinter(indent=4)

    # Attributes in the contacts json doc
    AD_ATTR_NAME = 'name'
    AD_ATTR_MAIL = 'mail'
    AD_ATTR_PHONE = 'call'
    AD_ATTR_CELL = 'cell'
    AD_ATTR_HOME = 'home'
    AD_ATTR_TITLE = 'description'

    # Default protocol handlers
    CALLING_PROTOCOL = "tel:%s"
    MAILING_PROTOCOL = "mailto:%s"

    # Plugin actions
    ACTION_CALL = "call"
    ACTION_MAIL = "mail"
    ACTION_CARD = "card"
    ACTION_COPY = "copy"
    
    ITEMCAT_CALLEE_M = kp.ItemCategory.USER_BASE + 1
    ITEMCAT_CALLEE_P = kp.ItemCategory.USER_BASE + 2
    ITEMCAT_CALLEE_H = kp.ItemCategory.USER_BASE + 3
    ITEMCAT_MAILEE = kp.ItemCategory.USER_BASE + 4
    ITEMCAT_CONTACT = kp.ItemCategory.USER_BASE + 5
    ITEMCATS = (ITEMCAT_CALLEE_M, ITEMCAT_CALLEE_P,  ITEMCAT_CALLEE_H, ITEMCAT_MAILEE, ITEMCAT_CONTACT)

    ITEM_LABEL_PREFIX = "Ppl: "
    
    ID_NAME = "name"
    
    SAMPLE_VCF = r"sample-contacts.vcf"
    PACKAGED_SAMPLE_VCF = r"etc\sample-contacts.vcf"
    VCF_SECTION_PREFIX = "vcf/"
    
    VERB_LIST = [
        Verb('Call',   'Call contact',            AD_ATTR_PHONE,    ACTION_CALL),
        Verb('Info',   'Contact info',            AD_ATTR_NAME,     ACTION_CARD),
        Verb('Mail',   'Mail contact',            AD_ATTR_MAIL,     ACTION_MAIL),
        Verb('Cell',   'Call contact cell',       'TEL;TYPE=CELL',  ACTION_CALL),
        Verb('Home',   'Call contact home',       'TEL;TYPE=HOME',  ACTION_CALL),
        Verb('Work',   'Call contact work',       'TEL;TYPE=WORK',  ACTION_CALL)
    ]
    
    CONTACTS_FILE = "contacts.json"

    def __init__(self):
        super().__init__()

    def load_vcard_file(self, vcf_file_path):
        self.info(f"Loading contacts file {vcf_file_path}")
        with open(vcf_file_path, "r", encoding='utf-8') as vcf:
            contact = None
            for line in vcf:
                if "BEGIN:VCARD\n" == line:
                    contact = {} #Contact()
                    contact[self.AD_ATTR_MAIL] = ""
                    contact[self.AD_ATTR_TITLE] = ""
                    continue
                elif line.startswith("END:VCARD"):
                    if contact:
                        self.contacts.append(contact)
                    contact = None
                    continue

                parts = line.strip().rsplit(':', 1)
                # tel_match = self.vcf_tel_parser.match(parts[0])
                # elif tel_match:
                #     print(f"{tel_match['type']} --> {parts[1]}\n")
                vcf_field = parts[0]
                if "FN" == vcf_field:
                    contact[self.AD_ATTR_NAME] = parts[1]
                elif vcf_field.startswith("TEL;"):
                    contact[vcf_field] = parts[1]
                elif vcf_field.startswith("EMAIL;"):
                    contact[self.AD_ATTR_MAIL] = parts[1]
                elif vcf_field.startswith("TITLE"):
                    contact[self.AD_ATTR_TITLE] += parts[1]
                elif vcf_field.startswith("NICKNAME"):
                    contact[self.AD_ATTR_TITLE] += parts[1]
                elif vcf_field.startswith("NOTE"):
                    contact[self.AD_ATTR_TITLE] += parts[1]

    def get_vcf_files(self):
        vcard_files = []

        vcard_file_list = self.settings.get_multiline("vcard_files", "main", [])
        for vcard_file in vcard_file_list:
            vcard_files.append(VcfFile(vcard_file))

        for section in self.settings.sections():
            if section.lower().startswith(self.VCF_SECTION_PREFIX):
                vcard_file = section[len(self.VCF_SECTION_PREFIX):].strip()
                if not vcard_file in vcard_file_list:
                    source = self.settings.get_stripped("source", section=section, fallback=None)
                    reload_delta_hours = self.settings.get_int("reload_delta_hours", section=section, fallback=None, min=0)
                    vcard_files.append(VcfFile(vcard_file, source, reload_delta_hours))

        return vcard_files

    def load_contacts_and_settings(self):
        self.contacts = []

        self.call_protocol = self.settings.get_stripped("call_protocol", "main", self.CALLING_PROTOCOL)
        self.cell_protocol = self.settings.get_stripped("cell_protocol", "main", self.CALLING_PROTOCOL)
        self.home_protocol = self.settings.get_stripped("home_protocol", "main", self.CALLING_PROTOCOL)
        self.mail_protocol = self.settings.get_stripped("mail_protocol", "main", self.MAILING_PROTOCOL)

        self.vcard_files = self.get_vcf_files()
        
        # Install a demo vCard file if non is configured (will be ignored once configured)
        if len(self.vcard_files) == 0:
            sample_vcf_path = os.path.join(kp.user_config_dir(), self.SAMPLE_VCF)
            if not os.path.exists(sample_vcf_path):
                sample_vcf_text = self.load_text_resource(self.PACKAGED_SAMPLE_VCF).replace("\r\n","\n")
                with open(sample_vcf_path, "w") as f:
                    f.write(sample_vcf_text)
                    f.close()
            self.load_vcard_file(sample_vcf_path)
            return

        for vcard_file in self.vcard_files:
            vcard_file_path = os.path.join(kp.user_config_dir(), vcard_file.filename)
            try:
                if vcard_file.source and os.path.exists(vcard_file.source):
                    copyfile(vcard_file.source, vcard_file_path)
                if not os.path.exists(vcard_file_path):
                    if vcard_file.source != None:
                        self.err(f"Failed to load vCard file '{vcard_file_path}'. File does not exist and cannot be copied from {vcard_file.source}")
                    else:
                        self.err(f"Failed to load vCard file '{vcard_file_path}'. File does not exist")
                    continue
                self.load_vcard_file(vcard_file_path)
            except Exception as exc:
                self.err(f"Failed to load vCard (.vcf) file {vcard_file_path}, {exc}")
    
    def on_start(self):
        self.settings = self.load_settings()
        #self._debug = True
        
        self.load_contacts_and_settings()
        self.VERBS = { v.name: v for v in self.VERB_LIST}

        if self._debug:
            self.pp.pprint(self.contacts)

        call_cellular_action = self.create_action(
                name=self.ACTION_CALL,
                label="Call cellular",
                short_desc="Call the cellular number",
                data_bag = self.AD_ATTR_CELL)

        # call_phone_action = self.create_action(
                # name = self.ACTION,
                # label = "Call phone",
                # short_desc = "Call the phone number",
                # data_bag = self.AD_ATTR_PHONE)
                
        # call_home_action = self.create_action(
                # name = self.ACTION,
                # label = "Call home",
                # short_desc = "Call the home number",
                # data_bag = self.AD_ATTR_HOME)
                
        # mail_action = self.create_action(
                # name=self.ACTION_MAIL,
                # label="Send mail",
                # short_desc="Send a mail to the contact",
                # data_bag = self.AD_ATTR_MAIL)
                
        # card_action = self.create_action(
                # name=self.ACTION_CARD,
                # label="Copy contact",
                # short_desc="Copy contact information to clipboard")
                
        # copy_action = self.create_action(
                # name=self.ACTION_COPY,
                # label="Copy item",
                # short_desc="Copy looked up item")
                
        # self.set_actions(self.ITEMCAT_CALLEE_M, [call_cellular_action, call_phone_action, call_home_action, copy_action, card_action]) 
        # self.set_actions(self.ITEMCAT_CALLEE_P, [call_phone_action, call_cellular_action, call_home_action, copy_action, card_action]) 
        # self.set_actions(self.ITEMCAT_CALLEE_H, [call_home_action, call_phone_action, call_cellular_action, copy_action, card_action]) 
        # self.set_actions(self.ITEMCAT_MAILEE,   [mail_action, copy_action, card_action]) 
        # self.set_actions(self.ITEMCAT_CONTACT,  [card_action, copy_action]) 
        pass

    def on_activated(self):
        pass

    def on_deactivated(self):
        pass

    def on_events(self, flags):
        if flags & kp.Events.PACKCONFIG:
            self.load_contacts_and_settings()
            self.on_catalog()

    def t(self, txt):
        self.info(txt)
        return txt

    def on_catalog(self):
        # Creating verbs Info, Mail, Call, Cell, Home, ...
        catalog = [
            self.create_item(
                    category = kp.ItemCategory.REFERENCE,
                    label = self.ITEM_LABEL_PREFIX + v.name,
                    short_desc = v.desc,
                    target = v.name,
                    args_hint = kp.ItemArgsHint.REQUIRED,
                    hit_hint = kp.ItemHitHint.NOARGS)
            for v in self.VERB_LIST
        ]

        self.set_catalog(catalog)
    
    def suggest_execution(self, items_chains, params):
        contact_no = int(params['contact_no'])
        contact = self.contacts[contact_no]

        self.info(f"executing contact {repr(contact)}")
        return

        l = [{"label": a.label(), "target": a.target()} for a in items_chain]
        self.t(f"on-suggest {repr(l)}\n")
        self.info(f"params={repr(params)}")

        # Creating list of "{verb} {name} - {associated-item}"
        suggestions = []
        for idx, contact in enumerate(self.contacts):
            if (not (verb.contact_field in contact) or 
                not (self.ID_NAME in contact) or
                not contact[self.ID_NAME]):
                continue
            
            if len(suggestions) > 10:
                break
                
            item = contact[verb.contact_field]
            if not item or not user_input.lower() in contact[self.ID_NAME].lower():
                continue

            title = contact[self.AD_ATTR_TITLE] if self.AD_ATTR_TITLE in contact else ""
            suggestions.append(self.create_item(
                category=verb.category,
                label=f'{verb.name} {contact[self.ID_NAME]} - {contact[verb.contact_field]}',
                short_desc=f"{contact[self.AD_ATTR_TITLE]}",
                target=item,
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.IGNORE,
                loop_on_suggest = True,
                data_bag=kpu.kwargs_encode(verb=verb.contact_field, contact_no=idx, default_action=True)))

        self.set_suggestions(suggestions, kp.Match.ANY, kp.Sort.NONE)

    
    def on_suggest(self, user_input, items_chain):
        if not items_chain or not user_input:
            return

        if self._debug:
            self.dbg(f"items_chain[0].target() = {items_chain[0].target()}")
            self.pp.pprint(items_chain[0])
            self.pp.pprint(items_chain[0].target())

        verb = self.VERBS[items_chain[0].target()]

        if self._debug:
            self.dbg(f"Adding suggestions for {verb.name}: {user_input}\n")

        if items_chain[-1].data_bag():
            params = kpu.kwargs_decode(items_chain[-1].data_bag()) 
        else:
            params = None
        if params and 'default_action' in params:
            self.suggest_execution(items_chain, params)
            return

        # Creating list of "{verb} {name} - {associated-item}"
        suggestions = []
        for idx,contact in enumerate(self.contacts):
            if len(suggestions) > 10:
                break
                
            if (not (self.ID_NAME in contact) or not contact[self.ID_NAME]):
                continue
            
            if not user_input.lower() in contact[self.ID_NAME].lower():
                continue

            item_target = None
            if (verb.contact_field.startswith("TEL;") and verb.contact_field in contact):
                item_target = contact[verb.contact_field]
                item_label = f'{verb.name} {contact[self.ID_NAME]} - {item_target}'
            elif (verb.contact_field == self.AD_ATTR_PHONE):
                for v in self.VERB_LIST:
                    if v.contact_field.startswith("TEL;") and v.contact_field in contact:
                        item_target = contact[v.contact_field]
                        item_label = f'{verb.name} {contact[self.ID_NAME]} - {item_target}'
                        break
                if not item_target:
                    continue
            elif verb.contact_field in contact:
                item_target = contact[verb.contact_field]
                item_label = f'{verb.name} {contact[self.ID_NAME]} - {item_target}'
            else:
                continue

            title = contact[self.AD_ATTR_TITLE] if self.AD_ATTR_TITLE in contact else ""
            suggestions.append(self.create_item(
                category=kp.ItemCategory.REFERENCE,
                label=item_label,
                short_desc=f"{contact[self.AD_ATTR_TITLE]}",
                target=item_target,
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.IGNORE,
                loop_on_suggest = True,
                data_bag=kpu.kwargs_encode(verb_name=verb.name, contact_no=idx, default_action=False)))

        self.set_suggestions(suggestions, kp.Match.ANY, kp.Sort.NONE)

    def do_card_action(self, contact):
        text = f"Name\t{contact[self.AD_ATTR_NAME]}"
        
        if contact[self.AD_ATTR_MAIL]:
            text += f"\nMail\t{contact[self.AD_ATTR_MAIL]}"
        for v in self.VERB_LIST:
            if v.contact_field.startswith("TEL;") and v.contact_field in contact:
                text += f"\n{v.name}#\t{contact[v.contact_field]}"
        if contact[self.AD_ATTR_TITLE]:
            text += f"\nTitle\t{contact[self.AD_ATTR_TITLE]}"

        kpu.set_clipboard(text)

    def do_call_action(self, contact, selection, protocol):
        url = protocol.replace("%s", selection.replace(" ", ""))
        kpu.shell_execute(url, args='', working_dir='', verb='', try_runas=True, detect_nongui=True, api_flags=None, terminal_cmd=None, show=-1)
    
    def do_mail_action(self, contact, verb, protocol):
        url = protocol.replace("%s", contact[verb.contact_field].replace(" ", ""))
        kpu.shell_execute(url, args='', working_dir='', verb='', try_runas=True, detect_nongui=True, api_flags=None, terminal_cmd=None, show=-1)
    
    def on_execute(self, item, action):
        if (not item):
            return 
            
        selection = item.target()
        params = kpu.kwargs_decode(item.data_bag())
        verb_name = params['verb_name']
        contact_no = int(params['contact_no'])
        contact = self.contacts[contact_no]
        verb = self.VERBS[verb_name]
        default_action = params['default_action'];

        if self._debug:
            self.dbg(f"Executing {verb_name}: {selection} (default_action={default_action})\n")


        # self.t(f"verb=\n")
        # self.pp.pprint(verb)
        # self.t(f"contact=\n")
        # self.pp.pprint(contact)        

        if verb.action == self.ACTION_CALL:
            self.do_call_action(contact, selection, self.cell_protocol)
        elif verb.action == self.ACTION_MAIL:
            self.do_mail_action(contact, verb, self.mail_protocol)
        elif verb.action == self.ACTION_CARD:
            self.do_card_action(contact)
        elif verb.action == self.ACTION_COPY:
            kpu.set_clipboard(contact[verb.contact_field])
