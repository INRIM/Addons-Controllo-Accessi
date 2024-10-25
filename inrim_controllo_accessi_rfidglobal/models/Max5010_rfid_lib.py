import dataclasses
import json
import logging
import os
import shutil
from dataclasses import field
from datetime import datetime
from typing import List

import httpx
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
    eventDateTime: datetime = field(default_factory=datetime.now)
    errorCode: str = ""
    accessAllowed: bool = False
    digitalInput: List[DigitalInputItem] = field(
        default_factory=list[DigitalInputItem])


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


class Max5010RfidClient:
    def __init__(self, device_ip, base_url, header_auth_key, header_auth_value):
        self.device_ip = device_ip
        self.base_url = base_url

        self.headers = {
            header_auth_key: header_auth_value
        }
        self.online = False
        self.connction_error = False
        self.response_error = False
        self.timeout = httpx.Timeout(5.0)
        self.device: Device = Device()

    @classmethod
    def make_EventsResponse_from_dict(self, data: dict) -> EventsResponse:
        events = EventsResponse(**data)
        for idx in range(len(events.eventRecords)):
            events.eventRecords[idx] = EventRecord(**events.eventRecords[idx])
        return events

    def post_request(self, path: str, body: dict) -> dict:
        payload = {"device": self.device_ip}
        payload.update(body)
        self.connction_error = False
        self.response_error = False
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(path, json=payload, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                self.response_error = True
                logger.info(
                    f"{path}, Status Code: {response.status_code}, payload: {payload}")
                return {}
        except Exception as e:
            logger.error(f"{path}, Error: {e}", exc_info=True)
            self.connction_error = True
            return {}

    def load_info(self) -> Device:
        self.online = False
        rest_path = f"{self.base_url}/info"
        res = self.post_request(rest_path, {})
        self.device = Device(**res)
        self.device.info = DeviceInfo(**res.get('info', {}))
        if self.device.status:
            self.online = True
        return self.device

    def load_status(self, ) -> Device:
        rest_path = f"{self.base_url}/status"
        res = self.post_request(rest_path, {})
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
        res = self.post_request(rest_path, body)
        return res

    def write_tags(self, tags_body: dict) -> ActionResponse:
        if not tags_body.get('tags') or not tags_body.get('timeZoneTable'):
            logger.info(
                f"No Enought Data Tags:{len(tags_body.get('tags'))} , Timezontable: {len(tags_body.get('timeZoneTable'))}")
            return from_dict(ActionResponse, {})
        if self.device.diagnostic.event_cnt > 0:
            res = ActionResponse()
            res.diagnostic = dataclasses.replace(device.diagnostic)
            logger.info(
                f"Download Events before update tags")
            return res
        rest_path = f"{self.base_url}/add-tags"
        res = self.post_request(rest_path, tags_body)
        return ActionResponse(**res)

    def update_clock(self) -> ActionResponse:
        rest_path = f"{self.base_url}/update-clock"
        res = self.post_request(rest_path, {})
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
        return self.make_EventsResponse_from_dict(eventsd)

    @classmethod
    def load_events_from_file(cls, filepath: str) -> EventsResponse:
        data = {}
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.make_EventsResponse_from_dict(data)
