A simple (python) wrapper around oathtool for two-factor-auth:

It copies the one-time-password to the clipboard and shows it with a notification.

dependencies:
```
sudo apt install oathtool xclip python3
```

simply install by:
```
sudo cp easy2fa/__init__.py /usr/local/bin/easy2fa
```

Secrets are stored in "~/.config/easy2fa/accounts" as a yaml file.

Released under the MIT License. Original repository @ https://github.com/lutostag/easy2fa
