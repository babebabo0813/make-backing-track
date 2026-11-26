# Audacity 脚本工作流

Audacity 3.x 的 `mod-script-pipe` 支持本地命令接口。Audacity 4 的接口与菜单不同，不假定 3.x 管道仍可用。优先检查当前版本与可用接口；必要时用官方 3.x 便携包在项目目录建立独立环境，而非替换用户安装的软件。

便携版在 Audacity.exe 旁建立 `Portable Settings`。设置文件为 `audacity.cfg`。使用独立可写 `TempDir`，避免与其他版本共用临时目录引发启动对话框。

在便携设置中启用本任务需要的 `[Module] mod-script-pipe=1`；`[ModuleDateTime]` 中的模块时间须与 DLL 的本地修改时间一致，格式 `yyyy-MM-ddTHH:mm:ss`，否则可能重新变成 New。不要更改用户现有安装的全局配置。处理完成后退出专用实例，避免让脚本管道长期暴露。

首次使用时定位本机安装的 UVR、FFmpeg、Python 与 Audacity，确认版本和可执行文件路径。优先使用用户提供的路径，其次检查 PATH；不要假定软件装在某个磁盘或用户名目录。

本文的 `D:/project/` 是通用示例目录，必须替换为实际工作目录。脚本的 `--ffmpeg` 参数显式传入本机 FFmpeg 路径。较旧 FFmpeg 的 amix 未必支持 `normalize=0`；需要外部参考混音时先查询本机滤镜选项。

## 客户端

Windows 管道为 `\\.\pipe\ToSrvPipe`、`\\.\pipe\FromSrvPipe`。Python 对管道 `os.path.exists()` 的结果未必可靠，直接连接并捕获失败。每条命令以 CRLF 加 NUL 结束，读到结果后的空行。客户端检查 `BatchCommand finished: OK`，超时即停止，保留日志供判断是否部分执行。

```text
python scripts/audacity_pipe.py --commands commands.json --log commands.jsonl --timeout 45
```

连接后先查 `GetInfo: Type=Tracks` 和 `Help: Command=SetTrackAudio`，避免修改非本任务工程。空工程的典型命令序列如下，替换所有示例路径和音量：

```text
SetProject: Name="Song - backing track" Rate=48000
Import2: Filename="D:/project/instrumental.flac"
SelectTracks: Track=0 TrackCount=1 Mode=Set
SetTrackStatus: Name="Instrumental"
SetTrackAudio: Volume=-4.8 Pan=0 Mute=0 Solo=0
Import2: Filename="D:/project/work/backing_aligned.wav"
SelectTracks: Track=1 TrackCount=1 Mode=Set
SetTrackStatus: Name="Aligned backing vocals"
SetTrackAudio: Volume=-7.8 Pan=0 Mute=0 Solo=0
SelectAll:
SetPreference: Name="/FileFormats/ExportFormat_SF1_Type/WAV_10000" Value=3
SaveProject2: Filename="D:/project/outputs/mix.aup3"
Export2: Filename="D:/project/outputs/mix.wav" NumChannels=2
```

3.7.9 实际参数为 **Volume（dB）**，不是某些旧手册写的 Gain。用 GetInfo 确认 volume 返回的是预期的线性比例。示例音量不是通用预设。

保存后 `Close:` 可让 SQLite 工程完成写入并关闭 WAL，随后再复制工程。不要在未保存或不明用户工程上发送 Close/Exit。若导出后再次调音，重新 Save、导出新的文件名，避免弹出覆盖确认阻塞命令队列。

官方资料：
- https://manual.audacityteam.org/man/scripting.html
- https://manual.audacityteam.org/man/portable_audacity.html
- https://manual.audacityteam.org/man/scripting_reference.html
- https://github.com/audacity/audacity/releases
