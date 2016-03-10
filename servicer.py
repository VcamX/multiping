
import logging

import message_pb2
import ping
import utils


def ping_reply_type_string(r_type):
    return {
        message_pb2.PingReply.UNKNOWN: 'Unknown',
        message_pb2.PingReply.OK: 'OK',
        message_pb2.PingReply.INVALID_ARGS: 'Invalid Arguments',
        message_pb2.PingReply.NOT_RESPONDING: 'Not Responding',
        message_pb2.PingReply.UNRESOLVABLE: 'Unresolvable',
    }[r_type]


class MessageServicer(message_pb2.BetaCommunicationServicer):

    def Platform(self, request, context):
        logging.debug('Receiving PlatformRequest')
        info = utils.platform_info()
        logging.debug('Sending PlatformReply')
        return message_pb2.PlatformReply(**info)

    def Ping(self, request, context):
        ping_reply = ping.ping(request.host, request.count, request.timeout)
        return message_pb2.PingReply(**ping_reply)
