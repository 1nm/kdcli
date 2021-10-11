# KidsDiary CLI

A CLI tool that helps manipulating KidsDiary from command line

## Usage

```
> ./kd.py draft -h
usage: kd.py draft [-h] -t TOKEN [-m MESSAGE] [-l] [-c]

optional arguments:
  -h, --help            show this help message and exit
  -t TOKEN, --token TOKEN
  -m MESSAGE, --message MESSAGE
                        Message to the teacher
  -l, --list            List the drafts
  -c, --create          Create a new draft
```


## Examples

### List the drafts
```
> ./kd.py draft -t $token -l
2021-10-08 02:43:50,448 - INFO: Found 1 draft(s), listing the first one ...
2021-10-08 02:43:50,521 - INFO: Current draft: {'draftId': 1584896, 'createAt': 1633622263000, 'publishScheduleDate': 1633649400000, 'textContent': 'This is a test draft', 'photos': [], 'items': {'avatarUrl': '', 'avatarUrlThumb': '', 'avatarUrlMiddle': '', 'avatarUrlLarge': '', 'photos': [], 'health': [{'healthStatus': 'Health', 'temperature': '36.5', 'healthTime': '1633648200000'}], 'sleep': [{'isTeacherDiary': False, 'childDataSleepId': None, 'sleepTime': 1633604400000, 'awakeTime': 1633647600000, 'teacherDiary': False}], 'food': [{'foodMenu': 'Milk and bread', 'foodTime': 1633648500000}], 'poop': [], 'pee': [], 'bath': [], 'nailCare': [], 'walking': [], 'pickUpPerson': 'Father', 'pickUpTime': 1633678200000, 'weight': '', 'height': '', 'roomId': '', 'roomName': '', 'childId': '', 'childName': '', 'feces': []}, 'diaryDate': 1633618800000}
```

### Create or replace a draft

```
./kd.py draft -t $TOKEN -c -m "This is a test draft"
```
