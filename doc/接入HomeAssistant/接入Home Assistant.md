# 接入Home Assistant

## 好处

接入Home Assistant, 用户可以享受到Home Assistant丰富的生态. Home Assistant也支持集成Alexa, Google Assistant, HomeKit Bridge这些.

![image-20240828152124749](assets/image-20240828152124749.png)

Home Assistant本身是本地运行的, 如果要让它能在公网上访问, 需要用户自行准备公网环境.

不过Home Assistant也提供一共可以从云端访问的版本, 需要用户付费. 

从提供智能家居服务的角度来说, 可以把租云服务这些的成本直接省去, 如果用户想支持通过Alexa这些控制, 多买一个[Home Assistant Cloud](https://www.nabucasa.com)会员就行了, 接入到HA之后相当于接入了国内外各大厂家, 一举多得.

## 演示

米家版本的接入到home assistant

https://sspai.com/post/94916

## 接入到HA

### 接入到HA能做什么

- 让HA系统可以控制接入的设备
- 如果是语音主机这种, 也可以控制以及接入到HA的设备

### 接入的方式

类似于米家的方式, 接入到HA可以通过实现一个HA的"集成", 

https://developers.home-assistant.io/docs/creating_integration_file_structure/

### 一个HA的集成可以做什么?

- 让HA系统可以控制自己的设备
- 让HA系统可以控制别的厂家的设备
- 让别的厂家的设备可以控制自己的设备

### 用户如何使用?

#### 已经把插件发布到HA的情况

用户进入到HA的管理界面, 选择集成, 添加集成

![image-20250605100544106](assets/image-20250605100544106.png)

搜索之后就可以添加了

![image-20250605101233583](assets/image-20250605101233583.png)

![image-20250606164334751](assets/image-20250606164334751.png)



![image-20250606164406281](assets/image-20250606164406281.png)



![image-20250606164423796](assets/image-20250606164423796.png)

#### 没发布插件到HA的情况

如果Home Assistant主机是我们提供给客户的, 可以在主机里直接预装程序, 就不用发布了.

或者是有HA主机的权限, 可以直接把集成copy到ha的custom_components路径下, 也不需要再发布了

其余流程和上文中的一样



### 实现方式

#### 实现集成

在根目录下新建

官方有些示例和文档可以用

https://github.com/ludeeus/integration_blueprint.git



https://github.com/home-assistant/example-custom-config/tree/master



米家也实现了开源的组件, 可以直接照葫芦画瓢

https://github.com/XiaoMi/ha_xiaomi_home.git

#### 测试功能

可以用pytest做测试

示例

https://github.com/MatthewFlamm/pytest-homeassistant-custom-component.git

#### 发布到HA

https://hacs.xyz/docs/publish/start/

### 发布的方式

#### 发布组件, 但是不开源

#### 发布组件, 也开源

#### 发布组件, 开源, 并且把组件也推送到HA官方



## 搭建环境

https://developers.home-assistant.io/docs/development_environment

这个搭环境的时候如果网不好很大概率失败报错类似于:

```
ith git rev-parse --is-inside-work-tree
Dockerfile-with-features:1
--------------------
   1 | >>> # syntax=docker/dockerfile:1.4
   2 |     ARG _DEV_CONTAINERS_BASE_IMAGE=placeholder
   3 |     FROM mcr.microsoft.com/devcontainers/python:1-3.12 AS dev_container_auto_added_stage_label
--------------------
ERROR: failed to solve: failed to resolve source metadata for docker.io/docker/dockerfile:1.4: failed to do request: Head "https://registry-1.docker.io/v2/docker/dockerfile/manifests/1.4": net/http: TLS handshake timeout
[41171 ms] Error: Command failed: docker buildx build --load --build-arg BUILDKIT_INLINE_CACHE=1 -f /tmp/devcontainercli-root/container-features/0.76.0-1749024633379/Dockerfile-with-features -t vsc-pugoing-94f1d7d2a6d8235df5113ab9048f56d19578beb43ff00013939cc3b388823136 --target dev_containers_target_stage --build-context dev_containers_feature_content_source=/tmp/devcontainercli-root/container-features/0.76.0-1749024633379 --build-arg _DEV_CONTAINERS_BASE_IMAGE=dev_container_auto_added_stage_label --build-arg _DEV_CONTAINERS_IMAGE_USER=vscode --build-arg _DEV_CONTAINERS_FEATURE_CONTENT_SOURCE=dev_container_feature_content_temp /workspaces/pugoing
[41171 ms]     at y6 (/root/.vscode-remote-containers/dist/dev-containers-cli-0.413.0/dist/spec-node/devContainersSpecCLI.js:468:1933)
[41172 ms]     at async dw (/root/.vscode-remote-containers/dist/dev-containers-cli-0.413.0/dist/spec-node/devContainersSpecCLI.js:467:1886)
[41172 ms]     at async Ix (/root/.vscode-remote-containers/dist/dev-containers-cli-0.413.0/dist/spec-node/devContainersSpecCLI.js:467:608)
[41172 ms]     at async Y6 (/root/.vscode-remote-containers/dist/dev-containers-cli-0.413.0/dist/spec-node/devContainersSpecCLI.js:484:3842)
[41172 ms]     at async BC (/root/.vscode-remote-containers/dist/dev-containers-cli-0.413.0/dist/spec-node/devContainersSpecCLI.js:484:4957)
[41172 ms]     at async p7 (/root/.vscode-remote-containers/dist/dev-containers-cli-0.413.0/dist/spec-node/devContainersSpecCLI.js:665:202)
[41172 ms]     at async d7 (/root/.vscode-remote-containers/dist/dev-containers-cli-0.413.0/dist/spec-node/devContainersSpecCLI.js:664:14804)
[41172 ms]     at async /root/.vscode-remote-containers/dist/dev-containers-cli-0.413.0/dist/spec-node/devContainersSpecCLI.js:484:1188
[41186 ms] Exit code 1
[41186 ms] Start: Run: docker rm -f 45f5a6d810d7689d6b2414bea30426d5cbe183c1b9c1b3f4b45dbc367d29ce3c
[41189 ms] Command failed: node /root/.vscode-remote-containers/dist/dev-containers-cli-0.413.0/dist/spec-node/devContainersSpecCLI.js up --container-session-data-folder /tmp/devcontainers-ff41f137-3c7f-4c6e-92ef-b077658272ea1749024610177 --workspace-folder /workspaces/pugoing --workspace-mount-consistency cached --gpu-availability detect --id-label vsch.local.repository=https://github.com/run02/pugoing.git --id-label vsch.local.repository.volume=pugoing-3c6e501dfbef7b0088aa9435dab9d67bd0256ac0b97e956dd09f450734ae12b9 --id-label vsch.local.repository.folder=pugoing --id-label devcontainer.config_file=/workspaces/pugoing/.devcontainer/devcontainer.json --log-level debug --log-format json --config /workspaces/pugoing/.devcontainer/devcontainer.json --override-config /tmp/devcontainer-21f23806-7c47-489d-b15b-bf59d6eca5a3.json --default-user-env-probe loginInteractiveShell --mount type=volume,source=pugoing-3c6e501dfbef7b0088aa9435dab9d67bd0256ac0b97e956dd09f450734ae12b9,target=/workspaces,external=true --mount type=volume,source=vscode,target=/vscode,external=true --mount type=bind,source=\\wsl.localhost\Ubuntu-22.04\mnt\wslg\runtime-dir\wayland-0,target=/tmp/vscode-wayland-f24c1f31-24f3-4cfc-9ce1-f2cda7be4055.sock --skip-post-create --update-remote-user-uid-default off --mount-workspace-git-root --terminal-columns 110 --terminal-rows 31 --include-configuration --include-merged-configuration
[41189 ms] Exit code 1
[41409 ms] Container server terminated (code: 137, signal: null).
[41409 ms] Container server terminated. Reconnecting in 5 seconds...
[46422 ms] Start: Container: Reconnecting Dev Container server
[46422 ms] Start: Run in container: /bin/sh
[46589 ms] Container server: Error response from daemon: No such container: 45f5a6d810d7689d6b2414bea30426d5cbe183c1b9c1b3f4b45dbc367d29ce3c
[46592 ms] Container server terminated (code: 1, signal: null).
[46592 ms] Container server terminated early. Not reconnecting.
[46592 ms] Reconnecting Dev Container server failed: Container server terminated (code: 1, signal: null).

```

配网这些太麻烦了

先用Linux搭环境

### 搭完整的开发环境

官方要求用python3.13, 为了不和Ubuntu系统上默认的python3冲突, 使用min conda来配置环境

#### 安装Miniconda

https://www.anaconda.com/docs/getting-started/miniconda/install#linux

#### 安装依赖

官方提供的是基于venv的, 但是要求要python>=3.13

```
script/setup
```

一般系统上的python不是这么高的版本,  这里用的conda, 

先用conda创建环境, 然后把setup脚本里的venv以外的复制出来执行即可

#### 运行测试

```
hass -c config
```

打开http://localhost:8123/, 能正常用说明配置成功

### 适用于集成的开发环境

#### 克隆仓库

```
git clone https://github.com/ludeeus/integration_blueprint.git
```

#### 安装Miniconda

https://www.anaconda.com/docs/getting-started/miniconda/install#linux

#### 创建环境

```sh
conda create -n ha python=3.13 -y
```

激活环境, 安装uv, uv装包比pip快很多, ha这种的依赖很多还是用uv来装节省时间

```sh
conda activate ha
pip install uv
```

#### 安装依赖

还有些是动态安装的依赖, 运行的第一次安装, 网不好的话装不上, 为了防止网不好, 先把界面装上方便后续操作

```
uv pip install home-assistant-frontend==20250214.0
```



```
uv pip install -r requirements.txt
```

#### 运行测试

这个时候还是网络要好, 要不然运行的时候动态的装包, 装不上有些就运行不了

```
scripts/develop
```

## 实现认证流程

这个也支持标准的OAuth2流程, 也可以用之前Alexa配置好的授权服务器,

## 接入灯光

### 接入普通的灯光

灯光类的是一样的

```python
import aiohttp
from homeassistant.components.light import LightEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .pugoing_api.pugoing_api import (
    process_rooms,
    get_global_token,
    control_device,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Awesome Light platform."""

    devices = await process_rooms(get_global_token())
    lamps = devices.get("Lamp", [])
    light_entities = [
        SimpleLight(
            lamp.get("dname", "no name"), lamp.get("sn", "no sn"), lamp.get("yid", "no yid")
        )
        for lamp in lamps
    ]

    add_entities(light_entities)


class SimpleLight(LightEntity):
    def __init__(self, name, sn, yid):
        self._name = name
        self._sn = sn
        self._yid = yid
        self._state = False

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._state

    async def async_turn_on(self, **kwargs):
        """Turn the light on."""
        async with aiohttp.ClientSession() as session:
            token = get_global_token()  # 从全局变量获取 token
            await control_device(
                self._sn, "uip", "", "LAMP_OPEN", self._yid, token, session
            )
            self._state = True
            self.schedule_update_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the light off."""
        async with aiohttp.ClientSession() as session:
            token = get_global_token()  # 从全局变量获取 token
            await control_device(
                self._sn, "uip", "", "LAMP_CLOSE", self._yid, token, session
            )
            self._state = False
            self.schedule_update_ha_state()

```

### 接入调光调色灯

https://developers.home-assistant.io/docs/core/entity/light/

## 接入窗帘类

https://developers.home-assistant.io/docs/core/entity/cover/#set-cover-position

## 空调

https://developers.home-assistant.io/docs/core/entity/climate/

## 发现设备

https://developers.home-assistant.io/docs/core/entity/

https://developers.home-assistant.io/docs/core/entity/#lifecycle-hooks

async_setup_entry

## 更新状态



## 反向控制

![image-20250606164116185](assets/image-20250606164116185.png)

用户可以创建一个令牌, 持有令牌的可以和HA系统交互,

可以直接控制HA系统内的设备

也可以直接把用户的语音指令发给HA, HA解析之后控制, 返回结果,

示例如下:

```python

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjNjYzM2Q0YjRlNjQ0ZTY2OWFlNzBkODdjZTIyMWEwNiIsImlhdCI6MTc0OTE4ODcwOSwiZXhwIjoyMDY0NTQ4NzA5fQ.FDrV6K9xvdPA0ojC8TSwL9DQIqPl9NoBPnEjuZvDtEE"

import requests
import json
import time

# 配置
HA_URL = "http://192.168.4.1:8123"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def list_lights():
    """列出所有灯实体"""
    resp = requests.get(f"{HA_URL}/api/states", headers=HEADERS)
    resp.raise_for_status()
    all_states = resp.json()

    lights = [e for e in all_states if e["entity_id"].startswith("light.")]
    print("发现的灯有：")
    for light in lights:
        print(f"- {light['entity_id']} (状态: {light['state']})")

    print("\n✅ 原始 JSON 返回内容（部分）：")
    print(json.dumps(lights, indent=2, ensure_ascii=False))
    return lights

def turn_on_light(entity_id):
    """打开指定灯"""
    resp = requests.post(
        f"{HA_URL}/api/services/light/turn_on",
        headers=HEADERS,
        json={"entity_id": entity_id}
    )
    resp.raise_for_status()
    print(f"\n💡 已尝试打开灯：{entity_id}")
    print("✅ 调用返回内容：")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))

def send_text_command(text):
    """通过文本指令控制 HA"""
    resp = requests.post(
        f"{HA_URL}/api/conversation/process",
        headers=HEADERS,
        json={"text": text, "language": "zh"}
    )
    resp.raise_for_status()
    print(f"\n📨 已发送指令：{text}")
    print("✅ 返回内容：")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    # 用文字控制灯
    lights = list_lights()
    if lights:
        # first_light = lights[0]["entity_id"]
        first_light = 'light.she_deng'
        turn_on_light(first_light)
    else:
        print("❌ 未找到任何灯设备。")

    send_text_command("打开顶灯")
    time.sleep(2)
    send_text_command("关闭顶灯")


```

运行结果:

```
(ha-env) ➜  test git:(dev) python3 test_ha.py
发现的灯有：
- light.she_deng (状态: off)
- light.ding_deng (状态: off)
- light.bi_deng (状态: off)

✅ 原始 JSON 返回内容（部分）：
[
  {
    "entity_id": "light.she_deng",
    "state": "off",
    "attributes": {
      "supported_color_modes": [
        "onoff"
      ],
      "color_mode": null,
      "sn": "10D07A46C664",
      "panel": "Lamp",
      "room": "客厅",
      "online": "1",
      "attribution": "Data provided by http://jsonplaceholder.typicode.com/",
      "friendly_name": "射灯",
      "supported_features": 0
    },
    "last_changed": "2025-06-06T05:59:35.698531+00:00",
    "last_reported": "2025-06-06T06:00:04.528674+00:00",
    "last_updated": "2025-06-06T05:59:35.698531+00:00",
    "context": {
      "id": "01JX1X5GQTTQEE4CW4N5VKSR3X",
      "parent_id": null,
      "user_id": "7b79ba782c64477daa2b1c3e61586337"
    }
  },
  {
    "entity_id": "light.ding_deng",
    "state": "off",
    "attributes": {
      "supported_color_modes": [
        "onoff"
      ],
      "color_mode": null,
      "sn": "10D07A46C664",
      "panel": "Lamp",
      "room": "客厅",
      "online": "1",
      "attribution": "Data provided by http://jsonplaceholder.typicode.com/",
      "friendly_name": "顶灯",
      "supported_features": 0
    },
    "last_changed": "2025-06-06T07:58:10.074680+00:00",
    "last_reported": "2025-06-06T08:34:49.635756+00:00",
    "last_updated": "2025-06-06T07:58:10.074680+00:00",
    "context": {
      "id": "01JX23YMA493YYMB4WNN5E90PS",
      "parent_id": null,
      "user_id": "7b79ba782c64477daa2b1c3e61586337"
    }
  },
  {
    "entity_id": "light.bi_deng",
    "state": "off",
    "attributes": {
      "supported_color_modes": [
        "onoff"
      ],
      "color_mode": null,
      "sn": "10D07A46C664",
      "panel": "Lamp",
      "room": "客厅",
      "online": "1",
      "attribution": "Data provided by http://jsonplaceholder.typicode.com/",
      "friendly_name": "壁灯",
      "supported_features": 0
    },
    "last_changed": "2025-06-06T08:06:12.386649+00:00",
    "last_reported": "2025-06-06T08:34:49.636039+00:00",
    "last_updated": "2025-06-06T08:06:12.386649+00:00",
    "context": {
      "id": "01JX24DBBH4K5MN01JCVKC1WXR",
      "parent_id": null,
      "user_id": "7b79ba782c64477daa2b1c3e61586337"
    }
  }
]

💡 已尝试打开灯：light.she_deng
✅ 调用返回内容：
[
  {
    "entity_id": "light.she_deng",
    "state": "on",
    "attributes": {
      "supported_color_modes": [
        "onoff"
      ],
      "color_mode": "onoff",
      "sn": "10D07A46C664",
      "panel": "Lamp",
      "room": "客厅",
      "online": "1",
      "attribution": "Data provided by http://jsonplaceholder.typicode.com/",
      "friendly_name": "射灯",
      "supported_features": 0
    },
    "last_changed": "2025-06-06T08:34:57.410733+00:00",
    "last_reported": "2025-06-06T08:34:57.410733+00:00",
    "last_updated": "2025-06-06T08:34:57.410733+00:00",
    "context": {
      "id": "01JX261ZYP4ZJ173V36B5YK1N9",
      "parent_id": null,
      "user_id": "7b79ba782c64477daa2b1c3e61586337"
    }
  }
]

📨 已发送指令：打开顶灯
✅ 返回内容：
{
  "response": {
    "speech": {
      "plain": {
        "speech": "顶灯已打开",
        "extra_data": null
      }
    },
    "card": {},
    "language": "zh",
    "response_type": "action_done",
    "data": {
      "targets": [],
      "success": [
        {
          "name": "顶灯",
          "type": "entity",
          "id": "light.ding_deng"
        }
      ],
      "failed": []
    }
  },
  "conversation_id": "01JX26208NQZTMTPK9QV31PRFQ",
  "continue_conversation": false
}

📨 已发送指令：关闭顶灯
✅ 返回内容：
{
  "response": {
    "speech": {
      "plain": {
        "speech": "顶灯已关闭",
        "extra_data": null
      }
    },
    "card": {},
    "language": "zh",
    "response_type": "action_done",
    "data": {
      "targets": [],
      "success": [
        {
          "name": "顶灯",
          "type": "entity",
          "id": "light.ding_deng"
        }
      ],
      "failed": []
    }
  },
  "conversation_id": "01JX2622JB6VFM0TQ5GP8KVKXX",
  "continue_conversation": false
}
发现的灯有：
- light.she_deng (状态: on)
- light.ding_deng (状态: on)
- light.bi_deng (状态: off)

✅ 原始 JSON 返回内容（部分）：
[
  {
    "entity_id": "light.she_deng",
    "state": "on",
    "attributes": {
      "supported_color_modes": [
        "onoff"
      ],
      "color_mode": "onoff",
      "sn": "10D07A46C664",
      "panel": "Lamp",
      "room": "客厅",
      "online": "1",
      "attribution": "Data provided by http://jsonplaceholder.typicode.com/",
      "friendly_name": "射灯",
      "supported_features": 0
    },
    "last_changed": "2025-06-06T08:34:57.410733+00:00",
    "last_reported": "2025-06-06T08:34:57.410733+00:00",
    "last_updated": "2025-06-06T08:34:57.410733+00:00",
    "context": {
      "id": "01JX261ZYP4ZJ173V36B5YK1N9",
      "parent_id": null,
      "user_id": "7b79ba782c64477daa2b1c3e61586337"
    }
  },
  {
    "entity_id": "light.ding_deng",
    "state": "on",
    "attributes": {
      "supported_color_modes": [
        "onoff"
      ],
      "color_mode": "onoff",
      "sn": "10D07A46C664",
      "panel": "Lamp",
      "room": "客厅",
      "online": "1",
      "attribution": "Data provided by http://jsonplaceholder.typicode.com/",
      "friendly_name": "顶灯",
      "supported_features": 0
    },
    "last_changed": "2025-06-06T08:34:58.073342+00:00",
    "last_reported": "2025-06-06T08:34:58.073342+00:00",
    "last_updated": "2025-06-06T08:34:58.073342+00:00",
    "context": {
      "id": "01JX26208M8WKJXQGGE9MKP6QY",
      "parent_id": null,
      "user_id": "7b79ba782c64477daa2b1c3e61586337"
    }
  },
  {
    "entity_id": "light.bi_deng",
    "state": "off",
    "attributes": {
      "supported_color_modes": [
        "onoff"
      ],
      "color_mode": null,
      "sn": "10D07A46C664",
      "panel": "Lamp",
      "room": "客厅",
      "online": "1",
      "attribution": "Data provided by http://jsonplaceholder.typicode.com/",
      "friendly_name": "壁灯",
      "supported_features": 0
    },
    "last_changed": "2025-06-06T08:06:12.386649+00:00",
    "last_reported": "2025-06-06T08:34:49.636039+00:00",
    "last_updated": "2025-06-06T08:06:12.386649+00:00",
    "context": {
      "id": "01JX24DBBH4K5MN01JCVKC1WXR",
      "parent_id": null,
      "user_id": "7b79ba782c64477daa2b1c3e61586337"
    }
  }
]
(ha-env) ➜  test git:(dev) 
```

