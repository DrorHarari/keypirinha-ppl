Keypirinha Plugin: Ppl
=========
# Easily call, email and copy contact information

This plugin for Keypirinha lets you quickly call, email or look up details of your contacts from the Keypirinha launch box.

The Ppl plugin (pronounced like people) supports the vCard file format for contacts as can be exported, for example, from Google Contacts.

## Usage ##
Make sure to install Keypirinha from http://keypirinha.com/

The easiest way to install Cvt is to use the [PackageControl](https://github.com/ueffel/Keypirinha-PackageControl) plugin's InstallPackage command. 

For manual installation simply download the cvt.keypirinha-package file from the Releases page of this repository to:

* `Keypirinha\portable\Profile\InstalledPackages` in **Portable mode**

**Or** 

* `%APPDATA%\Keypirinha\InstalledPackages` in **Installed mode** 

Open the LaunchBox and type:
```
Ppl Call <tab> <name> [<tab-to-select-actions-or-enter-for-default>
```

```
Ppl Cell <tab> <name> [<tab-to-select-actions-or-enter-for-default>
```

```
Ppl Mail <tab> <name> [<tab-to-select-actions-or-enter-for-default>
```

```
Ppl Info <tab> <name> [<tab-to-select-actions-or-enter-for-default>
```

Note that due to Keypirinha's ability to learn from usage, in most cases it would be enough to just type the action followed by a tab, for example:
```
Call <tab> <name> [<tab-to-select-actions-or-enter-for-default>
```

## Installation and Setup ##
The easiest way to install Ppl is to use the [PackageControl](https://github.com/ueffel/Keypirinha-PackageControl) plugin's InstallPackage command. 

For manual installation simply download the cvt.keypirinha-package file from the Releases page of this repository to:

* `Keypirinha\portable\Profile\InstalledPackages` in **Portable mode**

**Or** 

* `%APPDATA%\Keypirinha\InstalledPackages` in **Installed mode** 

Ppl comes with a sample list of contacts (it is written to the user folder as sample-contacts.vcf) but to use the plugin, you'll need to export your contacts into a vCard format (a .vcf file) from Google Contacts or from another application. 

Then you need to configure the Ppl plugin and add the .vcf file to vcard_files item like in the following example (here we use google.vcf):

```
[main]
...
vcard_files =
    google.vcf
...
```

The default protocol for calling a phone number is the TEL: protocol, and the default protocol for emailing is the MAILTO: protocol. The call_protocol, cell_protocol and mail_protocol items in the Ppl configuration file can be used to select a different protocol handler. For example, to force cell calls to explicitly use Skype change the configuration as follow:

```
[main]
...
cell_protocol = skype:%s
...
```

***Advanced***
To use contacts from Microsoft Outlook which does not export multiple contacts to a .vcf file, there is a program make_contacts.py in the etc folder of the plugin which can automatically generate a contacts.json file that plugin can use. Please see that program for detailed instructions for how to use it. The process is currently a little involved and will be improved in a later version. The resulting contacts.json needs to be copied to Keypirinha's User folder.

## Future ##

There are many ideas to make Ppl better but it is very useful in its current form. Future enhancements may include:
* Support Outlook csv contacts export format 
* Support more contact entry fields
* Support shared contacts file
* ...

## Release Notes ##

**V 0.2**
- Support custom protocol handlers for calling and mailing.

**V 0.1**
- Initial release, rough around the edges.

**V 0.4.1**
- Initial public, pretty useful!
