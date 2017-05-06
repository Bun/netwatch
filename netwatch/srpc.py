from socket import create_connection, socket, AF_UNIX
from json import dumps


def _create_connection(remote):
    if isinstance(remote, tuple):
        return create_connection(remote)

    s = socket(AF_UNIX)
    s.connect(remote)
    return s

def make_frame(message):
    packet = dumps(message)
    frame_uc = '%04u:%s' % (len(packet), packet)
    return frame_uc.encode('utf8')


class Client(object):
    def __init__(self, remote):
        self.con = _create_connection(remote)

    def send(self, message):
        self.con.sendall(make_frame(message))

    def close(self):
        self.con.close()
