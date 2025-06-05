#pugoing_api.api.py
import asyncio

import aiohttp
import json
import logging
from datetime import datetime
from collections import defaultdict
from .const import selectedUrls, DEVELOPING
from .utils import LoggerUtility
from .error import DeviceOfflineError, NoPermissionError, PuGoingInvalidResponseError

lib_logger = LoggerUtility(name="lib_logger", log_level=logging.DEBUG)

async def fetch_device_by_yid(token, sn, yid) -> dict:
    data = {"sn": sn, "yid": yid}
    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                    selectedUrls["fetchDeviceByYid"], json=data, headers=headers, timeout=5
            ) as response:
                result = await response.json()
                if result.get("ack") == 1:
                    device_info = result["data"]["ackinfo"]
                    if isinstance(device_info, list) and len(device_info) > 0:
                        return device_info[0]
                    else:
                        raise PuGoingInvalidResponseError("查询设备状态时应答的数据为空")

                elif result.get("ack") == 0:
                    error_message = result.get("msg", "Unknown error")
                    if error_message == "主机不在线":
                        raise DeviceOfflineError()
                    elif error_message == "您没有此权限访问该主机":
                        raise NoPermissionError()
                    lib_logger.error(f"Request failed with message: {result.get('msg')}")
                else:
                    lib_logger.error(f"Request failed with message: {result.get('msg')}")
                    raise Exception(f"Request failed with message: {result.get('msg')}")
        except Exception as e:
            lib_logger.error(f"Error during fetch_device_by_yid: {e}")
            raise e
# async def fetch_device_by_yid(token, sn, yid) -> dict:
#     data = {"token": token, "sn": sn, "yid": yid}

#     async with aiohttp.ClientSession() as session:
#         try:
#             async with session.post(
#                     selectedUrls["fetchDeviceByYid"], json=data, timeout=5
#             ) as response:
#                 result = await response.json()
#                 if result.get("ack") == 1:
#                     device_info = result["data"]["ackinfo"]
#                     if isinstance(device_info, list) and len(device_info) > 0:
#                         return device_info[0]
#                     else:
#                         raise PuGoingInvalidResponseError("查询设备状态时应答的数据为空")

#                 elif result.get("ack") == 0:
#                     error_message = result.get("msg", "Unknown error")
#                     if error_message == "主机不在线":
#                         raise DeviceOfflineError()
#                     elif error_message == "您没有此权限访问该主机":
#                         raise NoPermissionError()
#                     lib_logger.error(f"Request failed with message: {result.get('msg')}")
#                 else:
#                     lib_logger.error(f"Request failed with message: {result.get('msg')}")
#                     raise Exception(f"Request failed with message: {result.get('msg')}")
#         except Exception as e:
#             lib_logger.error(f"Error during fetch_device_by_yid: {e}")
#             raise e

async def fetch_sn_list(token):
    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        async with session.post(
                selectedUrls["fetchSnList"], headers=headers, timeout=5
        ) as response:
            result = await response.json()

            if result.get("ack") == 1:
                devices = result["data"]["list"]
                return devices
            else:
                lib_logger.error(f"Request failed with message: {result.get('msg')}")
                raise Exception(f"Request failed with message: {result.get('msg')}")
            
# async def fetch_sn_list(token):
#     data = {"token": token}

#     async with aiohttp.ClientSession() as session:
#         async with session.post(
#                 selectedUrls["fetchSnList"], json=data, timeout=5
#         ) as response:
#             result = await response.json()

#             if result.get("ack") == 1:
#                 devices = result["data"]["list"]

#                 # Convert UNIX timestamp to human-readable date
#                 # for device in devices:
#                 #     device["first_bind_time_human"] = datetime.fromtimestamp(
#                 #         device["first_bind_time"]
#                 #     ).strftime("%Y-%m-%d %H:%M:%S")
#                 #     device["last_bind_time_human"] = datetime.fromtimestamp(
#                 #         device["last_bind_time"]
#                 #     ).strftime("%Y-%m-%d %H:%M:%S")
#                 #
#                 # # Sort devices by last_bind_time from high to low
#                 # devices.sort(key=lambda x: x["last_bind_time"], reverse=True)

#                 # Extract SN numbers and the sorted devices
#                 # sn_numbers = [device["sn"] for device in devices]

#                 return devices
#             else:
#                 lib_logger.error(f"Request failed with message: {result.get('msg')}")
#                 raise Exception(f"Request failed with message: {result.get('msg')}")

async def fetch_devices_by_room(token, sn, room_name):
    data = {"sn": sn, "roomname": room_name}
    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        async with session.post(
                selectedUrls["fetchDevicesByRoom"], json=data, headers=headers, timeout=5
        ) as response:
            result = await response.json()

            if result.get("ack") == 1:
                devices = result["data"]["list"]
                return devices
            else:
                lib_logger.error(f"Request failed with message: {result.get('msg')}")
                raise Exception(f"Request failed with message: {result.get('msg')}")

# async def fetch_devices_by_room(token, sn, room_name):
#     data = {"token": token, "sn": sn, "roomname": room_name}

#     async with aiohttp.ClientSession() as session:
#         async with session.post(
#                 selectedUrls["fetchDevicesByRoom"], json=data, timeout=5
#         ) as response:
#             result = await response.json()

#             if result.get("ack") == 1:
#                 devices = result["data"]["list"]

#                 return devices

#             else:
#                 lib_logger.error(f"Request failed with message: {result.get('msg')}")
#                 raise Exception(f"Request failed with message: {result.get('msg')}")

async def control_device(sn, fm, dvcm, dkey, yid, token, digv=None):
    data = {"sn": sn, "fm": fm, "dvcm": dvcm, "dkey": dkey, "yid": yid}
    headers = {"Authorization": f"Bearer {token}"}

    if digv is not None:
        data["digv"] = digv

    lib_logger.debug("control data: ", data)

    async with aiohttp.ClientSession() as session:
        async with session.post(
                selectedUrls["controlDevice"], json=data, headers=headers, timeout=5
        ) as response:
            result = await response.json()

            if result.get("ack") == 0:
                error_message = result.get("msg", "Unknown error")
                if error_message == "主机不在线":
                    raise DeviceOfflineError()
                elif error_message == "您没有此权限访问该主机":
                    raise NoPermissionError()
                lib_logger.error(f"Request failed with message: {result.get('msg')}")
            else:
                lib_logger.info("Device control successful:", result)

            return result
# async def control_device(sn, fm, dvcm, dkey, yid, token, digv=None):
#     data = {"sn": sn, "fm": fm, "dvcm": dvcm, "dkey": dkey, "yid": yid, "token": token}

#     if digv is not None:
#         data["digv"] = digv

#     lib_logger.debug("control data: ", data)

#     async with aiohttp.ClientSession() as session:
#         async with session.post(
#                 selectedUrls["controlDevice"], json=data, timeout=5
#         ) as response:
#             result = await response.json()

#             if result.get("ack") == 0:
#                 error_message = result.get("msg", "Unknown error")
#                 if error_message == "主机不在线":
#                     raise DeviceOfflineError()
#                 elif error_message == "您没有此权限访问该主机":
#                     raise NoPermissionError()
#                 lib_logger.error(f"Request failed with message: {result.get('msg')}")
#             else:
#                 lib_logger.info("Device control successful:", result)

#             return result

async def categorize_devices_by_panel(token, sn, room_name):
    devices = await fetch_devices_by_room(token, sn, room_name)
    categorized_devices = {}

    for device in devices:
        panel_type = device.get("dpanel", "Unknown")
        device["sn"] = sn
        if panel_type not in categorized_devices:
            categorized_devices[panel_type] = []

        categorized_devices[panel_type].append(device)

    return categorized_devices
# async def categorize_devices_by_panel(token, sn, room_name):
#     devices = await fetch_devices_by_room(token, sn, room_name)
#     categorized_devices = {}

#     for device in devices:
#         panel_type = device.get("dpanel", "Unknown")
#         device["sn"] = sn
#         if panel_type not in categorized_devices:
#             categorized_devices[panel_type] = []

#         categorized_devices[panel_type].append(device)

#     return categorized_devices

async def fetch_sn_and_room_list(token):
    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        async with session.post(
                selectedUrls["fetchSnAndRoomList"], headers=headers, timeout=5
        ) as response:
            result = await response.json()

            if result.get("ack") == 1:
                return result["data"]["list"]
            else:
                lib_logger.error(f"Request failed with message: {result.get('msg')}")
                raise Exception(f"Request failed with message: {result.get('msg')}")
            
# async def fetch_sn_and_room_list(token):
#     data = {"token": token}

#     async with aiohttp.ClientSession() as session:
#         async with session.post(
#                 selectedUrls["fetchSnAndRoomList"], json=data, timeout=5
#         ) as response:
#             result = await response.json()

#             if result.get("ack") == 1:
#                 return result["data"]["list"]
#             else:
#                 lib_logger.error(f"Request failed with message: {result.get('msg')}")
#                 raise Exception(f"Request failed with message: {result.get('msg')}")


def merge_dicts(dict_list):
    merged_dict = defaultdict(list)
    for d in dict_list:
        for key, value in d.items():
            # 如果键不存在，会自动添加这个键并初始化为空列表，然后直接扩展
            merged_dict[key].extend(value)
    return dict(merged_dict)


async def process_rooms(token):
    sn_room_list = await fetch_sn_and_room_list(token)
    lib_logger.debug(
        "Retrieved sn_room_list:",
        json.dumps(sn_room_list, ensure_ascii=False),
    )

    if not sn_room_list or len(sn_room_list) < 1:
        lib_logger.debug("No SN/Room List found")
        return {"event": {"header": None, "payload": None}}  # 模拟返回值
    devices_all = []
    for sn_room in sn_room_list:
        sn = sn_room["sn"]
        room_list = sn_room["room"]

        lib_logger.debug("Room List:", json.dumps(room_list, ensure_ascii=False))
        lib_logger.debug("SN:", sn)

        for room in room_list:
            lib_logger.debug(f"Processing room: {room['name']}")
            try:
                devices = await categorize_devices_by_panel(
                    token, sn, room['name']
                )
                lib_logger.debug(
                    "Retrieved devices for room:",
                    json.dumps(devices, ensure_ascii=False),
                )
                if not devices:
                    lib_logger.debug(f"No devices found in room: {room['name']}")
                    continue
                devices_all.append(devices)

            except Exception as e:
                lib_logger.error(f"Error processing room {room['name']}: {str(e)}")

    return merge_dicts(devices_all)


async def get_devices_by_hotel_room_name(name: str, token: str) -> dict:
    """
    根据酒店房间名和token获取房间下所有设备,
    先查询token下的所有管家, 找到名称相同的管家的sn号,
    然后查询该sn下的所有设备
    :param name: 酒店的房间名, 例如501, 502这种, 不应该是客厅这种
    :param token:
    :return:
    """
    # 使用 asyncio.gather 同时发送 fetch_sn_list 和 fetch_sn_and_room_list 请求
    sn_list, sn_room_list = await asyncio.gather(fetch_sn_list(token), fetch_sn_and_room_list(token))

    room_num: str
    sn: str = ""
    for item in sn_list:
        room_name = item.get("name", "")
        if not isinstance(room_name, str):
            continue
        if room_name.__contains__("|"):
            room_num = room_name.split("|")[1]
        else:
            room_num = room_name
        if room_num == name:
            sn = item.get("sn")
            break

    lib_logger.debug(
        "Retrieved sn_room_list:",
        json.dumps(sn_room_list, ensure_ascii=False),
    )

    if not sn_room_list or len(sn_room_list) < 1:
        lib_logger.debug("No SN/Room List found")
        return {"event": {"header": None, "payload": None}}  # 模拟返回值

    room_list = []
    for item in sn_room_list:
        if item.get("sn") == sn:
            room_list = item.get("room")
            break

    lib_logger.debug("Room List:", json.dumps(room_list, ensure_ascii=False))
    lib_logger.debug("SN:", sn)

    devices_all = []
    # 使用 asyncio.gather 并行查询房间下的所有设备
    tasks = [
        categorize_devices_by_panel(token, sn, room['name'])
        for room in room_list
    ]

    try:
        results = await asyncio.gather(*tasks)
        for i, devices in enumerate(results):
            room_name = room_list[i].get('name')
            lib_logger.debug(
                f"Retrieved devices for room {room_name}:",
                json.dumps(devices, ensure_ascii=False),
            )
            if not devices:
                lib_logger.debug(f"No devices found in room: {room_name}")
                continue
            devices_all.append(devices)
    except Exception as e:
        lib_logger.error(f"Error processing rooms: {str(e)}")

    return merge_dicts(devices_all)


# async def get_devices_by_hotel_room_name(name: str, token: str) -> dict:
#     """
#     根据酒店房间名和token获取房间下所有设备,
#     先查询token下的所有管家, 找到名称相同的管家的sn号,
#     然后查询该sn下的所有设备
#     :param name: 酒店的房间名, 例如501, 502这种, 不应该是客厅这种
#     :param token:
#     :return:
#     """
#     sn_list = await fetch_sn_list(token)
#     room_num: str
#     sn: str = ""
#     for item in sn_list:
#         room_name = item.get("name", "")
#         if not isinstance(room_name, str):
#             continue
#         if room_name.__contains__("|"):
#             room_num = room_name.split("|")[1]
#         else:
#             room_num = room_name
#         if room_num == name:
#             sn = item.get("sn")
#             break
#
#     sn_room_list = await fetch_sn_and_room_list(token)
#     lib_logger.debug(
#         "Retrieved sn_room_list:",
#         json.dumps(sn_room_list, ensure_ascii=False),
#     )
#
#     if not sn_room_list or len(sn_room_list) < 1:
#         lib_logger.debug("No SN/Room List found")
#         return {"event": {"header": None, "payload": None}}  # 模拟返回值
#     room_list = []
#     for item in sn_room_list:
#         if item.get("sn") == sn:
#             room_list = item.get("room")
#             break
#
#     lib_logger.debug("Room List:", json.dumps(room_list, ensure_ascii=False))
#     lib_logger.debug("SN:", sn)
#
#     devices_all = []
#     for room in room_list:
#         lib_logger.debug(f"Processing room: {room['name']}")
#         try:
#             devices = await categorize_devices_by_panel(
#                 token, sn, room['name']
#             )
#             lib_logger.debug(
#                 "Retrieved devices for room:",
#                 json.dumps(devices, ensure_ascii=False),
#             )
#             if not devices:
#                 lib_logger.debug(f"No devices found in room: {room['name']}")
#                 continue
#             devices_all.append(devices)
#
#         except Exception as e:
#             lib_logger.error(f"Error processing room {room['name']}: {str(e)}")
#
#     return merge_dicts(devices_all)


async def login(username: str, password: str):
    data = {"account": username, "pwd": password}

    async with aiohttp.ClientSession() as session:
        async with session.post(selectedUrls["login"], json=data, timeout=5) as response:
            if response.status != 200:
                lib_logger.error("Login request failed with status code: %s", response.status)
                raise Exception(f"Login request failed with status code: {response.status}")

            result = await response.json()

            if result.get("ack") == 1:
                return result["data"]["token"]
            else:
                lib_logger.error(f"Login failed with message: {result.get('msg')}")
                raise Exception(f"Login failed with message: {result.get('msg')}")
