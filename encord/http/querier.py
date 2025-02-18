#
# Copyright (c) 2020 Cord Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import dataclasses
import logging
from typing import TypeVar, Type, List

import requests
import requests.exceptions
from requests import Session, Timeout
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util import Retry

from encord.configs import BaseConfig
from encord.exceptions import *
from encord.http.error_utils import check_error_response
from encord.http.query_methods import QueryMethods
from encord.http.request import Request
from encord.orm.formatter import Formatter

logger = logging.getLogger(__name__)


class Querier:
    """Querier for DB get/post requests."""

    T = TypeVar("T")

    def __init__(self, config: BaseConfig):
        self._config = config

    def basic_getter(self, db_object_type: Type[T], uid=None, payload=None) -> T:
        """Single DB object getter."""
        request = self.request(QueryMethods.GET, db_object_type, uid, self._config.read_timeout, payload=payload)
        res = self.execute(request)
        if res:
            if issubclass(db_object_type, Formatter):
                return db_object_type.from_dict(res)
            elif dataclasses.is_dataclass(db_object_type):
                return db_object_type(**res)
            else:
                return db_object_type(res)
        else:
            raise ResourceNotFoundError("Resource not found.")

    def get_multiple(self, object_type: Type[T], uid=None, payload=None) -> List[T]:
        request = self.request(QueryMethods.GET, object_type, uid, self._config.read_timeout, payload=payload)
        result = self.execute(request)

        if result is not None:
            if issubclass(object_type, Formatter):
                return [object_type.from_dict(item) for item in result]
            else:
                return [object_type(**item) for item in result]
        else:
            raise ResourceNotFoundError(f"[{object_type}] not found for query with uid=[{uid}] and payload=[{payload}]")

    def basic_delete(self, db_object_type: Type[T], uid=None):
        """Single DB object getter."""
        request = self.request(
            QueryMethods.DELETE,
            db_object_type,
            uid,
            self._config.read_timeout,
        )

        return self.execute(request)

    def basic_setter(self, db_object_type: Type[T], uid, payload):
        """Single DB object setter."""
        request = self.request(
            QueryMethods.POST,
            db_object_type,
            uid,
            self._config.write_timeout,
            payload=payload,
        )

        res = self.execute(request)

        if res:
            return res
        else:
            raise RequestException("Setting %s with uid %s failed." % (db_object_type, uid))

    def basic_put(self, db_object_type, uid, payload, enable_logging=True):
        """Single DB object put request."""
        request = self.request(
            QueryMethods.PUT,
            db_object_type,
            uid,
            self._config.write_timeout,
            payload=payload,
        )

        res = self.execute(request, enable_logging)

        if res:
            return res
        else:
            raise RequestException("Setting %s with uid %s failed." % (db_object_type, uid))

    def request(self, method, db_object_type: Type[T], uid, timeout, payload=None):
        request = Request(method, db_object_type, uid, timeout, self._config.connect_timeout, payload)

        request.headers = self._config.define_headers(request.data)
        return request

    def execute(self, request, enable_logging=True):
        """Execute a request."""
        if enable_logging:
            logger.info("Request: %s", (request.data[:100] + "..") if len(request.data) > 100 else request.data)

        session = Session()
        session.mount("https://", HTTPAdapter(max_retries=Retry(connect=0)))

        req = requests.Request(
            method=request.http_method,
            url=self._config.endpoint,
            headers=request.headers,
            data=request.data,
        ).prepare()

        timeouts = (request.connect_timeout, request.timeout)

        try:
            res = session.send(req, timeout=timeouts)
        except Timeout as e:
            raise TimeOutError(str(e))
        except RequestException as e:
            raise RequestException(str(e))
        except Exception as e:
            raise UnknownException(str(e))

        try:
            res_json = res.json()
        except Exception:
            raise EncordException("Error parsing JSON response: %s" % res.text)

        if res_json.get("status") != requests.codes.ok:
            response = res_json.get("response")
            extra_payload = res_json.get("payload")
            check_error_response(response, extra_payload)

        session.close()

        return res_json.get("response")
