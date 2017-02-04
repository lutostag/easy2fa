#!/usr/bin/python3

import sys
import argparse
import subprocess
import textwrap

from easy2fa.storage import AccountStorage, SHELF

RESERVED = ['generate', 'add', 'remove', 'list', 'default']
EPILOG = textwrap.dedent("""\
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
""")


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


class CLI(object):
    def __init__(self, filename=SHELF, chosen_account=None):
        self.storage = AccountStorage(filename)
        self.chosen_account = chosen_account

    def add(self):
        """Add an account"""
        name = self._get_account('New account name: ',
                                 self._ensure_new_account)
        secret = check_input('Secret: ')
        type_ = check_input("Type of Account, 'timer' or 'counter'",
                            self._ensure_type, default='counter').lower()
        self._show(self.storage.add(name, secret, type_))

    def remove(self):
        """Remove an account"""
        if not self.storage.accounts:
            print('No accounts to remove.', file=sys.stderr)
            return 1
        name = self._get_account('Account to remove: ',
                                 self._ensure_has_account)
        self.storage.remove(name)

    def default(self):
        """Set the default account"""
        if not self.storage.accounts:
            print('Please add accounts before setting a default account.',
                  file=sys.stderr)
            return 1
        name = self._get_account('Account to set as default ',
                                 self._ensure_has_account,
                                 default=self.shelf['default'])
        self.storage.default(name)

    def list(self):
        """List the accounts"""
        default = self.storage.default
        if default:
            print("Default: %s" % default)
        for account in self.storage.list:
            print(account)

    def generate(self):
        """Command to generate from an account"""
        name = self.chosen_account
        if not name:
            if self.storage.default:
                name = self.storage.default
            else:
                name = self.add()
                sys.exit(0)
        self._show(self.storage.generate(name), name)

    def _ensure_has_account(self, account):
        if account not in self.storage.accounts:
            return "Account '%s' unknown" % account

    def _ensure_new_account(self, account):
        if account in self.storage.accounts:
            return "Account '%s' already exists" % account
        if account in RESERVED:
            return "Account with name '%s' not allowed, " % account + \
                "specially reserved names are: %s" % ",".join(RESERVED)

    def _ensure_type(self, type_):
        type_ = type_.lower()
        if type_ != 'timer' and type_ != 'counter':
            return "Must either be an 'timer' or 'counter'"

    def _show(self, value, account):
        """Display the value 3 ways. Print it to stdout, copy to clipboard, and
        show a notification"""
        print(value)
        try:
            clip = subprocess.Popen(['xclip', '-i', '-selection', 'clipboard'],
                                    stdin=subprocess.PIPE)
            clip.stdin.write(value.encode('utf-8'))
            clip.stdin.close()
            subprocess.check_output(['notify-send',
                                     "easy2fa (%s): %s" % (account, value)])
        except:
            print("Unable to copy to clipboard or notify")

    def _get_account(self, *args, **kwargs):
        """Return the account given on the commandline, otherwise ask for it by
        passing given args to check_input."""
        if self.chosen_account is not None:
            return self.chosen_account
        return check_input(*args, **kwargs)


def parse_args():
    parser = argparse.ArgumentParser(
        add_help=False, prefix_chars='-garld', allow_abbrev=False,
        description='A simple two-factor auth client.', epilog=EPILOG,
        usage="easy2fa [-h] [command] [account]",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--help', help=argparse.SUPPRESS, action='help')
    parser.add_argument('-h', help=argparse.SUPPRESS, action='help')

    commands = parser.add_mutually_exclusive_group()
    for command in RESERVED:
        commands.add_argument(command, metavar=command, action='store_const',
                              const=command, dest='command',
                              help=argparse.SUPPRESS)

    opts, extra = parser.parse_known_args()
    command = 'generate'
    account = None
    if opts.command:
        command = opts.command
    if len(extra) > 1:
        parser.print_usage()
        sys.exit(2)
    elif len(extra) == 1:
        account = extra.pop()
    return (command, account)


def main():
    command, account = parse_args()
    accountStorage = AccountStorage(SHELF, chosen_account=account)
    return getattr(accountStorage, command)()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
