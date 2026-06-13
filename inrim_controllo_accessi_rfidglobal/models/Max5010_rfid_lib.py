import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
import pytz

logger = logging.getLogger(__name__)

DEFAULT_TIMEZONE_CONFIG = "1000000000000000"
DEFAULT_TZ_NAME = "UTC"
EVENTS_STATUS_EMPTY = 146
EVENTS_STATUS_OK = 148
REQUEST_TIMEOUT_SECONDS = 10.0


@dataclass
class Tag:
    idd: str = ""
    timezoneConfig: str = DEFAULT_TIMEZONE_CONFIG


@dataclass
class TimeZoneTableItem:
    dateStart: datetime = field(default_factory=datetime.now)
    dateEnd: datetime = field(default_factory=datetime.now)
    days: int = 255
    hoursStart: str = "00:00"
    hoursEnd: str = "23:59"


@dataclass
class AddTagsBody:
    tags: list[Tag] = field(default_factory=list)
    timeZoneTable: list[TimeZoneTableItem] = field(default_factory=list)


@dataclass
class EventRecord:
    idd: str = ""
    eventDateTime: str = ""
    errorCode: str = ""
    accessAllowed: bool = False
    digitalInput: list[bool] = field(default_factory=list)
    tz: str = DEFAULT_TZ_NAME

    def _get_tzinfo(self):
        return pytz.timezone(self.tz or DEFAULT_TZ_NAME)

    def _get_event_datetime(self) -> datetime:
        return datetime.fromisoformat(self.eventDateTime)

    def eventDateTime_to_utc(self) -> datetime:
        loc = self._get_tzinfo().localize(self._get_event_datetime())
        return loc.astimezone(pytz.UTC).replace(tzinfo=None)

    def eventDateTime_to_utc_isoformat(self) -> str:
        return self.eventDateTime_to_utc().isoformat()

    def eventDateTime_to_tz(self) -> datetime:
        dt_utc = pytz.UTC.localize(self.eventDateTime_to_utc())
        return dt_utc.astimezone(self._get_tzinfo()).replace(tzinfo=None)

    def eventDateTime_to_tz_isoformat(self) -> str:
        return self.eventDateTime_to_tz().isoformat()


@dataclass
class EventsResponse:
    status: int = 0
    statusStr: str = ""
    layoutIdd: bool = False
    layoutTimeStamp: bool = False
    layoutEventStatus: bool = False
    layoutInput: bool = False
    dataSetsLenght: int = 0
    hasMore: bool = False
    layout: list[bool] = field(default_factory=list)
    eventRecords: list[EventRecord] = field(default_factory=list)

    def is_error(self) -> bool:
        return self.status == -2

    def is_ok(self) -> bool:
        return self.status == EVENTS_STATUS_OK

    @classmethod
    def from_dict(cls, data: dict[str, Any], tz: str) -> "EventsResponse":
        payload = dict(data or {})
        event_records = payload.pop("eventRecords", [])
        return cls(
            eventRecords=[
                EventRecord(**{**record, "tz": tz})
                for record in event_records
            ],
            **payload,
        )


@dataclass
class DeviceInfo:
    deviceId: str = ""
    readerType: str = ""
    mode: str = ""
    modeCode: str = ""


@dataclass
class DeviceDiagnostic:
    event_tab_size: int = 0
    event_cnt: int = 0
    systemClock: str | None = None


@dataclass
class Device:
    status: bool = False
    diagnostic: DeviceDiagnostic = field(default_factory=DeviceDiagnostic)
    info: DeviceInfo = field(default_factory=DeviceInfo)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Device":
        payload = dict(data or {})
        return cls(
            status=payload.get("status", False),
            diagnostic=DeviceDiagnostic(**(payload.get("diagnostic") or {})),
            info=DeviceInfo(**(payload.get("info") or {})),
        )


@dataclass
class ActionResponse:
    status: bool = False
    diagnostic: DeviceDiagnostic = field(default_factory=DeviceDiagnostic)
    result: bool = False
    message: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ActionResponse":
        payload = dict(data or {})
        return cls(
            status=payload.get("status", False),
            diagnostic=DeviceDiagnostic(**(payload.get("diagnostic") or {})),
            result=payload.get("result", False),
            message=payload.get("message", ""),
        )


class Max5010RfidClient:
    def __init__(
            self, device_ip, base_url, header_auth_key, header_auth_value, tz,
            reader_id=None, reader_name="", access_point_id=None,
            access_point_name=""):
        self.device_ip = device_ip
        self.base_url = base_url.rstrip("/")
        self.headers = {header_auth_key: header_auth_value}
        self.reader_id = reader_id
        self.reader_name = reader_name or ""
        self.access_point_id = access_point_id
        self.access_point_name = access_point_name or ""
        self.online = False
        self.connection_error = False
        self.connction_error = False
        self.response_error = False
        self.timeout = httpx.Timeout(REQUEST_TIMEOUT_SECONDS)
        self.device: Device = Device()
        self._tz_name = self._normalize_tz_name(tz)
        self.tz = pytz.timezone(self._tz_name)

    @staticmethod
    def _normalize_tz_name(tz: Any) -> str:
        if isinstance(tz, str):
            return tz or DEFAULT_TZ_NAME
        zone = getattr(tz, "zone", None)
        if zone:
            return zone
        return DEFAULT_TZ_NAME

    def _build_url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    @staticmethod
    def _endpoint_from_url(url: str) -> str:
        parsed = urlparse(url)
        return parsed.path or url

    @staticmethod
    def _quote_log_value(value: Any) -> str:
        if value is None:
            return "-"
        text = str(value).replace('"', "'").strip()
        if not text:
            return "-"
        if re.search(r"\s", text):
            return f'"{text}"'
        return text

    @staticmethod
    def _classify_http_error(exc: httpx.HTTPError) -> str:
        error_text = str(exc).lower()
        if (
                "name or service not known" in error_text
                or "temporary failure in name resolution" in error_text
                or "gaierror" in error_text):
            return "DNS"
        if isinstance(exc, httpx.TimeoutException):
            return "TIMEOUT"
        if isinstance(exc, httpx.ConnectError):
            return "CONNECTION"
        return exc.__class__.__name__

    def _log_context(self, url: str) -> str:
        context = {
            "endpoint": self._endpoint_from_url(url),
            "reader_ip": self.device_ip,
            "reader_id": self.reader_id,
            "reader_name": self.reader_name,
            "access_point_id": self.access_point_id,
            "access_point_name": self.access_point_name,
        }
        return " ".join(
            f"{key}={self._quote_log_value(value)}"
            for key, value in context.items()
        )

    def _reset_errors(self):
        self.connection_error = False
        self.connction_error = False
        self.response_error = False

    @classmethod
    def make_eventsResponse_from_dict(cls, data: dict, tz) -> EventsResponse:
        return EventsResponse.from_dict(data or {}, cls._normalize_tz_name(tz))

    def post_request(self, path: str, body: dict | None = None) -> tuple[dict, str]:
        payload = {"device": self.device_ip}
        if body:
            payload.update(body)
        self._reset_errors()
        try:
            with httpx.Client(timeout=self.timeout, headers=self.headers) as client:
                response = client.post(path, json=payload)
        except httpx.HTTPError as exc:
            msg = (
                f"Exception {path}, error_type={self._classify_http_error(exc)} "
                f"{self._log_context(path)}, Error: {exc}"
            )
            self.connection_error = True
            self.connction_error = True
            logger.error(msg)
            return {}, msg

        if response.status_code != httpx.codes.OK:
            self.response_error = True
            msg = (
                f"Error {path}, status_code={response.status_code} "
                f"{self._log_context(path)}, "
                f"payload: {payload}"
            )
            logger.info(msg)
            return {}, msg

        try:
            return response.json(), "OK"
        except ValueError as exc:
            self.response_error = True
            msg = (
                f"Error {path}, error_type=INVALID_JSON "
                f"{self._log_context(path)}, invalid JSON response: {exc}"
            )
            logger.error(msg)
            return {}, msg

    def load_info(self) -> Device:
        self.online = False
        res, msg = self.post_request(self._build_url("info"), {})
        if not res:
            logger.info(msg)
            self.device = Device()
            return self.device
        self.device = Device.from_dict(res)
        self.online = self.device.status
        return self.device

    def load_status(self) -> Device:
        res, msg = self.post_request(self._build_url("status"), {})
        if not res:
            logger.info(msg)
            self.online = False
            return self.device
        status_device = Device.from_dict(res)
        if self.device.status and status_device.status:
            self.device.diagnostic = status_device.diagnostic
            self.online = True
        else:
            self.online = False
        return self.device

    def connect(self):
        self.load_info()
        if self.device.status:
            self.load_status()

    def read_events(self, number_events: int) -> dict:
        body = {"numberEvents": number_events}
        res, msg = self.post_request(self._build_url("read-events"), body)
        if not res:
            logger.info(msg)
        return res

    def write_tags(self, tags_body: dict) -> dict:
        response = {
            "status": True,
            "diagnostic": {
                "event_tab_size": 0,
                "event_cnt": 0,
            },
            "result": False,
        }
        tags = tags_body.get("tags") or []
        timezones = tags_body.get("timeZoneTable") or []
        if not tags or not timezones:
            response["message"] = (
                f"No Enought Data Tags:{len(tags)} , Timezontable: {len(timezones)}"
            )
            return response
        if self.device.diagnostic.event_cnt > 0:
            response["message"] = (
                f"Download {self.device.diagnostic.event_cnt} Events before update tags"
            )
            return response
        res, msg = self.post_request(self._build_url("add-tags"), tags_body)
        if not res:
            response["message"] = msg
            return response
        res.setdefault("message", msg)
        return res

    def update_clock(self) -> ActionResponse:
        res, msg = self.post_request(self._build_url("update-clock"), {})
        if not res:
            return ActionResponse(message=msg)
        action = ActionResponse.from_dict(res)
        if not action.message:
            action.message = msg
        return action

    def read_and_save_events(
            self, number_events: int, path: str, filename: str,
            moveto: str) -> EventsResponse:
        base_path = Path(path)
        base_path.mkdir(parents=True, exist_ok=True)
        target_path = base_path
        if moveto:
            target_path = base_path / moveto
            target_path.mkdir(parents=True, exist_ok=True)
        events_data = self.read_events(number_events)
        if events_data and events_data.get("eventRecords"):
            output_file = target_path / filename
            output_file.write_text(
                json.dumps(events_data, ensure_ascii=False),
                encoding="utf-8",
            )
        return self.make_eventsResponse_from_dict(events_data, self._tz_name)

    @classmethod
    def load_events_from_file(cls, filepath: str, tz: str) -> EventsResponse:
        with Path(filepath).open("r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        return cls.make_eventsResponse_from_dict(data, tz)
