import re


def ipv4(address):
    if re.fullmatch(
            r'(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3}'
            r'([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])'
            r'', address):
        return True
    else:
        return False


def ipv6(address):
    if re.fullmatch(
            r'(([0-9aA-fF]{1,4}:){7}[0-9aA-fF]{1,4}|'
            r'([0-9aA-fF]{1,4}:){7}:|'
            r'([0-9aA-fF]{1,4}:){1,6}:[0-9aA-fF]{1,4}|'
            r'([0-9aA-fF]{1,4}:){1,5}(:[0-9aA-fF]{1,4}){1,2}|'
            r'([0-9aA-fF]{1,4}:){1,4}(:[0-9aA-fF]{1,4}){1,3}|'
            r'([0-9aA-fF]{1,4}:){1,3}(:[0-9aA-fF]{1,4}){1,4}|'
            r'([0-9aA-fF]{1,4}:){1,2}(:[0-9aA-fF]{1,4}){1,5}|'
            r'[0-9aA-fF]{1,4}:((:[0-9aA-fF]{1,4}){1,6})|'
            r':((:[0-9aA-fF]{1,4}){1,7}|:)|'
            r'fe80:(:[0-9aA-fF]{0,4}){0,4}%[0-9aA-zZ]+|::(ffff(:0{1,4})?:))'
            r'', address):
        return True
    else:
        return False


def macaddress(address):
    if '.' in address:
        if re.fullmatch(
                r'(('
                r'([0-9aA-fF]){4}|'
                r'([0-9aA-fF]){3}([aA-fF0-9])|'
                r'(([aA-fF0-9])([aA-fF0-9]){3})|'
                r'((([0-9][aA-fF])|([aA-fF0-9])){2})|'
                r'(([aA-fF0-9])([aA-fF0-9]){2}([aA-fF0-9])))\.){2}'
                r'(([0-9aA-fF]){4})|'
                r'(([0-9aA-fF]){3}([aA-fF0-9]))|'
                r'(([aA-fF0-9])([aA-fF0-9]){3})|'
                r'((([0-9][aA-fF])|([aA-fF][0-9])){2})|'
                r'(([aA-fF0-9])([aA-fF0-9]){2}([aA-fF0-9]))'
                r'', address):
            return True
        else:
            return False
    else:
        if re.fullmatch(
                r'(((([0-9aA-fF]){2}-){5}|'
                r'(([0-9][aA-fF]|[aA-fF][0-9])-){5})'
                r'(([0-9aA-fF]){2}|([0-9][aA-fF]|[aA-fF][0-9]){2}))|'
                r'(((([0-9aA-fF]){2}:){5}|'
                r'(([0-9][aA-fF]|[aA-Ff][0-9]):){5})'
                r'(([0-9aA-fF]){2}|([0-9][aA-fF]|[aA-fF][0-9]){2}))'
                r'', address):
            return True
        else:
            return False
