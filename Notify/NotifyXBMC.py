# -*- encoding: utf-8 -*-
#
# XBMC Notify Wrapper
#
# Copyright (C) 2014 Chris Caron <lead2gold@gmail.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

from NotifyBase import NotifyBase
from json import dumps as to_json

import requests

# XBMC uses the http protocol with JSON requests
XBMC_PORT = 8080

XBMC_ERROR_MAP = {
    400: 'Bad Request; Unsupported Parameters',
    401: 'Verification Failed',
    500: 'Internal server error.',
}

class NotifyXBMC(NotifyBase):
    """
    A wrapper for XBMC Notifications
    """
    def __init__(self, **kwargs):

        super(NotifyXBMC, self).__init__(**kwargs)

        if self.secure:
            self.schema = 'https'
        else:
            self.schema = 'http'

        if not self.port:
            self.port = XBMC_PORT

        return

    def notify(self, title, body, **kwargs):
        """
        Perform XBMC Notification
        """

        # prepare JSON Object
        payload = {
            'jsonrpc': '2.0',
            'method': 'GUI.ShowNotification',
            'params': {
                'title': title,
                'message': body,
                # displaytime is defined in microseconds
                'displaytime': 12000,
            },
            'id': 1,
        }

        headers = {'content-type': 'application/json'}

        auth = None
        if self.user:
            auth = (self.user, self.password)

        url = '%s://%s' % (self.schema, self.host)
        if isinstance(self.port, int):
            url += ':%d' % self.port

        url += '/jsonrpc'

        try:
            self.logger.debug('XBMC POST URL: %s' % url)
            r = requests.post(
                url,
                data=to_json(payload),
                headers=headers,
                auth=auth,
            )
            if r.status_code != 200:
                try:
                    error_msg = XBMC_ERROR_MAP[r.status_code]
                except IndexError:
                    error_msg = 'Failed to send XBMC notification'

                self.logger.error('%s (error=%s)' % (
                        error_msg,
                        r.status_code,
                ))

                self.logger.debug(
                    'XBMC Server returned error %s' % str(r.raw))
                return False

        except requests.ConnectionError as e:
            self.logger.error(
                'A Connection error occured sending XBMC ' + \
                'notification to %s.' %
                    self.host,
            )
            self.logger.debug('Socket Exception: %s' % str(e))
            return False

        return True
