import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "inrim_controllo_accessi_rfidglobal"
    / "models"
    / "Max5010_rfid_lib.py"
)
SPEC = importlib.util.spec_from_file_location("max5010_rfid_lib", MODULE_PATH)
rfid_lib = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = rfid_lib
SPEC.loader.exec_module(rfid_lib)


class FailingHttpClient:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def post(self, path, json):
        raise httpx.ConnectError("[Errno -3] Temporary failure in name resolution")


class Max5010ClientLoggingTests(unittest.TestCase):
    def test_log_context_contains_access_point_and_reader(self):
        client = rfid_lib.Max5010RfidClient(
            "10.194.16.5",
            "https://access-reader.docker.ininrim.it",
            "authtoken",
            "test-token",
            "Europe/Rome",
            reader_id=42,
            reader_name="Zp001 Ped In",
            access_point_id=7,
            access_point_name="Zp001 Cacce Ped In",
        )

        context = client._log_context("https://access-reader.docker.ininrim.it/info")

        self.assertIn("endpoint=/info", context)
        self.assertIn("reader_ip=10.194.16.5", context)
        self.assertIn("reader_id=42", context)
        self.assertIn('reader_name="Zp001 Ped In"', context)
        self.assertIn("access_point_id=7", context)
        self.assertIn('access_point_name="Zp001 Cacce Ped In"', context)

    def test_dns_error_log_is_classified_and_contextualized(self):
        client = rfid_lib.Max5010RfidClient(
            "10.194.16.6",
            "https://access-reader.docker.ininrim.it",
            "authtoken",
            "test-token",
            "Europe/Rome",
            reader_id=43,
            reader_name="Zp001 Ped Out",
            access_point_id=8,
            access_point_name="Zp001 Cacce Ped Out",
        )

        with patch.object(rfid_lib.httpx, "Client", FailingHttpClient):
            with self.assertLogs(rfid_lib.logger, level="ERROR") as logs:
                response, message = client.post_request(client._build_url("status"))

        self.assertEqual({}, response)
        self.assertIn("error_type=DNS", message)
        self.assertIn("reader_ip=10.194.16.6", message)
        self.assertIn('access_point_name="Zp001 Cacce Ped Out"', message)
        self.assertIn("endpoint=/status", "\n".join(logs.output))


if __name__ == "__main__":
    unittest.main()
