# KidsDiary CLI

A CLI tool that helps manipulating KidsDiary from command line

## Usage

```bash
docker run --rm -it -e USERNAME=XXX -e PASSWORD=XXX x1nm/kd <command>
```

```
usage: kd [-h] {draft,version} ...

KidsDiary CLI

positional arguments:
  {draft,login,logout,version}
    draft               see `draft -h`
    version             see `version -h`

optional arguments:
  -h, --help            show this help message and exit
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
  -L {0,1,2}, --use-last-photos {0,1,2}
                        Use last n photos (default: 0)
```

## Examples

### List the drafts

```bash
> docker run --rm -it -e USERNAME=XXX -e PASSWORD=XXX x1nm/kd draft -l
```

```
Logged in as ???
Found 1 draft(s):
{'draftId': 1595487, 'createAt': 1634224574000, 'publishScheduleDate': 1634254200000, 'textContent': 'This is a test draft', 'photos': [], 'items': {'avatarUrl': '', 'avatarUrlThumb': '', 'avatarUrlMiddle': '', 'avatarUrlLarge': '', 'photos': [], 'health': [{'healthStatus': 'Health', 'temperature': '36.8', 'healthTime': '1634253000000'}], 'sleep': [{'isTeacherDiary': False, 'childDataSleepId': None, 'sleepTime': 1634209200000, 'awakeTime': 1634252400000, 'teacherDiary': False}], 'food': [{'foodMenu': 'Milk and bread', 'foodTime': 1634253300000}], 'poop': [], 'pee': [], 'bath': [], 'nailCare': [], 'walking': [], 'pickUpPerson': 'Father', 'pickUpTime': 1634283000000, 'weight': '', 'height': '', 'roomId': '', 'roomName': '', 'childId': '', 'childName': '', 'feces': []}, 'diaryDate': None}
```

### Create or replace a draft

```bash
> docker run --rm -it -e USERNAME=XXX -e PASSWORD=XXX x1nm/kd draft -L 1 -c -m "This is a test draft"
```

```
Logged in as ???
Replacing draft 1595487 ...
Draft 1595487 updated.
```
