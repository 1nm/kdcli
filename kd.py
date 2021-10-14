#!/usr/bin/env python3
import json
import logging
import random
import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from datetime import datetime, timezone, timedelta
from typing import Dict
from pathlib import Path

import requests

logging.basicConfig(
    format="%(asctime)s - %(levelname)s: %(message)s", level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)

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


def nearest(tz: timezone = TIME_ZONE_JST) -> datetime:
    hour = datetime.now(tz).hour
    return today() if hour < 9 else tomorrow()


def remove_config() -> str:
    kdcliConfigDir = Path.home() / ".kdcli"
    configFile = kdcliConfigDir / "config.json"
    if configFile.exists:
        configFile.unlink()


def load_config() -> Dict:
    kdcliConfigDir = Path.home() / ".kdcli"
    configFile = kdcliConfigDir / "config.json"
    if not kdcliConfigDir.exists() or not configFile.exists():
        return None
    with configFile.open(mode="r") as f:
        config = json.load(f)
    return config


def save_config(config: Dict):
    kdcliConfigDir = Path.home() / ".kdcli"
    if not kdcliConfigDir.exists():
        kdcliConfigDir.mkdir()
    configFile = kdcliConfigDir / "config.json"
    with configFile.open(mode="w") as f:
        json.dump(config, f)


class KidsDiaryCLI:
    def __init__(self, config: Dict):
        if config is None or 'userToken' not in config:
            raise ValueError("Token does not exist!")
        self._config = config

    def get_draft_payload(self, date: datetime = today(),
                          message: str = "本日もよろしくお願いいたします",
                          food_menu: str = "Milk and bread",
                          pick_up_person: str = "Father",
                          publish_delta=timedelta(
                              hours=8, minutes=30),  # publish at 8:30am
                          # slept at 8pm yesterday
                          sleep_time_delta=timedelta(hours=-4),
                          awake_time_delta=timedelta(hours=8),  # awaken at 8am
                          food_time_delta=timedelta(
                              hours=8, minutes=15),  # food at 8:15am
                          # temperature taken at 8:10am
                          health_time_delta=timedelta(hours=8, minutes=10),
                          pick_up_time_delta=timedelta(
                              hours=16, minutes=30)  # pick-up at 4:30pm
                          ) -> Dict:
        dt0am = datetime_0am(date)
        return {
            "childId": self._config['childIds'][0],
            "userToken": self._config['userToken'],
            "publishScheduleDate": epoch_millis(dt0am + publish_delta),
            "textContent": message,
            "health": [{"healthStatus": "Health",
                        # randomly generated from 36.4 to 36.8
                        "temperature": f"36.{random.choice([4, 5, 6, 7, 8])}",
                        "healthTime": str(epoch_millis(dt0am + health_time_delta))}],
            "sleep": [{"sleepTime": epoch_millis(dt0am + sleep_time_delta),
                       "awakeTime": epoch_millis((dt0am + awake_time_delta))}],
            "food": [{"foodMenu": food_menu, "foodTime": epoch_millis(dt0am + food_time_delta)}],
            "pickUpPerson": pick_up_person, "pickUpTime": epoch_millis(dt0am + pick_up_time_delta)}

    def list_drafts(self):
        payload = {
            "childId": self._config['childIds'][0], "userToken": self._config['userToken']}
        draft_list_response = post(path="diary/draft/list", payload=payload)
        if draft_list_response.status_code == 200:
            data = draft_list_response.json()
            if data['totalHits'] > 0:
                logger.info(
                    f"Found {data['totalHits']} draft(s):")
                # List the draft content
                for draft in data['list']:
                    draft_content = self.get_draft(draft_id=draft['draftId'])
                    logger.info(f"{draft_content}")

    def get_draft(self, draft_id: str) -> Dict:
        payload = {
            "childId": self._config['childIds'][0], "userToken": self._config['userToken']}
        payload['draftId'] = draft_id
        draft_detail_response = post(
            path="diary/draft/detail", payload=payload)
        if draft_detail_response.status_code == 200:
            return draft_detail_response.json()

    def create_or_update_draft(self, draft_payload: Dict = None):
        payload = {
            "childId": self._config['childIds'][0], "userToken": self._config['userToken']}
        draft_list_response = post(path="diary/draft/list", payload=payload)
        if draft_list_response.status_code == 200:
            data = draft_list_response.json()
            if data['totalHits'] > 0:
                if draft_payload is not None:
                    draft_payload['draftId'] = data['list'][0]['draftId']
                    logger.info(
                        f"Replacing draft {draft_payload['draftId']} ...")
                    update_draft_response = post(
                        path="diary/draft/update", payload=draft_payload)
                    if update_draft_response.status_code == 200:
                        logger.info(
                            f"Draft {draft_payload['draftId']} updated.")
                    else:
                        logger.error(
                            f"Draft update API returned status code: {update_draft_response.status_code}, message: {update_draft_response.text}")
            else:
                logger.info(f"No drafts")
                if draft_payload is not None:
                    logger.info("Creating a new draft ...")
                    create_draft_response = post(
                        path="diary/draft/post", payload=draft_payload)
                    if create_draft_response.status_code == 200:
                        logger.info("Draft created.")
                    else:
                        logger.error(
                            f"Draft creation API returned status code: {create_draft_response.status_code}, message: {create_draft_response.text}")
        else:
            logger.error(
                f"Draft list API returned status code: {draft_list_response.status_code}, message: {draft_list_response.text}")


def command_draft(args):
    config = load_config()
    if config is None:
        logger.error("Credentials not found! Please login.")
        sys.exit(1)
    else:
        logger.info(f"Logged in as {config['loginName']}")
    helper = KidsDiaryCLI(config)
    if args.list:
        helper.list_drafts()
    elif args.create:
        date = today() if args.today else nearest()
        message = args.message.replace('\\n', '\n')
        food_menu = args.food_menu
        pick_up_person = args.pick_up_person
        draft_payload = helper.get_draft_payload(
            date=date, message=message, food_menu=food_menu, pick_up_person=pick_up_person)
        helper.create_or_update_draft(draft_payload=draft_payload)


def command_login(args):
    login_response = post(
        path="login", payload={"loginName": args.user, "password": args.password})
    if login_response.status_code == 200:
        login_response_json = login_response.json()
        config = {
            'userToken': login_response_json['userToken'], 'childIds': login_response_json['childIds'], 'loginName': login_response_json['loginName']}
        save_config(config)
        logger.info(f"Login succeeded!")
    else:
        logger.error(f"Login failed!")


def command_logout(args):
    remove_config()
    logger.info(f"Logged out")


def main():
    parser = ArgumentParser(description="KidsDiary CLI",
                            formatter_class=ArgumentDefaultsHelpFormatter)

    subparsers = parser.add_subparsers()

    parser_draft = subparsers.add_parser(
        'draft', help='see `draft -h`', formatter_class=ArgumentDefaultsHelpFormatter)

    parser_draft.add_argument(
        "-l", "--list", action="store_true", help='List the drafts')
    parser_draft.add_argument(
        "-c", "--create", action="store_true", help='Create a new draft')
    parser_draft.add_argument("-T", "--today", action="store_true",
                              help='Publish the draft today')
    parser_draft.add_argument(
        "-m", "--message", default='本日もよろしくお願いします', help='Message to the teacher')
    parser_draft.add_argument(
        "-p", "--pick-up-person", default='Father', help='Pick-up person')
    parser_draft.add_argument(
        "-f", "--food-menu", default='Milk and bread', help='Food menu')
    parser_draft.set_defaults(handler=command_draft)

    parser_login = subparsers.add_parser(
        'login', help='see `login -h`', formatter_class=ArgumentDefaultsHelpFormatter)
    parser_login.add_argument("-u", "--user", required=True)
    parser_login.add_argument("-p", "--password", required=True)
    parser_login.set_defaults(handler=command_login)

    parser_logout = subparsers.add_parser(
        'logout', help='see `logout -h`', formatter_class=ArgumentDefaultsHelpFormatter)
    parser_logout.set_defaults(handler=command_logout)

    args = parser.parse_args()
    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
