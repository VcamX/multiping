
import logging

import message_pb2
import utils


class MessageServicer(message_pb2.BetaCommunicationServicer):

    def Platform(self, request, context):
        logging.debug('Receiving PlatformRequest')
        info = utils.platform_info()
        logging.debug('Sending PlatformReply')
        return message_pb2.PlatformReply(**info)
