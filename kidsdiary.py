#!/usr/bin/env python3
import json
import logging
import random
from argparse import ArgumentParser
from datetime import datetime, timezone, timedelta
from typing import Dict

import requests

logging.basicConfig(
    format="%(asctime)s - %(levelname)s: %(message)s", level=logging.INFO)

TIME_ZONE_JST = timezone(timedelta(hours=9))


def post(path: str, payload: Dict):
    kids_diary_api_endpoint = "https://kidsdiary.jp/api"
    headers = {'content-type': 'application/json'}
    return requests.post(f"{kids_diary_api_endpoint}/{path}",
                         headers=headers, data=json.dumps(payload))


def datetime_0am(dt: datetime) -> datetime:
    year = dt.year
    month = dt.month
    day = dt.day
    return datetime(year, month, day)


# Default timezone is JST (GMT+9)
def epoch_millis(dt: datetime, tz: timezone = TIME_ZONE_JST) -> int:
    epoch = datetime.utcfromtimestamp(0)
    return int((dt - epoch - tz.utcoffset(dt)).total_seconds() * 1000)


def today(tz: timezone = TIME_ZONE_JST) -> datetime:
    return datetime.now(tz)


def tomorrow(tz: timezone = TIME_ZONE_JST) -> datetime:
    return datetime.now(tz) + timedelta(days=1)


class KidsDiaryDraftHelper:
    def __init__(self, token: str):
        self._logger = logging.getLogger(
            KidsDiaryDraftHelper.__class__.__name__)
        self._token = token
        my_profile_response = post(
            path="my_profile", payload={"userToken": token})
        if my_profile_response.status_code == 200:
            # Assume there is only one child
            self._child_id = my_profile_response.json()["childIds"][0]
        else:
            raise ValueError("Could not retrieve child id from KidsDiary!")

    def get_draft_payload(self, date: datetime = today(),
                          text: str = "本日もよろしくお願いいたします",
                          publishDelta=timedelta(
                              hours=8, minutes=30),  # publish at 8:30am
                          # slept at 8pm yesterday
                          sleepTimeDelta=timedelta(hours=-4),
                          awakeTimeDelta=timedelta(hours=8),  # awaken at 8am
                          foodTimeDelta=timedelta(
                              hours=8, minutes=15),  # food at 8:15am
                          # temperature taken at 8:10am
                          healthTimeDelta=timedelta(hours=8, minutes=10),
                          pickUpTimeDelta=timedelta(
                              hours=16, minutes=30)  # pick-up at 4:30pm
                          ) -> Dict:
        dt0am = datetime_0am(date)
        return {
            "childId": self._child_id,
            "userToken": self._token,
            "publishScheduleDate": epoch_millis(dt0am + publishDelta),
            "textContent": text,
            "health": [{"healthStatus": "Health",
                        # randomly generated from 36.4 to 36.8
                        "temperature": f"36.{random.choice([4, 5, 6, 7, 8])}",
                        "healthTime": str(epoch_millis(dt0am + healthTimeDelta))}],
            "sleep": [{"sleepTime": epoch_millis(dt0am + sleepTimeDelta),
                       "awakeTime": epoch_millis((dt0am + awakeTimeDelta))}],
            "food": [{"foodMenu": "Milk and bread", "foodTime": epoch_millis(dt0am + foodTimeDelta)}],
            "pickUpPerson": "Father", "pickUpTime": epoch_millis(dt0am + pickUpTimeDelta)}

    def list_drafts(self):
        self.create_or_update_draft(draft_payload=None)

    def create_or_update_draft(self, draft_payload: Dict = None):
        payload = {"childId": self._child_id, "userToken": self._token}
        self._logger.info(payload)
        draft_list_response = post(path="diary/draft/list", payload=payload)
        if draft_list_response.status_code == 200:
            data = draft_list_response.json()
            if data['totalHits'] > 0:
                self._logger.info(
                    f"Found {data['totalHits']} drafts")
                draft_id = data['list'][0]['draftId']
                payload['draftId'] = draft_id
                draft_detail_response = post(
                    path="diary/draft/detail", payload=payload)
                self._logger.info(
                    f"Current draft: {draft_detail_response.json()}")
                if draft_payload is not None:
                    self._logger.info("Replacing the current draft ...")
                    draft_payload['draftId'] = draft_id
                    update_draft_response = post(
                        path="diary/draft/update", payload=draft_payload)
                    if update_draft_response.status_code == 200:
                        self._logger.info("Draft updated")
                    else:
                        self._logger.warning(update_draft_response.status_code)
            else:
                self._logger.info(f"No drafts")
                if draft_payload is not None:
                    self._logger.info("Creating a new draft ...")
                    create_draft_response = post(
                        path="diary/draft/post", payload=draft_payload)
                    if create_draft_response.status_code == 200:
                        self._logger.info("Draft created")
                    else:
                        self._logger.warning(create_draft_response.status_code)
        else:
            self._logger.warning("Failed to list the drafts")
            self._logger.warning(draft_list_response.status_code)
            self._logger.warning(draft_list_response.text)


def main():
    parser = ArgumentParser(description="KidsDiary Draft Helper CLI")
    parser.add_argument("-l", "--list", action="store_true")
    parser.add_argument("-m", "--message")
    parser.add_argument("-t", "--token", required=True)
    args = parser.parse_args()
    helper = KidsDiaryDraftHelper(args.token)
    if args.list:
        helper.list_drafts()
    else:
        draft_payload = helper.get_draft_payload(date=today(), text=args.text)
        helper.create_or_update_draft(draft_payload=draft_payload)


if __name__ == '__main__':
    main()
