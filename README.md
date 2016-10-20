A simple (bash) wrapper around oathtool for two-factor-auth:

It copies the one-time-password to the clipboard and shows it with a notification.

dependencies:
```
sudo apt install oathtool xclip
```

simply install by:
```
sudo cp otp /usr/local/bin
```

Settings are stored in "~/.config/otp/", there two files hold the counter and secret respectively.

Released under the MIT License. Original repository @ https://github.com/lutostag/otp
