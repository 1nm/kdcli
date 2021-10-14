# KidsDiary CLI

A CLI tool that helps manipulating KidsDiary from command line

## Install
```
curl -LO https://github.com/1nm/kdcli/releases/latest/download/kd
sudo install -o root -g root -m 0755 kd /usr/local/bin/kd
```

## Usage

```
usage: kd [-h] {draft,login,logout,version} ...

KidsDiary CLI

positional arguments:
  {draft,login,logout,version}
    draft               see `draft -h`
    login               see `login -h`
    logout              see `logout -h`
    version             see `version -h`

optional arguments:
  -h, --help            show this help message and exit
```

### Login

```
usage: kd login [-h] -u USER -p PASSWORD

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER
  -p PASSWORD, --password PASSWORD
```

### Draft

```
usage: kd draft [-h] [-l] [-c] [-T] [-m MESSAGE] [-p PICK_UP_PERSON] [-f FOOD_MENU]

optional arguments:
  -h, --help            show this help message and exit
  -l, --list            List the drafts (default: False)
  -c, --create          Create a new draft (default: False)
  -T, --today           Publish the draft today (default: False)
  -m MESSAGE, --message MESSAGE
                        Message to the teacher (default: 本日もよろしくお願いします)
  -p PICK_UP_PERSON, --pick-up-person PICK_UP_PERSON
                        Pick-up person (default: Father)
  -f FOOD_MENU, --food-menu FOOD_MENU
                        Food menu (default: Milk and bread)
```

## Examples

### Login

```bash
> kd login -u YOUR_USER_NAME -p YOUR_PASSWORD
```

```
Login succeeded!
```

```
Logged out
```

### List the drafts

```bash
> kd draft -l
```

```
Logged in as ???
Found 1 draft(s):
{'draftId': 1595487, 'createAt': 1634224574000, 'publishScheduleDate': 1634254200000, 'textContent': 'This is a test draft', 'photos': [], 'items': {'avatarUrl': '', 'avatarUrlThumb': '', 'avatarUrlMiddle': '', 'avatarUrlLarge': '', 'photos': [], 'health': [{'healthStatus': 'Health', 'temperature': '36.8', 'healthTime': '1634253000000'}], 'sleep': [{'isTeacherDiary': False, 'childDataSleepId': None, 'sleepTime': 1634209200000, 'awakeTime': 1634252400000, 'teacherDiary': False}], 'food': [{'foodMenu': 'Milk and bread', 'foodTime': 1634253300000}], 'poop': [], 'pee': [], 'bath': [], 'nailCare': [], 'walking': [], 'pickUpPerson': 'Father', 'pickUpTime': 1634283000000, 'weight': '', 'height': '', 'roomId': '', 'roomName': '', 'childId': '', 'childName': '', 'feces': []}, 'diaryDate': None}
```

### Create or replace a draft

```bash
> kd draft -c -m "This is a test draft"
```

```
Logged in as ???
Replacing draft 1595487 ...
Draft 1595487 updated.
```
