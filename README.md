# 活动答疑 Agent

面向线上活动、线下活动和混合活动的咨询回复助手。同一个问答内核读取不同活动包，回答报名、入口、地点、日程等已确认信息；个人状态、作业代答、安全和投诉默认转人工。

开源英才夏令营是内置参考活动包，不是唯一使用场景。它同时包含线上课程答疑和线下入营信息，并带有 MXMACA 算子优化社区的公开资料。

## 活动包

| 活动包 | 形式 | 内容 |
| --- | --- | --- |
| `summer-camp` | 线上、线下 | 开源英才夏令营参考包 |
| `online-workshop` | 线上 | 只有直播入口，没有线下会场 |
| `offline-meetup` | 线下 | 只有地点和签到，没有直播 |
| `hybrid-summit` | 线上、线下 | 两种参加方式都可以 |

新增一场活动时，复制 `activities/offline-meetup/`，修改 `activity.json` 和 `faq.json`。`formats` 只能写 `online`、`offline`，或两者都写。知识库字段沿用 `data/faq.json` 的结构。

## 本地运行

需要 Python 3.10 或更高版本，不需要安装第三方包。

```powershell
python -m summer_camp_agent.cli activities
python -m summer_camp_agent.cli demo
python -m summer_camp_agent.cli ask "直播链接在哪里？" --activity online-workshop
python -m summer_camp_agent.cli ask "活动地点在哪里？" --activity offline-meetup
python -m summer_camp_agent.cli ask "可以只参加线上吗？" --activity hybrid-summit
python -m summer_camp_agent.cli validate
python -m unittest discover -s tests -p "test_*.py"
```

`demo` 不访问网络。夏令营样例固定在 2026-07-10 回放，避免活动结束后有效期过期导致演示失真。真实消息按消息日期判断资料是否仍有效。

模型生成是可选能力。设置 `OPENAI_API_KEY` 后，可以把 `OPENAI_BASE_URL` 指到任何 OpenAI 兼容接口，包括部署在 MXMACA 或其他环境上的本地推理服务。没有密钥时，FAQ 和活动包演示仍然可以运行。

## 回复边界

- 只回复活动包里写明、且未过期的内容。
- 录取、报名状态、名额查询转给活动里的主办方或组委会。
- 作业答案、代写和调试请求转给活动配置的对接人。
- 医疗、安全、突发和投诉立即转人工。
- 示例活动包中的 `example.com` 只用于演示，不是真实报名或直播地址。

## 许可证

Apache License 2.0。详见 `LICENSE`。
