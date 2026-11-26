# make-backing-track · 制作带垫音伴奏

基于 UVR 和 Audacity 的 Agent Skill：从原曲提取和声、叠唱或尾字垫音，与官方伴奏或分离伴奏对齐混合，制作适合自己演唱的伴奏。

音频处理在本地完成，无需音乐平台 API Key。运行 skill 的 AI 助手仍使用其自身账号或套餐。

## 能做什么

- 有原曲和官方伴奏：提取背景人声，校准时间并混回官方伴奏。
- 只有原曲：先分出伴奏与人声，再尝试分出背景人声。
- 已有分离音轨：直接检查对齐、混音和导出。
- 在 Audacity 中保存可编辑工程，导出 WAV，可另导出 MP3。

这是调用已有工具的工作流，不是新的人声分离模型，也不是一键独立应用。当前主要面向 Windows；`audacity_pipe.py` 仅支持 Windows 命名管道。UVR 的分离操作需要可用的界面控制能力或用户手动完成。

## 依赖

| 依赖 | 用途 | 获取方式 |
| --- | --- | --- |
| [Ultimate Vocal Remover GUI](https://github.com/Anjok07/ultimatevocalremovergui) | 分离伴奏、主唱与背景人声 | 使用官方仓库和发布页 |
| Kim Vocal 2、5_HP-Karaoke-UVR 模型 | 本 skill 的默认两阶段分离流程 | 优先通过 UVR 内置下载管理器获取；以实际可用模型和标注为准 |
| Python 3、NumPy | 对齐与电平估计 | `python -m pip install -r requirements.txt` |
| [FFmpeg](https://ffmpeg.org/download.html) | 音频解码、重采样、验证 | 自行安装，向脚本传入可执行文件路径 |
| [Audacity](https://www.audacityteam.org/) | 混音、保存工程和导出 | 管道脚本面向启用 mod-script-pipe 的 3.x；其他版本先确认接口 |

第三方程序、模型和音色不随本仓库分发，各自遵循其许可。软件路径均由使用者提供或在本机发现。

## 安装 skill

把整个 `make-backing-track` 文件夹复制到 Codex 的技能目录，通常为 `~/.codex/skills/`；若设置了 CODEX_HOME，则使用其下的 `skills/`。保留 `SKILL.md`、`agents/`、`references/` 和 `scripts/` 的相对结构。其他支持 SKILL.md 的助手按各自的技能安装方式加载。

在本文件夹内安装辅助脚本依赖，建议使用独立虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

不要将模型、歌曲或安装包复制进 skill 文件夹。

## 调用示例

```text
使用 $make-backing-track，处理我提供的原曲和官方伴奏。
保留和声和尾字垫音，尽量减少主唱，在 Audacity 中保存工程并导出 WAV。
```

也可以提供原曲或已经分离好的伴奏、背景人声。工作前明确源文件、成品目录以及要使用的软件。

流程是：确认音轨 → UVR 分离 → 试听辨认背景人声 → 对齐 → 混音 → 工程与成品验证。模型的输出名称不一定对应真实内容，尤其第二遍的 Instrumental 可能是背景人声，必须核对。

## 辅助脚本

以下为 Windows PowerShell 示例，在 skill 文件夹中执行。`D:/project/` 和 `C:/tools/` 都是示例路径；先替换为实际路径，并创建源音频及成品目录。

分离完成后，准备与伴奏对齐的背景人声：

```powershell
python scripts/prepare_audio.py --original "D:/project/original.wav" --instrumental "D:/project/instrumental.wav" --backing "D:/project/backing.wav" --ffmpeg "C:/tools/ffmpeg/bin/ffmpeg.exe" --work-dir "D:/project/work/take-01"
```

若用了上述虚拟环境，将 `python` 换成 `.\.venv\Scripts\python.exe`。

- 输入 backing 必须与 original 共用时间起点；已剪辑的文件需先确认起点。
- 输出 `backing_aligned.wav` 是浮点对齐音轨，`preparation.json` 包含偏移和建议轨道增益；脚本不执行 UVR 分离，也不输出最终混音。
- `--backing-db` 默认 -3，仅为背景人声相对伴奏的起始增益；`--target-sample-peak-db` 默认 -1.5，是采样峰值估计目标，不是真峰值保证。
- 多处对齐不一致时停止并检查版本、剪辑或速度。脚本只处理常数偏移，不自动修复速度漂移；默认搜索范围约为正负一秒。
- 已存在输出时脚本拒绝覆盖，换一个工作目录再运行。

Audacity 管道客户端读取 JSON 字符串数组并保存逐条日志：

```powershell
python scripts/audacity_pipe.py --commands commands.json --log commands.jsonl --timeout 45
```

实际命令、接口启用和导出示例见 [Audacity 工作流](references/audacity.md)。先读当前工程状态，确认是本次任务的工程；超时后停止并检查状态。连接建立不在响应超时计时范围内。日志可能含用户的本机路径，不要提交。

## 限制与素材

背景人声与主唱高度重合时可能无法完整分离，也可能有主唱残留、金属感或尾音损失。结果需要试听，不能保证无损或完全去主唱。成品应检查时长、声道、垫音贡献和真峰值，必要时降低混音电平再导出。

本 skill 的目标是保留背景人声的伴奏；从现场音频中去掉预录垫音并提取现场麦声，需要不同的处理流程。

本仓库不包含歌曲、分离音轨、模型权重或软件安装包。公开演示优先使用自制或已获得发布授权的素材；发布工具不代表获得歌曲或录音的使用授权。

## 许可与来源

仓库内的技能文本和辅助脚本按 [MIT License](LICENSE) 提供。第三方依赖、模型、音乐及录音不适用本仓库的 MIT 许可。实现说明和上游资料见 [来源说明](THIRD_PARTY_NOTICES.md)。
