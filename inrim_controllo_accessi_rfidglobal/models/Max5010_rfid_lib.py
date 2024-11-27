import json
import logging
import os
import shutil
from dataclasses import field
from datetime import datetime
from typing import List

import httpx
import pytz
from attr import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Tag:
    idd: str = ""
    timezoneConfig: str = "1000000000000000"


@dataclass
class TimeZoneTableItem:
    dateStart: datetime = field(default_factory=datetime.now)
    dateEnd: datetime = field(default_factory=datetime.now)
    days: int = 255
    hoursStart: str = "00:00"
    hoursEnd: str = "23:59"


@dataclass
class AddTagsBody:
    tags: List[Tag] = field(default_factory=list)
    timeZoneTable: List[TimeZoneTableItem] = field(default_factory=list)


# Event Record

@dataclass
class DigitalInputItem():
    input: bool = False


@dataclass
class LayoutItem():
    input: bool = False


@dataclass
class EventRecord():
    idd: str = ""
    eventDateTime: str = ""
    errorCode: str = ""
    accessAllowed: bool = False
    digitalInput: List[DigitalInputItem] = field(
        default_factory=list[DigitalInputItem])
    tz: str = ""

    def __post_init__(self):
        if self.tz:
            self.tzo = pytz.timezone(self.tz)

    def eventDateTime_to_utc(self):
        tzo = pytz.timezone(self.tz or "UTC")
        loc = tzo.localize(
            datetime.fromisoformat(self.eventDateTime)
        )
        return loc.astimezone(pytz.UTC).replace(tzinfo=None)

    def eventDateTime_to_utc_isoformat(self):
        return self.eventDateTime_to_utc().replace(tzinfo=None)

    def eventDateTime_to_tz(self):
        tzo = pytz.timezone(self.tz or "UTC")
        dt_naive = datetime.fromisoformat(date_str)
        dt_utc = pytz.UTC.localize(dt_naive)
        return dt_utc.astimezone(tzo).replace(tzinfo=None)

    def eventDateTime_to_tz_isoformat(self):
        return self.eventDateTime_to_tz().isoformat()


@dataclass
class EventsResponse():
    status: int = 0
    statusStr: str = ""
    layoutIdd: bool = False
    layoutTimeStamp: bool = False
    layoutEventStatus: bool = False
    layoutInput: bool = False
    dataSetsLenght: int = 0
    hasMore: bool = False
    layout: List[LayoutItem] = field(default_factory=list)
    eventRecords: List[EventRecord] = field(default_factory=list)

    def is_error(self) -> bool:
        return self.status == -2

    def is_ok(self) -> bool:
        return self.status == 148


# Device Info and Status
@dataclass
class DeviceInfo():
    deviceId: str = ''
    readerType: str = ''
    mode: str = ''
    modeCode: str = ''


@dataclass
class DeviceDiagnostic():
    event_tab_size: int = 0
    event_cnt: int = 0
    systemClock: datetime = None


@dataclass
class Device():
    status: bool = False
    diagnostic: DeviceDiagnostic = field(default_factory=DeviceDiagnostic)
    info: DeviceInfo = field(default_factory=DeviceInfo)


# Action Response
@dataclass
class ActionResponse():
    status: bool = False
    diagnostic: DeviceDiagnostic = field(default_factory=DeviceDiagnostic)
    result: bool = False
    message: str = ""


class Max5010RfidClient:
    def __init__(
            self, device_ip, base_url, header_auth_key, header_auth_value, tz):
        self.device_ip = device_ip
        self.base_url = base_url

        self.headers = {
            header_auth_key: header_auth_value
        }
        self.online = False
        self.connction_error = False
        self.response_error = False
        self.timeout = httpx.Timeout(10.0)
        self.device: Device = Device()
        self._tz = tz
        self.tz = pytz.timezone(tz)

    @classmethod
    def make_EventsResponse_from_dict(cls, data: dict, tz) -> EventsResponse:
        events = EventsResponse(**data)
        for idx in range(len(events.eventRecords)):
            events.eventRecords[idx]['tz'] = tz
            events.eventRecords[idx] = EventRecord(**events.eventRecords[idx])
        return events

    def post_request(self, path: str, body: dict) -> (dict, str):
        payload = {"device": self.device_ip}
        payload.update(body)
        self.connction_error = False
        self.response_error = False
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(path, json=payload, headers=self.headers)
            if response.status_code == 200:
                return response.json(), "OK"
            else:
                self.response_error = True
                msg = f"Error {path}, Status Code: {response.status_code}, payload: {payload}"
                logger.info(msg)
                return {}, msg
        except Exception as e:
            msg = f"Exception {path}, Error: {e}"
            self.connction_error = True
            return {}, msg

    def load_info(self) -> Device:
        self.online = False
        rest_path = f"{self.base_url}/info"
        res, msg = self.post_request(rest_path, {})
        self.device = Device(**res)
        self.device.info = DeviceInfo(**res.get('info', {}))
        if self.device.status:
            self.online = True
        return self.device

    def load_status(self, ) -> Device:
        rest_path = f"{self.base_url}/status"
        res, msg = self.post_request(rest_path, {})
        device = Device(**res)
        if self.device.status and device.status:
            self.device.diagnostic = DeviceDiagnostic(**device.diagnostic)
        return self.device

    def connect(self):
        self.load_info()
        if self.device.status:
            self.load_status()

    def read_events(self, numeber_events: int) -> dict:
        body = {
            "numberEvents": numeber_events
        }
        rest_path = f"{self.base_url}/read-events"
        res, msg = self.post_request(rest_path, body)
        return res

    def write_tags(self, tags_body: dict) -> dict:
        ar = {
            "status": True,
            "diagnostic": {
                "event_tab_size": 0,
                "event_cnt": 0
            },
            "result": False
        }
        if not tags_body.get('tags') or not tags_body.get('timeZoneTable'):
            msg = f"No Enought Data Tags:{len(tags_body.get('tags'))} , Timezontable: {len(tags_body.get('timeZoneTable'))}"
            ar['message'] = msg
            return ar
        if self.device.diagnostic.event_cnt > 0:
            msg = f"Download  {self.device.diagnostic.event_cnt} Events before update tags"
            ar['message'] = msg
            return ar
        rest_path = f"{self.base_url}/add-tags"
        res, msg = self.post_request(rest_path, tags_body)
        res['message'] = msg
        return res

    def update_clock(self) -> ActionResponse:
        rest_path = f"{self.base_url}/update-clock"
        res, msg = self.post_request(rest_path, {})
        return ActionResponse(**res)

    def read_and_save_events(
            self, numeber_events: int, path: str, filename: str,
            moveto: str) -> EventsResponse:

        if not os.path.exists(path):
            os.makedirs(path)
            dstpath = os.path.join(path, moveto)
            os.makedirs(dstpath)
        eventsd = self.read_events(numeber_events)
        if eventsd:
            jdata = json.dumps(eventsd)
            src = os.path.join(path, filename)
            with open(src, 'w') as json_file:
                json_file.write(jdata)
            if moveto:
                dstpath = os.path.join(path, moveto)
                dst = os.path.join(dstpath, filename)
                shutil.move(src, dst)
        return self.make_EventsResponse_from_dict(eventsd, self.tz)

    @classmethod
    def load_events_from_file(cls, filepath: str, tz: str) -> EventsResponse:
        data = {}
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.make_EventsResponse_from_dict(data, tz)
