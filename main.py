import json
import os
import random
import time
from bs4 import BeautifulSoup
import requests
import subprocess

# Resize window and set title
os.system('mode con: cols=47 lines=9')
os.system('title oguser Bumper!')

info_List = []
try:
    with open("./data/info.json", "r") as f:
        information = json.load(f)

    for infoPiece in information:
        info_List.append(infoPiece)

except Exception as errorImportInfo:
    print(f'INCORRECT FORMAT IN "info.json" FILE')

userUsername = info_List[0]["username"]
userPassword = info_List[0]["password"]
bumpingThread = info_List[0]["threadLink"]
bumpMsg = info_List[0]["bumpMessage"]
is2FA = info_List[0]["is2FA"]


def run_command_in_specific_directory(directory, command):
    original_dir = os.getcwd()

    try:
        os.chdir(directory)

        result = subprocess.run(command, shell=True,
                                capture_output=True, text=True)

        if result.returncode == 0:
            print("Command executed successfully!")
        else:
            print("Error executing the command:")
            print(result.stderr)

    finally:
        os.chdir(original_dir)


def parse_cf_clearance_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    if "clearance_cookies" in data and len(data["clearance_cookies"]) > 0:
        last_cookie = data["clearance_cookies"][-1]
        if "cf_clearance" in last_cookie:
            cf_clearance_value = last_cookie["cf_clearance"]
            return cf_clearance_value
    return None


def parse_cookie():
    directory_path = r'C:/Users/zardo/Desktop/oguserBumper/CF-Clearance-Scraper'
    command = 'py main.py -d -v -f cookies.json https://oguser.gg'
    run_command_in_specific_directory(directory_path, command)
    file_path = os.path.join(directory_path, 'cookies.json')
    cf_clearance = parse_cf_clearance_from_json(file_path)
    if cf_clearance:
        print("Parsed cf_clearance value")
    else:
        print("cf_clearance value not found or JSON content is invalid.")
    return cf_clearance


def main(cf_clearance):
    while True:
        session = requests.Session()
        session.cookies.update({
            "cf_clearance": str(cf_clearance)
        })
        session.headers.update({
            "Te": "trailers",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Connection": "close",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.5",
            "Sec-Fetch-Mode": "navigate"
        })

        response = session.get("https://oguser.com/")

        if (response.status_code == 200 and str(response.url) == 'https://oguser.com/'):
            print(f'Connected to oguser.com!')

            paramsGet = {"action": "login"}

            response = session.get(
                "https://oguser.com/member.php", params=paramsGet)

            if (response.status_code == 200 and str(response.url) == 'https://oguser.com/member.php?action=login'):
                soup = BeautifulSoup(response.content, "html.parser")
                my_post_key_val = soup.find(attrs={"name": "my_post_key"})
                my_post_key = my_post_key_val["value"]

                if is2FA == True:
                    code = input(f'Enter 2FA Code: ')
                else:
                    code = ''

                paramsPost = {
                    "remember": "yes",
                    "2facode": f"{code}",
                    "password": userPassword,
                    "action": "do_login",
                    "my_post_key": my_post_key,
                    "url": "https://oguser.com/",
                    "username": userUsername
                }

                response = session.post(
                    "https://oguser.com/member.php", data=paramsPost)

                if (response.status_code == 200 and str(response.url) == 'https://oguser.com/'):
                    print(
                        f"Log in to flipd user @{paramsPost['username']} success!")

                    response = session.get(bumpingThread)

                    if (response.status_code == 200 and str(response.url) == str(bumpingThread)):
                        print(f'Got thread successfully!')

                        soup2 = BeautifulSoup(response.content, "html.parser")

                        site_title = soup2.find("title").get_text()

                        my_post_key_val = soup2.find(
                            attrs={"name": "my_post_key"})
                        mPostKey = my_post_key_val["value"]

                        postHashVal = soup2.find(attrs={"name": "posthash"})
                        mPostHash = postHashVal["value"]

                        lastPidVal = soup2.find(attrs={"name": "lastpid"})
                        mLastPid = lastPidVal["value"]

                        fromPageVal = soup2.find(attrs={"name": "from_page"})
                        mFromPage = fromPageVal["value"]

                        tidVal = soup2.find(attrs={"name": "tid"})
                        mTid = tidVal["value"]

                        bumpCount = 0
                        while True:
                            bumpMsg2 = f'{random.choice(bumpMsg)}'

                            paramsGet = {"processed": "1", "tid": mTid}
                            paramsPost = {
                                "method": "quickreply",
                                "subject": f"RE: {site_title}",
                                "posthash": mPostHash,
                                "lastpid": mLastPid,
                                "action": "do_newreply",
                                "from_page": mFromPage,
                                "my_post_key": mPostKey,
                                "message": bumpMsg2,
                                "tid": mTid,
                                "postoptions%5Bsignature%5D": "1",
                                "quoted_ids": ""
                            }
                            response = session.post(
                                "https://oguser.com/newreply.php", data=paramsPost, params=paramsGet)

                            if ("pid" in str(response.url) and response.status_code == 200):
                                bumpCount += 1
                                print(f'Bumped message [#{bumpCount}]')
                                time.sleep(930)

                            else:
                                print(f'Failed to bump message',
                                      response.status_code, response.url)
                                break

                    else:
                        print(f'Could not get thread',
                              response.status_code, response.url)
                        break

                else:
                    print(f'Could not log in to [{paramsPost["username"]}]',
                          response.status_code, response.url)
                    break

            else:
                print(f'Could not get login page',
                      response.status_code, response.url)
                break

        else:
            print(f'Failed to connect to oguser.com',
                  response.status_code, response.url)
            break


if __name__ == '__main__':
    while True:
        cookie = parse_cookie()
        main(cookie)

        if not main:
            cookie = parse_cookie()
            main(cookie)
