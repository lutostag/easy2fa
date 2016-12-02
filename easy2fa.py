#!/usr/bin/python3

import os
import sys
import argparse
import shelve

SHELF = '~/.config/easy2fa/accounts'
RESERVED = ['list', 'add', 'remove', 'default']


def check_input(prompt, assertion, fail_text, default=None):
    if default is not None:
        prompt += " [default=%s]: "

    while True:
        value = input(prompt).strip()
        if value == "" and default is not None:
            value = default
            
        if assertion(value):
            return value

        print(('\tInvalid input: ' + abort_text).format(value))


class AccountStorage(object):
    def __init__(self, filename):
        self.filename = filename
        self.safety_check()
        with open(filename, 'r') as fd:
            self.shelf = yaml.load(fd)
        self.accounts = self.shelf['accounts']

    def safety_check(self):
        if os.path.isfile(self.filename):
            dirname = os.path.dirname(self.filename)
            try:
                assert(os.stat(self.filename).st_uid == os.geteuid())
                assert(os.stat(self.filename).st_gid == os.getegid())
                assert(os.stat(self.filename).st_mode == 0o100600)
                assert(os.stat(self.dirname).st_uid == os.geteuid())
                assert(os.stat(self.dirname).st_gid == os.getegid())
                assert(os.stat(self.dirname).st_mode == 0o040755)
                #TODO: extend checks to be more discerning
            except AssertionError:
                print("Aborting: Safety checks not met for %s" % self.filename)
                raise
        else:
            pass #create

    def ensure_account(prompt, account):
        if not account:
            self.list()
            account = input(prompt)
        if account not in accounts:
            print('Aborting: Account "%s" unknown' % account)
            sys.exit(1)

    def add(self, name=None):
        if not name:
            name = input('New account name: ')
        if name in self.accounts:
            print('Aborting: Account with that name already exists')
            sys.exit(1)
        if name in RESERVED:
            print('Aborting: Account with name "%s" not allowed' % name)
            print('Specially reserved names are: %s' % ",".join(RESERVED))
            sys.exit(1)
        secret = input('Secret: ')
        counter = input('Counter, if time based enter "time" (default=0): ')
        if counter == '':
            counter = 0
        elif counter != 'time':
            try:
                counter = int(counter)
            except ValueError:
                print('Aborting: Invalid input %s' % time)
                sys.exit(1)
        
        if 'default' not in self.shelf:
            self.shelf['default'] = name
        self.accounts[name] = (secret, counter)
        self.generate(name)

    def default(self, name=None):
        name = ensure_account('Account to set as default: ', name)
        self.shelf['default'] = name

    def remove(self, name=None):
        name = ensure_account('Account to remove: ', name)
        if self.shelf['default'] == name:
            if len(accounts) >= 1:
                self.shelf['default'] = sorted(accounts.keys())[0]
            else:
                del self.shelf['default']
        del account[name]

    def list(self):
        print("Default: %s" % self.shelf['default'])
        print("\n".join(sorted(self.accounts.keys())))

    def _generate(self, name):
        secret, counter = self.accounts[name]
        opts = "--counter=%s" % str(counter)
        if counter == 'time':
            opts = '--totp'
        else:
            counter += 1
        try:
            otp = subprocess.check_output(['oathtool', opts, secret])
        except:
            print("Unable to create one time password")
            raise

        try:
            clip = subprocess.Popen(['xclip', '-f', '-selection', 'clipboard'],
                                    stdin=subprocess.PIPE)
            clip.stdin.write(otp)
            clip.stdin.close()
            otp = subprocess.check_output(
                ['notify-send', "One time password on clipboard: %s" % otp])
        except:
            print("Unable to copy to clipboard or notify")

        self.accounts[name] = secret, counter

    def generate(self, name=None):
        if not name:
            if 'default' in self.shelf:
                name = self.shelf['default']
            else:
                name = self.add()
                sys.exit(0)
        self._generate(name)

    def save_shelf():
        with open(self.filename, 'w') as fd:
            yaml.dump(self.shelf, fd)


def parse_args():
    parser = argparse.ArgumentParser()
    default.add_argument('account', nargs='?', help='name of account')
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')
    add = subparsers.add_parser('add', help='Add an account')
    remove = subparsers.add_parser('remove', help='Remove an account')
    list_ = subparsers.add_parser('list', help='List accounts ')
    default = subparsers.add_parser('default', help='Set default account')
    return parser.parse_args()


def main():
    opts = parse_args()
    command = 'generate'
    if opts.command:
        command = opts.command
    accountstorage =  AccountStorage(SHELF)
    getattr(accountstorage, command)(name=opts.account)
    accountstorage.save_shelf()

if __name__ == '__main__':
    sys.exit(main())
