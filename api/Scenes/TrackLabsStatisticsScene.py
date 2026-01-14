import datetime
import random
import uuid

import vesta

from Helper.ConfigHelper import ConfigHelper
from Repository import Repository
from Scenes.AbstractScene import AbstractScene, SceneExecuteReturn

import csv
import gzip
import io
import sys
from datetime import date, timedelta
from typing import Dict, Tuple, List, Optional

import httpx
import jwt  # PyJWT
from jwt.algorithms import ECAlgorithm


from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
from google.oauth2 import service_account

KEY_FILE = "/config/ebikeconnect-156817-b02783a8f7b3.json"
PROPERTY_ID = "271546499"  # GA4 property id (nur Zahl)

credentials = service_account.Credentials.from_service_account_file(KEY_FILE)
google_client = BetaAnalyticsDataClient(credentials=credentials)

request = RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    dimensions=[Dimension(name="date")],
    metrics=[Metric(name="sessions"), Metric(name="activeUsers")],
    date_ranges=[DateRange(start_date="14daysAgo", end_date="yesterday")],
)






ASC_API_BASE = "https://api.appstoreconnect.apple.com"
SALES_REPORTS_ENDPOINT = f"{ASC_API_BASE}/v1/salesReports"



# ----------------------------
# HIER DEINE WERTE EINTRAGEN
# ----------------------------
ISSUER_ID = "69a6de6e-840d-47e3-e053-5b8c7c11a4d1"          # App Store Connect -> Issuer ID
KEY_ID = "W82D347DL6"                                       # Key ID
VENDOR_NUMBER = "80067783"                                  # Vendor Number
APP_TITLE = "TrackLabs"
PRIVATE_KEY_P8_PATH = "/config/AuthKey_W82D347DL6.p8"       # Pfad zur .p8 Datei
DAYS = 14                                                   # letzte N Tage inkl. heute
# ----------------------------
# Product Type Identifier: 7 = Update (laut Apple)
# https://developer.apple.com/help/app-store-connect/reference/reporting/product-type-identifiers
UPDATE_PRODUCT_TYPE_ID = "7F"
DOWNLOAD_PRODUCT_TYPE_ID = "1F"



def load_private_key_p8(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def make_jwt(issuer_id: str, key_id: str, private_key_p8: str) -> str:
    now = int(__import__("time").time())
    payload = {
        "iss": issuer_id,
        "iat": now,
        "exp": now + 20 * 60,  # 20 min
        "aud": "appstoreconnect-v1",
    }
    headers = {"kid": key_id, "typ": "JWT", "alg": "ES256"}

    # PyJWT kann .p8 direkt signieren, wenn es ein PEM EC private key ist (was .p8 ist).
    token = jwt.encode(payload, private_key_p8, algorithm="ES256", headers=headers)
    return token


def download_daily_summary_report(
    client: httpx.Client,
    token: str,
    vendor_number: str,
    report_date: date,
) -> bytes | None:
    params = {
        "filter[frequency]": "DAILY",
        "filter[reportType]": "SALES",
        "filter[reportSubType]": "SUMMARY",
        "filter[vendorNumber]": vendor_number,
        "filter[reportDate]": report_date.isoformat(),  # YYYY-MM-DD
    }
    headers = {"Authorization": f"Bearer {token}"}

    r = client.get(SALES_REPORTS_ENDPOINT, params=params, headers=headers, timeout=30.0)
    if r.status_code in (204, 404):
        # 204: kein Content; 404: Report (noch) nicht vorhanden
        return None
    r.raise_for_status()
    return r.content  # gzip-komprimierter TSV-Report


def parse_summary_sales_tsv_gz(gz_bytes: bytes) -> List[Dict[str, str]]:
    # Apple liefert i.d.R. gzip
    with gzip.GzipFile(fileobj=io.BytesIO(gz_bytes)) as gz:
        raw = gz.read()
    text = raw.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text), delimiter="\t")
    return list(reader)


def extract_tracklabs_downloads_updates(rows: List[Dict[str, str]]) -> Tuple[int, int]:
    downloads = 0
    updates = 0

    for row in rows:
        title = (row.get("Title") or "").strip()
        date = (row.get("Begin Date") or "").strip()
        if title != APP_TITLE:
            continue

        units_str = (row.get("Units") or "0").strip()
        try:
            units = int(float(units_str))
        except ValueError:
            units = 0

        product_type_id = (row.get("Product Type Identifier") or "").strip()

        #print(f"{date}: {product_type_id} -> {units}")

        if product_type_id == UPDATE_PRODUCT_TYPE_ID:
            updates += units
        elif product_type_id == DOWNLOAD_PRODUCT_TYPE_ID:
            downloads += units

    return downloads, updates


class TrackLabsStatisticsScene(AbstractScene):
    priority = 100
    post_execution: bool = False

    def execute(self, vboard, previous_identifier: str = None) -> SceneExecuteReturn:

        start_date = datetime.datetime.now()
        end_date = self.get_next_full_hour()

        if not self.post_execution:
            return SceneExecuteReturn(f"{self.__class__.__name__}_{str(uuid.uuid4())}", True, self.priority, self,
                                      start_date, end_date, "not executed yet", None)

        private_key = load_private_key_p8(PRIVATE_KEY_P8_PATH)
        token = make_jwt(ISSUER_ID, KEY_ID, private_key)

        start = date.today() - timedelta(days=DAYS - 1)
        days = [start + timedelta(days=i) for i in range(DAYS)]

        per_day = []
        total_downloads = 0
        total_updates = 0

        with httpx.Client() as client:
            for d in days:
                gz = download_daily_summary_report(client, token, VENDOR_NUMBER, d)
                if not gz:
                    per_day.append((d.isoformat(), None, None))
                    continue

                rows = parse_summary_sales_tsv_gz(gz)
                downloads, updates = extract_tracklabs_downloads_updates(rows)

                per_day.append((d.isoformat(), downloads, updates))
                total_downloads += downloads
                total_updates += updates

        # Output
        # print(f"\nTrackLabs — Downloads & Updates (letzte {DAYS} Tage, inkl. heute)\n")
        # print(f"{'Date':<12}  {'Downloads':>10}  {'Updates':>10}")
        # print("-" * 36)
        # for day_str, dl, up in per_day:
        #     if dl is None:
        #         print(f"{day_str:<12}  {'(n/a)':>10}  {'(n/a)':>10}")
        #     else:
        #         print(f"{day_str:<12}  {dl:>10}  {up:>10}")
        #
        # print("-" * 36)
        # print(f"{'TOTAL':<12}  {total_downloads:>10}  {total_updates:>10}\n")

        # google analytics stuff

        response = google_client.run_report(request)
        #print(response.rows)

        g_active_users = 0
        g_sessions = 0
        for row in response.rows:
            gdate = row.dimension_values[0].value
            sessions = row.metric_values[0].value
            users = row.metric_values[1].value
            g_sessions += int(sessions)
            g_active_users += int(users)
            #print(gdate, sessions, users)


        message = f"tracklabs statistics\n\nDownloads: {total_downloads}\nUpdates: {total_updates}\nActive Users: {g_active_users}\nSessions: {g_sessions}"
        chars = vesta.encode_text(message, align="center", valign="middle")

        return SceneExecuteReturn(f"{self.__class__.__name__}_{start_date}", True, self.priority, self,
                                  start_date, end_date, message, chars)


    def post_execute(self, vboard) -> Optional[SceneExecuteReturn]:
        self.post_execution = True
        res = self.execute(vboard)
        self.post_execution = False
        return res