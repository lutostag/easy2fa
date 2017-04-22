# easy2fa <img src="https://cdn.rawgit.com/lutostag/easy2fa/b33d2821/snap/gui/easy2fa.svg" alt="" width="32" height="32">
[![Travis branch](https://img.shields.io/travis/lutostag/easy2fa/master.svg)](https://travis-ci.org/lutostag/easy2fa)
*A simple (python) wrapper around oathtool for two-factor-auth*

It copies the one-time-password to the clipboard and shows it with a notification.

## Usage
### CLI
```
$ easy2fa
usage: easy2fa [-h] [command] [account]

A simple two-factor auth client.

commands:
  (default:generate)

  generate  Generate one time password for an account
  add       Add an account
  remove    Remove an account
  list      List accounts
  default   Set default account

optional arguments:
  account          Name of account to be used with any of the above commands
                   (except 'list', for which it is ignored). If not provided,
                   will use default or fall back to asking interactively.
  -h, --help       Show this help message and exit

The accounts are stored in a yaml file located at '~/.config/easy2fa/accounts'
```

### Graphical
You can also run it with a gui using [rofi](https://davedavenport.github.io/rofi/).
Simply click on the icon after installed or run `easy2fa.gui`, here is an example screenshot:

[![screenshot](https://cdn.rawgit.com/lutostag/easy2fa/69fc05f6/docs/screenshots/graphical.png)](https://github.com/lutostag/easy2fa/tree/master/docs/screenshots)

## Install

Currently easy2fa only works on GNU/Linux, you can install either via snaps or pip.

### Snap
Follow the installation [instructions for snapd](https://snapcraft.io/docs/core/install) for your platform then simply:
```
snap install easy2fa
```

### Pip

dependencies:
```
$ sudo apt install oathtool xclip python3 python3-pip rofi
```

simply install by:
```
$ pip3 install easy2fa
```

## Notes
Secrets are stored in "~/.config/easy2fa/accounts" as a yaml file.

Released under the MIT License. Original repository @ https://github.com/lutostag/easy2fa
