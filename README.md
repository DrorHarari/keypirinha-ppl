Keypirinha Plugin: Ppl
=========
# Easily call, email and copy contact information

This plugin for Keypirinha lets you quickly call, email or look up details of your contacts from the Keypirinha launch box.

The Ppl plugin (pronounced like people) supports the vCard file format for contacts as can be exported, for example, from Google Contacts.

## Usage ##
Open the LaunchBox and type:
```
Call <tab> <name> [<tab-to-select-actions-or-enter-for-default>
```

```
Cell <tab> <name> [<tab-to-select-actions-or-enter-for-default>
```

```
Mail <tab> <name> [<tab-to-select-actions-or-enter-for-default>
```

```
Info <tab> <name> [<tab-to-select-actions-or-enter-for-default>
```

In most cases it is enough to just type the action followed by a tab and name. If typing the action name does not find it, you may need just one time to prefix it with Ppl: - for example:
```
Ppl: Call <tab> <name> [<tab-to-select-actions-or-enter-for-default>
```

## Installation and Setup ##
Make sure to install Keypirinha from http://keypirinha.com/

The easiest way to install Ppl is to use the [PackageControl](https://github.com/ueffel/Keypirinha-PackageControl) plugin's InstallPackage command. 

For manual installation simply download the ppl.keypirinha-package file from the Releases page of this repository to:

* `Keypirinha\portable\Profile\InstalledPackages` in **Portable mode**

**Or** 

* `%APPDATA%\Keypirinha\InstalledPackages` in **Installed mode** 

Ppl comes with a sample contacts file to play with (it is written to the user folder as sample-contacts.vcf) but to use the plugin, you'll need to export your contacts into a vCard format (a .vcf file) from Google Contacts or from another application add add it to the Ppl configuration file. 

In the following example, we add a company contacts vCard file from a shared location and a Google contact file from the User configuration directory:

```
...
[vcf/company-contacts.vcf]
source = \\fileserv\shared\company-contacts.vcf

[vcf/my-google-contacts.vcf]
...
```

The default Windows Shell protocol for calling a phone number is the TEL: protocol, and the default protocol for emailing is the MAILTO: protocol. The call_protocol and mail_protocol items in the Ppl configuration file can be used to select a different protocol handler. For example, to force cell calls to explicitly use Skype change the configuration as follow:

```
[main]
...
cell_protocol = skype:%s
...
```

***Advanced***
To use contacts from Microsoft Outlook which does not export multiple contacts to a .vcf file, there is a program make_contacts.py in the etc folder of the plugin which can automatically generate a contacts.json file that plugin can use. Please see that program for detailed instructions for how to use it. The process is currently a little involved and will be improved in a later version. The resulting contacts.json needs to be copied to Keypirinha's User folder.

## Future ##

There are many ideas to make Ppl better but it is already very useful in its current form. Future enhancements may include:
* Support Outlook csv contacts export format 
* Support more contact entry fields
* ...

## Release Notes ##

**V0.8**
- Add 'encoding' when adding a vcf file in the plugin configuration (default remains utf-8)

**V0.7**
- Show relevant phone number with the relevant action

**V0.6**
- Remove support for contacts.json
- Support copying vCard from predefined remote source (e.g. shared VCF contacts file)
- Add support for home phone numbers in VCF files

**V0.5**
- Support custom protocol handlers for calling and mailing.

**V0.4.1**
- Initial public, pretty useful!

**V0.1**
- Initial release, rough around the edges.
