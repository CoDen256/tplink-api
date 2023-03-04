# This is a sample Python script.
import requests

host = "192.168.0.1"
username = "admin"
password = "admin"


def get_dhcp_settings(host, username, password):
    path = "cgi?5"
    url = f"http://{host}/{path}"

    headers = {
        "Content-Type": "text/plain",
        "Cookie": "Authorization=Basic YWRtaW46YWRtaW4=",
        "Host": "192.168.0.1",
        "Origin": "http:/192.168.0.1",
        "Referer": "http:/192.168.0.1/mainFrame.htm",
        "Sec-GPC": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    }
    payload = "[LAN_HOST_ENTRY#0,0,0,0,0,0#0,0,0,0,0,0]0,4\nleaseTimeRemaining\nMACAddress\nhostName\nIPAddress"
    print(payload)
    # return requests.post(url, data=payload, headers=headers)

# https://github.com/developerdost/tp-link
result = get_dhcp_settings(host, username, password)
print(result.status_code)
print(result.content)
