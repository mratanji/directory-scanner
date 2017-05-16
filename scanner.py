'''
Scans directories and will output unix commands for creating them, keeping permissions and ownership
'''
import os
import sys
import stat
import pwd
import grp

USAGE = '''
USAGE:
    python scanner.py [PATH TO FOLDER] [OUTPUT FILE]

Will scan through folders, starting with [PATH TO FOLDER], and generate 
linux commands to create copies of those directories. The user, group,
and permission bits will be created.
'''

def validate_input():
    '''Validate the proper number of arguments is provided'''
    if len(sys.argv) != 3:
        print USAGE
        exit(1)
    return sys.argv[1:]


def check_path(path):
    '''Check if a path is valid'''
    if not os.path.exists(path):
        print 'Error - path not valid'
        exit(1)


def start(path):
    '''Iterate through path recursively and generate creation commands'''
    all_commands = []
    for root, subdirs, files in os.walk(path, followlinks=True):
        all_commands.extend(get_creation_commands(root))
    return all_commands



def get_creation_commands(path):
    '''Generate list of commands to create path'''
    path = os.path.realpath(path)
    commands = []
    commands.append('mkdir -p ' + path)
    commands.append('chown -R ' + get_owner(path) + ':' + get_group(path) + ' ' + path)
    commands.append('chmod ' + get_permissions_octal(path) + ' ' + path)
    return commands


def get_owner(path):
    '''Get the username for the owner of path'''
    stat_info = os.stat(path)
    uid = stat_info.st_uid
    username = pwd.getpwuid(uid).pw_name
    return username


def get_group(path):
    '''Get the group name for the owner of path'''
    stat_info = os.stat(path)
    gid = stat_info.st_gid
    group = grp.getgrgid(gid).gr_name
    return group


def get_permissions_octal(path):
    '''Get permission in binary (FOGE)'''
    all_permission_bits = oct(stat.S_IMODE(os.stat(path).st_mode))
    return all_permission_bits


def generate_script(all_commands, outfile):
    '''Write commands to outfile'''
    outfile = os.path.normpath(os.path.realpath(os.path.expandvars(outfile)))
    with open(outfile, 'w') as final_file:
        for command in all_commands:
            final_file.write(command + '\n')


def process():
    '''Record permission info about path'''
    path, outfile = validate_input()
    check_path(path)
    all_commands = start(path)
    generate_script(all_commands, outfile)


process()
