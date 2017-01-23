A simple (python) wrapper around oathtool for two-factor-auth:

It copies the one-time-password to the clipboard and shows it with a notification.

dependencies:
```
sudo apt install oathtool xclip python3 python3-pip
```

simply install by:
```
pip3 install easy2fa
```

Secrets are stored in "~/.config/easy2fa/accounts" as a yaml file.

Released under the MIT License. Original repository @ https://github.com/lutostag/easy2fa
