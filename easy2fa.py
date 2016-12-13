#!/usr/bin/python3

import os
import sys
import argparse
import subprocess
import yaml

SHELF = os.path.expanduser('~/.config/easy2fa/accounts')
RESERVED = ['list', 'add', 'remove', 'default', 'generate']


def check_input(prompt, assertion=None, default=None):
    """Get input from cmdline, ensuring that it passes the given assertion.
    
    assertion: a function that if given a value will return None if the check
    should pass, otherwise returning a helpful error message as a string."""
    if default is not None:
        prompt += " [default=%s]: " % str(default)

    while True:
        value = input(prompt).strip()
        if value == "" and default is not None:
            value = default
            
        if assertion is not None:
            check = assertion(value)
            if check is not None:
                error_msg = '\tInvalid input'
                if not isinstance(check, bool):
                    error_msg += ': ' + str(check)
                print(error_msg)
                continue
        return value


class AccountStorage(object):
    def __init__(self, filename):
        self.filename = filename
        self._safety_check()
        self.shelf = None
        self.accounts = None
        self.chosen_account = None
        self._load()

    def add(self):
        name = self._get_account('New account name: ',
                                 self._ensure_new_account)
        secret = check_input('Secret: ')
        type_ = check_input("Type of Account, 'timer' or 'counter'",
                              self._ensure_type, default='counter').lower()
        if type_ != 'timer':
            # start the counter at zero
            type_ = 0
        self.accounts[name] = (secret, type_)
        self._update_default()
        self._generate(name)
        self._save_shelf()

    def remove(self):
        name = self._get_account('Account to remove: ',
                                 self._ensure_has_account)
        del self.accounts[name]
        self._update_default()
        self._save_shelf()

    def default(self):
        if not self.accounts:
            print('Please add accounts before setting a default account.')
            return 1
        account = self._get_account('Account to set as default: ',
                                    self._ensure_has_account)
        self.shelf['default'] = account
        self._save_shelf()

    def list(self):
        if 'default' in self.shelf:
            print("Default: %s" % self.shelf['default'])
        for account in sorted(self.accounts.keys()):
            print(account)
    
    def generate(self):
        name = self.chosen_account
        if not name:
            if 'default' in self.shelf:
                name = self.shelf['default']
            else:
                name = self.add()
                sys.exit(0)
        self._generate(name)
        self._save_shelf()

    def _generate(self, name):
        secret, type_ = self.accounts[name]
        opts = '--totp'
        if type_ != 'timer':
            opts = "--counter=%s" % str(type_)
            type_ += 1
        try:
            otp = subprocess.check_output(
                ['oathtool', '-b', opts, secret]).decode().strip()
        except:
            print("Unable to create one time password")
            raise
        self._show(otp)
        self.accounts[name] = secret, type_
    
    def _update_default(self, account=None):
        if self.shelf.get('default') in self.accounts:
            return
        if 'default' in self.shelf and not self.accounts:
            del self.shelf['default']
            return
        self.shelf['default'] = sorted(self.accounts.keys())[0]

    def _ensure_has_account(self, account):
        if account not in self.accounts:
            return "Account '%s' unknown" % account

    def _ensure_new_account(self, account):
        if account in self.accounts:
            return "Account '%s' already exists" % account
        if account in RESERVED:
            return "Account with name '%s' not allowed, " % account + \
                "specially reserved names are: %s" % ",".join(RESERVED)

    def _ensure_type(self, type_):
        type_ = type_.lower()
        if type_ != 'timer' and type_ != 'counter':
            return "Must either be an 'timer' or 'counter'"

    def _show(self, value, clipboard=False):
        print(value)
        try:
            clip = subprocess.Popen(['xclip', '-i', '-selection', 'clipboard'],
                                    stdin=subprocess.PIPE)
            clip.stdin.write(value.encode('utf-8'))
            clip.stdin.close()
            subprocess.check_output(['notify-send',
                                     "On clipboard: %s" % value])
        except:
            print("Unable to copy to clipboard or notify")

    def _get_account(self, *args, **kwargs):
        """Return the account given on the commandline, otherwise ask for it by
        passing given args to check_input."""
        if self.chosen_account is not None:
            return self.chosen_account
        return check_input(*args, **kwargs)

    def _save_shelf(self):
        with open(self.filename, 'w') as fd:
            yaml.dump(self.shelf, fd)
    
    def _safety_check(self):
        dirname = os.path.dirname(self.filename)
        if os.path.isfile(self.filename):
            try:
                assert(os.stat(self.filename).st_uid == os.geteuid())
                assert(os.stat(self.filename).st_gid == os.getegid())
                assert(os.stat(self.filename).st_mode == 0o100600)
                assert(os.stat(dirname).st_uid == os.geteuid())
                assert(os.stat(dirname).st_gid == os.getegid())
                assert(os.stat(dirname).st_mode == 0o040755)
                #TODO: extend checks to be more discerning
            except AssertionError:
                print("Aborting: Safety checks not met for %s" % self.filename)
                raise
        else:
            try:
                os.makedirs(dirname, 0o755)
            except:
                pass
            os.open(self.filename, os.O_WRONLY | os.O_CREAT, 0o600)

    def _load(self):
        with open(self.filename, 'r') as fd:
            self.shelf = yaml.load(fd)
        if self.shelf is None:
            self.shelf = {'accounts': {}}
        assert(isinstance(self.shelf, dict))
        assert('accounts' in self.shelf)
        self.accounts = self.shelf['accounts']
        assert(isinstance(self.accounts, dict))
        try:
            for account, info in self.accounts.items():
                assert(isinstance(account, str))
                assert(len(info) == 2)
                assert(info[1] == 'timer' or isinstance(info[1], int))
        except AssertionError:
            print("Aborting: Format checks not met for %s" % self.filename)
            raise


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('account', nargs='?', help='name of account')
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')
    add = subparsers.add_parser('add', help='Add an account')
    remove = subparsers.add_parser('remove', help='Remove an account')
    list_ = subparsers.add_parser('list', help='List accounts ')
    default = subparsers.add_parser('default', help='Set default account')
    generate = subparsers.add_parser('generate',
                                     help='Generate otp for account')
    return parser.parse_args()


def main():
    opts = parse_args()
    command = 'generate'
    if opts.command:
        command = opts.command
    accountstorage = AccountStorage(SHELF)
    accountstorage.chosen_account = opts.account
    return getattr(accountstorage, command)()


if __name__ == '__main__':
    sys.exit(main())
