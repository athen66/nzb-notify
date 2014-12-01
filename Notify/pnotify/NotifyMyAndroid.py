# -*- encoding: utf-8 -*-
#
# Notify My Android Notify Wrapper
#
# Copyright (C) 2014 Chris Caron <lead2gold@gmail.com>
#
# This file is part of NZBGet-Notify.
#
# NZBGet-Notify is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NZBGet-Notify is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NZBGet-Notify. If not, see <http://www.gnu.org/licenses/>.

from json import dumps
import requests
import re

from NotifyBase import NotifyBase
from NotifyBase import NotifyFormat
from NotifyBase import HTTP_ERROR_MAP

# Notify My Android uses the http protocol with JSON requests
NMA_URL = 'https://www.notifymyandroid.com/publicapi/notify/publicapi/notify'

# Extend HTTP Error Messages
NMA_HTTP_ERROR_MAP = dict(HTTP_ERROR_MAP.items() + {
    400: 'Data is wrong format, invalid length or null.',
    401: 'API Key provided is invalid',
    402: 'Maximum number of API calls per hour reached.',
}.items())

# Used to validate Authorization Token
VALIDATE_APIKEY = re.compile(r'[A-Za-z0-9]{48}')

# Priorities
class NotifyMyAndroidPriority(object):
    VERY_LOW = -2
    MODERATE = -1
    NORMAL = 0
    HIGH = 1
    EMERGENCY = 2

NMA_PRIORITIES = (
    NotifyMyAndroidPriority.VERY_LOW,
    NotifyMyAndroidPriority.MODERATE,
    NotifyMyAndroidPriority.NORMAL,
    NotifyMyAndroidPriority.HIGH,
    NotifyMyAndroidPriority.EMERGENCY,
)

class NotifyMyAndroid(NotifyBase):
    """
    A wrapper for Notify My Android Notifications
    """
    def __init__(self, apikey, priority=NotifyMyAndroidPriority.NORMAL,
                 devapikey=None, **kwargs):
        """
        Initialize Notify My Android Object
        """
        super(NotifyMyAndroid, self).__init__(
            title_maxlen=1000, body_maxlen=10000,
            notify_format=NotifyFormat.TEXT,
            **kwargs)

        # The Priority of the message
        if priority not in NMA_PRIORITIES:
            self.priority = NotifyMyAndroid.NORMAL
        else:
            self.priority = priority

        # Validate apikey
        if not VALIDATE_APIKEY.match(apikey):
            self.logger.warning(
                'Invalid Notify My Android API Key specified.'
            )
            raise TypeError(
                'Invalid Notify My Android API Key specified.'
            )
        self.apikey = apikey

        if devapikey:
            # Validate apikey
            if not VALIDATE_APIKEY.match(devapikey):
                self.logger.warning(
                    'Invalid Notify My Android DEV API Key specified.'
                )
                raise TypeError(
                    'Invalid Notify My Android DEV API Key specified.'
                )
        self.devapikey = devapikey


    def _notify(self, title, body, notify_type, **kwargs):
        """
        Perform Notify My Android Notification
        """

        headers = {
            'User-Agent': self.app_id,
            'Content-Type': 'application/json'
        }

        # prepare JSON Object
        payload = {
            'apikey': self.apikey,
            'application': self.app_id,
            'event': title,
            'description': body,
            'priority': self.priority,
        }

        if self.devapikey:
            payload['developerkey'] = self.devapikey

        self.logger.debug('Notify My Android POST URL: %s' % NMA_URL)
        try:
            r = requests.post(
                NMA_URL,
                data=dumps(payload),
                headers=headers,
            )
            if r.status_code != requests.codes.ok:
                # We had a problem
                try:
                    self.logger.warning(
                        'Failed to send Notify My Android notification: ' +\
                        '%s (error=%s).' % (
                            NMA_HTTP_ERROR_MAP[r.status_code],
                            r.status_code,
                    ))
                except IndexError:
                    self.logger.warning(
                        'Failed to send Notify My Android notification ' +\
                        '(error=%s).' % (
                            r.status_code,
                    ))

                # Return; we're done
                return False
            else:
                self.logger.info('Sent Notify My Android notification.')

        except requests.ConnectionError as e:
            self.logger.warning(
                'A Connection error occured sending Notify My Android ' + \
                'notification.'
            )
            self.logger.debug('Socket Exception: %s' % str(e))

            # Return; we're done
            return False

        return True
