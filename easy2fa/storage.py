#!/usr/bin/python3

import os
import subprocess
import yaml

SHELF = os.path.expanduser('~/.config/easy2fa/accounts')
TYPES = ['counter', 'timer']


class AccountStorage(object):
    def __init__(self, filename=SHELF):
        self.filename = filename
        self._safety_check()
        self.shelf = None
        self.accounts = None
        self._load()

    @property
    def list(self):
        return sorted(self.accounts.keys())

    @property
    def default(self):
        return self.shelf.get('default')

    @default.setter
    def default(self, name):
        assert(name in self.accounts)
        self.shelf['default'] = name
        self._save_shelf()

    def add(self, name, secret, type_):
        assert(name not in self.accounts)
        assert(type_ in TYPES)
        if type_ != 'timer':
            # start the counter at zero
            type_ = 0
        self.accounts[name] = (secret, type_)
        self._update_default()
        self._save_shelf()

    def remove(self, name):
        assert(name in self.accounts)
        del self.accounts[name]
        self._update_default()
        self._save_shelf()

    def generate(self, name):
        assert(name in self.accounts)
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
        self.accounts[name] = secret, type_
        self._save_shelf()
        return otp

    def _update_default(self, account=None):
        if self.shelf.get('default') in self.accounts:
            return
        if 'default' in self.shelf and not self.accounts:
            del self.shelf['default']
            return
        self.shelf['default'] = sorted(self.accounts.keys())[0]

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
                # TODO: extend checks to be more discerning
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
