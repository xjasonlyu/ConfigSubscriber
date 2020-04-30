# Subscribe Config Convert Framework

`subscriber`是一个用`Flask`写的负责将机场订阅配置文件转换成自己需要的格式的（**玩具**）框架🤪

## Why

目前很多机场都支持节点订阅，但是配置或多或少都有些死板，不易变通，而且作为一个强迫症怎么能忍受参差不齐的节点命名🌚

虽然已经有一些在线的订阅转换网站，但是缺点也很明显：不够灵活，自定义空间小，而且也可能存在安全风险

如果手改的话，节点多了基本会累死，而且不能及时更新订阅信息

所以，此玩具项目应运而生🙈

`subscriber`目前支持以clash的配置文件作为输入，使用jinja2作为配置模版引擎，支持二次转换成

- Clash 配置文件
- Surge 配置文件
- 其他（用jinja2写模版就行）

## Usage

使用非常简单，跑`Docker`里，需要`HTTPS`的话，用nginx或者caddy反代即可

```sh
docker pull xjasonlyu/subscriber
```

docker-compose示例

```yaml
version: '3'
services:
  subscriber:
    image: xjasonlyu/subscriber:latest
    volumes:
      - /etc/subscriber:/config:ro
    restart: always
    network_mode: host
    container_name: subscriber
```

客户端添加订阅URL示例

- Clash: `http://yourserver/subscribe/clash?auth=your_auth_code`
- Surge: `http://yourserver/subscribe/surge?auth=your_auth_code`

## Configuration

`subscriber`支持高度的自定义，通过配置模版几乎可以匹配任何的客户端

### Subscriber Config

`subscriber`参考配置文件如下：

```json
{
    "settings": {
        "cache": {
            "cache_type": "simple",
            "cache_ignore_errors": false,
            "cache_default_timeout": 300
        }
    },
    "subscriptions": {
        "_auth_01_": {
            "link": "https://example.com/config_01.yml",
            "parser": "N3RO",
            "template": "modules/n3ro.j2",
            "sort": "node.net,node.flag,id",
            "filter": "node.flag and type=='ss'",
            "interval": 86400,
            "extras": {}
        },
        "_auth_02_": {
            "link": "https://example.com/config_02.yml",
            "parser": "rixCloud",
            "template": "modules/rixcloud.j2",
            "sort": "node.attr,node.flag,id",
            "filter": "node.flag and type=='ss'",
            "interval": 259200,
            "extras": {}
        }
    },
    "ruleset": {
        "remotes": [
            "https://raw.githubusercontent.com/ConnersHua/Profiles/master/Surge/Ruleset",
            "https://raw.githubusercontent.com/rixCloud-Inc/rixCloud-Surge3_Rules/master"
        ]
    }
}
```

`settings`字段目前仅支持`cache`一项，配置与[Flask-Caching](https://flask-caching.readthedocs.io/en/latest/#configuring-flask-caching)相同，无视大小写

`subscriptions`字段里是每一个订阅的映射，key是`your_auth_code`，value具体配置如下：

- `link`: 原机场订阅的clash格式链接（支持`http|https|file`协议）
- `parser`: 指定的订阅转换器，参考`subscribe/parser`目录，自定义
- `template`: jinja2模版，参考`config/templates`目录，自定义
- `sort`: 节点排序规则，字段参考`subscribe.filter::Proxy`类的实现
- `filter`: 节点过滤器，只有满足条件才会进一步转换，字段参考`subscribe.filter::Proxy`类的实现
- `interval`: 配置更新间隔，仅Surge支持，可以忽略
- `extras`: 额外的变量，方便jinja2模版的引用

`ruleset`字段目前只有`remotes`一个子字段，作为上游规则集URL

- 示例URL: `http://yourserver/ruleset/Apple.list`

### Templates

这玩意儿用jinja2写模版，所以能随便折腾，所以前提是要会jinja2的语法，然后就随意配置了

具体参考`config/templates`目录下的demo

## End

之所以说玩具，除了代码不到1000行以外，就是配置一点都不人性化了2333，不过一次配置完以后就舒服了Orz
