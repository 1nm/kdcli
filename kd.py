#!/usr/bin/env python3
import json
import logging
import os
import random
import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict

import requests

__version__ = '0.0.1'

logging.basicConfig(
    # format="%(asctime)s - %(levelname)s: %(message)s", level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    format="%(message)s", level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S', stream=sys.stdout)

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


def remove_config():
    kdcli_config_dir = Path.home() / ".kdcli"
    config_file = kdcli_config_dir / "config.json"
    if config_file.exists:
        config_file.unlink()


def load_config():
    if "USERNAME" in os.environ and "PASSWORD" in os.environ:
        username = os.environ["USERNAME"]
        password = os.environ["PASSWORD"]
        login_response = post(path="login", payload={"loginName": username, "password": password})
        if login_response.status_code == 200:
            return login_response.json()
    if "TOKEN" in os.environ:
        user_token = os.environ["TOKEN"]
        my_profile_response = post(path="my_profile", payload={"userToken": user_token})
        if my_profile_response.status_code == 200:
            return my_profile_response.json()
    kdcli_config_dir = Path.home() / ".kdcli"
    config_file = kdcli_config_dir / "config.json"
    if not kdcli_config_dir.exists() or not config_file.exists():
        return None
    with config_file.open(mode="r") as f:
        config = json.load(f)
    return config


def save_config(config: Dict):
    kdcli_config_dir = Path.home() / ".kdcli"
    if not kdcli_config_dir.exists():
        kdcli_config_dir.mkdir()
    config_file = kdcli_config_dir / "config.json"
    with config_file.open(mode="w") as f:
        json.dump(config, f)


def get_random_body_temperature() -> float:
    return random.randint(364, 371) / 10.0


class KidsDiaryCLI:
    def __init__(self, config: Dict):
        if config is None or 'userToken' not in config:
            raise ValueError("Token does not exist!")
        self._config = config

    def get_draft_payload(self, date: datetime = today(),
                          message: str = "本日もよろしくお願いいたします",
                          food_menu: str = "Milk and bread",
                          pick_up_person: str = "Father",
                          photos=None,
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
        if photos is None:
            photos = []
        dt0am = datetime_0am(date)
        return {
            "childId": self._config['childIds'][0],
            "userToken": self._config['userToken'],
            "publishScheduleDate": epoch_millis(dt0am + publish_delta),
            "textContent": message,
            "photos": photos,
            "health": [{"healthStatus": "Health",
                        # randomly generated from 36.4 to 37.1
                        "temperature": f"{get_random_body_temperature()}",
                        "healthTime": str(epoch_millis(dt0am + health_time_delta))}],
            "sleep": [{"sleepTime": epoch_millis(dt0am + sleep_time_delta),
                       "awakeTime": epoch_millis((dt0am + awake_time_delta))}],
            "food": [{"foodMenu": food_menu, "foodTime": epoch_millis(dt0am + food_time_delta)}],
            "pickUpPerson": pick_up_person, "pickUpTime": epoch_millis(dt0am + pick_up_time_delta)}

    def get_all_photos(self):
        payload = {"userToken": self._config['userToken']}
        photo_list_response = post(path="album/photo/all", payload=payload)
        if photo_list_response.status_code == 200:
            data = photo_list_response.json()
            if data['totalHits'] > 0:
                return data['list']

    def list_photos(self):
        photos = self.get_all_photos()
        count = len(photos)
        logger.info(f"Found {count} photo(s):")
        for photo in photos:
            logger.info(f"{photo}")

    def get_last_photos(self, num_photos=1):
        logger.info(f"Getting last {num_photos} photo(s)")
        photos = self.get_all_photos()[0:num_photos]
        photo_urls = [photo['url'] for photo in photos]
        photo_urls_reversed = photo_urls[::-1]
        return photo_urls_reversed

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
        payload = {"childId": self._config['childIds'][0], "userToken": self._config['userToken'], 'draftId': draft_id}
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
        photos = helper.get_last_photos(args.use_last_photos)
        draft_payload = helper.get_draft_payload(
            date=date, message=message, food_menu=food_menu, pick_up_person=pick_up_person, photos=photos)
        logger.info(draft_payload)
        helper.create_or_update_draft(draft_payload=draft_payload)


def command_login(args):
    login_response = post(
        path="login", payload={"loginName": args.user, "password": args.password})
    if login_response.status_code == 200:
        login_response_json = login_response.json()
        config = {
            'userToken': login_response_json['userToken'], 'childIds': login_response_json['childIds'],
            'loginName': login_response_json['loginName']}
        save_config(config)
        logger.info(f"Login succeeded!")
    else:
        logger.error(f"Login failed!")


def command_logout(args):
    remove_config()
    logger.info(f"Logged out")


def command_version(args):
    logger.info(f"{__version__}")


def command_photo(args):
    config = load_config()
    if config is None:
        logger.error("Credentials not found! Please login.")
        sys.exit(1)
    else:
        logger.info(f"Logged in as {config['loginName']}")
    helper = KidsDiaryCLI(config)
    if args.list:
        helper.list_photos()


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
    parser_draft.add_argument(
        "-L", "--use-last-photos", default=0, type=int, choices=range(0, 3), help='Use last n photos')
    parser_draft.set_defaults(handler=command_draft)

    parser_login = subparsers.add_parser(
        'login', help='see `login -h`', formatter_class=ArgumentDefaultsHelpFormatter)
    parser_login.add_argument("-u", "--user", required=True)
    parser_login.add_argument("-p", "--password", required=True)
    parser_login.set_defaults(handler=command_login)

    parser_logout = subparsers.add_parser(
        'logout', help='see `logout -h`', formatter_class=ArgumentDefaultsHelpFormatter)
    parser_logout.set_defaults(handler=command_logout)

    parser_version = subparsers.add_parser(
        'version', help='see `version -h`', formatter_class=ArgumentDefaultsHelpFormatter)
    parser_version.set_defaults(handler=command_version)

    parser_photo = subparsers.add_parser(
        'photo', help='see `photo -h`', formatter_class=ArgumentDefaultsHelpFormatter)
    parser_photo.add_argument(
        "-l", "--list", action="store_true", help='List the photos')
    parser_photo.set_defaults(handler=command_photo)

    args = parser.parse_args()
    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
