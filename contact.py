from typing import Dict

class Contact(object):
    name: str
    nickname: str
    title: str
    org: str
    note: str
    mailboxes: Dict[str,str]
    phones: Dict[str,str]
    addresses: Dict[str,str]
    birthday: datetime.datetime
    
    def __init__(self, name: str):
        self.name = name
        self.nickname = ""
        self.title = ""
        self.org = ""
        self.note = ""
        self.mailboxes = {}
        self.phones = {}
        self.addresses = {}
        self.birthday = None

    def __str__(self):
        items = ("%s: %r\n" % (k, v) for k, v in self.__dict__.items() if v and k != "name")
        return f"Contact {self.name}:\n{', '.join(items)}"

    def __repr__(self):
        items = ("%s = %r" % (k, v) for k, v in self.__dict__.items() if v )
        return "<%s: {%s}>" % (self.__class__.__name__, ', '.join(items))
