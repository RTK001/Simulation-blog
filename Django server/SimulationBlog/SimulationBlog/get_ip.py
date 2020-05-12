'''
Logic to get Ip address on Local
'''

from platform import system


def get_host_windows():
    from socket import gethostname, gethostbyname
    #return [gethostname(), gethostbyname(gethostname())]
    return gethostbyname(gethostname())

def get_host_linux():
    from subprocess import check_output
    ip = check_output(['hostname', '--all-ip-addresses'], universal_newlines = True)
    return ip.split(" ")[0]

ip_lookup = {'Windows': get_host_windows,
            'Linux': get_host_linux}

def get_ipv4():
    return ip_lookup[system()]()
