Keypirinha Plugin: Ppl
=========
# A universal unit converter for the Keypirinha launcher

This plugin for Keypirinha help calling and emailing people.


## Usage ##
Make sure to install Keypirinha from http://keypirinha.com/

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

## Installation ##

The easiest way to install Ppl is to use the [PackageControl](https://github.com/ueffel/Keypirinha-PackageControl) plugin's InstallPackage command. For manual installation simply download the ppl.keypirinha-package file from the Releases page of this repository to the Keypirinha\portable\Profile\InstalledPackages folder.

Before using the plugin, you need to generate the contacts.json file - this is done automatically by the etc\make_contacts.py program. Please see that program for detailed instructions for how to use it. The process is a little involved because it currently cannot be done from Keypirinha. A contacts.json-sample is provided in the etc folder of this repository - it can be copied to the Keypirinha's User folder as contacts.json to see how it works.

## Credits ##

* TBD

## Release Notes ##

**V 0.1**
- Initial release, rough around the edges.
