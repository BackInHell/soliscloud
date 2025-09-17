
# solis_api.py (patched)
# Fixes:
#  - Date header now uses RFC1123 English via email.utils.formatdate(usegmt=True) to avoid locale issues.
#  - Content-Type switched to "application/json" (matches signing examples in docs).
#  - Added toggle to use ";charset=UTF-8" if needed (set USE_JSON_CHARSET=True).

import base64
import datetime as dt
import hashlib
import hmac
import json
from typing import Any, Dict, Optional, List, Union

import requests
from email.utils import formatdate

JSON = Dict[str, Any]


class SolisClient:
    def __init__(self, api_id: str, api_secret: str, base_url: str = "https://www.soliscloud.com:13333", *, use_json_charset: bool = False):
        self.api_id = api_id
        self.api_secret = api_secret.encode("utf-8")
        self.base_url = base_url.rstrip("/")
        # Use "application/json" for signing by default; optionally include charset in header & signing.
        self.content_type = "application/json;charset=UTF-8" if use_json_charset else "application/json"
        self.session = requests.Session()

    # --- Helpers ---------------------------------------------------------
    @staticmethod
    def _gmt_date() -> str:
        # RFC 1123 English (always en-US), e.g. "Fri, 26 Jul 2019 06:00:46 GMT"
        return formatdate(usegmt=True)

    @staticmethod
    def _content_md5(body: str) -> str:
        m = hashlib.md5()
        m.update(body.encode("utf-8"))
        return base64.b64encode(m.digest()).decode("ascii")

    def _sign(self, method: str, content_md5: str, date: str, resource_path: str) -> str:
        string_to_sign = f"{method}\n{content_md5}\n{self.content_type}\n{date}\n{resource_path}"
        hm = hmac.new(self.api_secret, string_to_sign.encode("utf-8"), hashlib.sha1)
        return base64.b64encode(hm.digest()).decode("ascii")

    def _post(self, path: str, payload: Optional[JSON] = None, timeout: int = 30) -> JSON:
        url = f"{self.base_url}{path}"
        body = json.dumps(payload or {}, separators=(",", ":"), ensure_ascii=False)
        content_md5 = self._content_md5(body)
        date = self._gmt_date()
        sign = self._sign("POST", content_md5, date, path)
        headers = {
            "Content-MD5": content_md5,
            "Content-Type": self.content_type,
            "Date": date,
            "Authorization": f"API {self.api_id}:{sign}",
            "Accept": "application/json",
        }
        resp = self.session.post(url, data=body.encode("utf-8"), headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    # --- Public endpoints (Auswahl) -------------------------------------
    def inverter_list(
        self,
        page_no: int = 1,
        page_size: int = 20,
        station_id: Optional[Union[int, str]] = None,
        nmi_code: Optional[str] = None,
        sn_list: Optional[List[str]] = None,
    ) -> JSON:
        path = "/v1/api/inverterList"
        payload: JSON = {"pageNo": page_no, "pageSize": page_size}
        if station_id is not None:
            payload["stationId"] = str(station_id)
        if nmi_code:
            payload["nmiCode"] = nmi_code
        if sn_list:
            payload["snList"] = sn_list
        return self._post(path, payload)

    def inverter_detail(self, id: Optional[Union[int, str]] = None, sn: Optional[str] = None) -> JSON:
        path = "/v1/api/inverterDetail"
        if not id and not sn:
            raise ValueError("id oder sn ist erforderlich.")
        payload: JSON = {}
        if id is not None:
            payload["id"] = str(id)
        if sn:
            payload["sn"] = sn
        return self._post(path, payload)

    def inverter_day(
        self,
        time_yyyy_mm_dd: str,
        time_zone: int,
        id: Optional[Union[int, str]] = None,
        sn: Optional[str] = None,
        money: str = "",
    ) -> JSON:
        path = "/v1/api/inverterDay"
        if not id and not sn:
            raise ValueError("id oder sn ist erforderlich.")
        payload: JSON = {"time": time_yyyy_mm_dd, "timeZone": str(time_zone), "money": money}
        if id is not None:
            payload["id"] = str(id)
        if sn:
            payload["sn"] = sn
        return self._post(path, payload)


if __name__ == "__main__":
    API_ID = ""
    API_SECRET = ""
    BASE_URL = "https://www.soliscloud.com:13333"

    client = SolisClient(API_ID, API_SECRET, BASE_URL, use_json_charset=False)

    try:
        ilist = client.inverter_list(page_no=1, page_size=10)
        print("inverterList:", json.dumps(ilist, indent=2, ensure_ascii=False))
    except requests.HTTPError as e:
        print("HTTP error:", e.response.status_code, e.response.text)
    except Exception as e:
        print("Error:", repr(e))