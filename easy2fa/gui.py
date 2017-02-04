#!/usr/bin/python3

import sys
import subprocess
import shlex
from subprocess import PIPE

from easy2fa.storage import SHELF, AccountStorage
from easy2fa.cli import CLI

COMMANDS = """  add       Add an account
  remove    Remove an account
  default   Set default account
"""


def create_prompt(text):
    return '<span weight="bold">easy2fa:</span><span style="italic">' + \
           '%s</span>' % text

def alert(text):
    run_with_input(['rofi', '-e', 'easy2fa: %s' % text])
    sys.exit(1)


def run_with_input(command, input_=''):
    proc = subprocess.Popen(command, stdin=PIPE, stdout=PIPE)
    value, _ = proc.communicate(input=input_.encode('utf-8'))
    if proc.returncode != 0:
        sys.exit(0)
    return value.decode().strip()


def choose(prompt, choices, default=None):
    """Get an selection from a given set of choices"""
    end = ""
    if default is not None:
        row = choices.index(default)
        end = ' -selected-row %s' % (row)
    cmd = 'rofi -dmenu -no-custom -format i -p ""' + end
    output = run_with_input(shlex.split(cmd) + ['-mesg', prompt],
                            '\n'.join(choices))
    if output:
        return choices[int(output)]
    return None


def check_input(prompt, assertion=None):
    """Get input from rofi, ensuring that it passes the given assertion.

    assertion: a function that if given a value will return None if the check
    should pass, otherwise returning a helpful error message as a string."""
    args = "-dmenu -mesg '' -l -1 -fixed-num-lines -hide-scrollbar -i -bw 0 -p"
    error_msg = ""

    while True:
        if error_msg:
            prompt = error_msg
        value = run_with_input(shlex.split('rofi ' + args) + [prompt])

        if assertion is not None:
            check = assertion(value)
            if check is not None:
                error_msg = 'Invalid input'
                if not isinstance(check, bool):
                    error_msg += ': ' + str(check)
                print(error_msg)
                continue
        return value


class GUI(CLI):
    def start(self):
        """Get the command or account to generate otp for."""
        accounts = self.storage.list
        default = self.storage.default
        commands = ['add', 'remove', 'default']
        end = ""
        if default is not None:
            row = accounts.index(default)
            end = ' -selected-row %s' % (row + len(commands))
        cmd = 'rofi -dmenu -no-custom -format i -u 0-2 -p ""' + end
        prompt = create_prompt('Select account to generate or command')
        output = run_with_input(shlex.split(cmd) + ['-mesg', prompt],
                                COMMANDS + '\n'.join(accounts))
        if not output:
            sys.exit(0)
        choice = int(output)
        if choice >= len(commands):
            self.generate(accounts[choice - len(commands)])
        else:
            getattr(self, commands[choice])()

    def generate(self, account):
        self._show(self.storage.generate(account), account)

    def add(self):
        name = check_input('New account name: ',
                           assertion=self._ensure_new_account)

        secret = check_input('Secret: ')

        type_ = choose(create_prompt('Type of account, "counter" or "timer"'),
                       ['counter', 'timer'], default='timer')
        self.storage.add(name, secret, type_)
        self.generate(name)

    def remove(self):
        if not self.storage.accounts:
            alert('No accounts to remove.')

        choice = choose(create_prompt('Select account to remove'),
                        choices=self.storage.list, default=self.storage.default)
        self.storage.remove(choice)

    def default(self):
        if not self.storage.accounts:
            alert('Please add accounts before setting a default account.')

        choice = choose(create_prompt('Select account to set as default'),
                        choices=self.storage.list, default=self.storage.default)
        self.storage.default = choice


def main():
    GUI(filename=SHELF).start()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
