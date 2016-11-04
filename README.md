A simple (bash) wrapper around oathtool for two-factor-auth:

It copies the one-time-password to the clipboard and shows it with a notification.

dependencies:
```
sudo apt install oathtool xclip
```

simply install by:
```
sudo cp easy2fa /usr/local/bin
```

Settings are stored in "~/.config/easy2fa/", there two files hold the counter and secret respectively.

Released under the MIT License. Original repository @ https://github.com/lutostag/easy2fa
