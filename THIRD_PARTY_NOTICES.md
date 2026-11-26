# 来源与第三方依赖说明

本项目由用户的音轨处理实践与 AI 辅助编写整理而成。它编排已有分离、对齐与混音工具，不宣称发明 UVR、模型架构、互相关算法或 Audacity 脚本接口，也不代表相关上游项目的官方产品。

## 本仓库内容

- `SKILL.md`：带垫音伴奏制作流程。
- `scripts/prepare_audio.py`：使用 NumPy 与 FFmpeg 估计偏移并准备对齐音轨。
- `scripts/audacity_pipe.py`：通过 Audacity Windows 命名管道执行用户明确指定的命令。
- `references/audacity.md`：接口操作记录与通用示例。

此次发布整理沿用现有 skill 中的这些文本与脚本，没有引入下列项目的源码、可执行程序或模型权重。本说明不构成对全部历史代码来源的鉴定；后续引入第三方实现时，应逐文件记录来源、版本、许可证，并保留其要求的声明。

## 上游工具与接口资料

| 上游 | 本项目如何使用 | 分发范围 |
| --- | --- | --- |
| [Ultimate Vocal Remover GUI](https://github.com/Anjok07/ultimatevocalremovergui) / [发布页](https://github.com/Anjok07/ultimatevocalremovergui/releases) | 用户自行运行分离；默认参考 Kim Vocal 2 和 5_HP-Karaoke-UVR | 不包含其代码、程序或权重；模型需单独核对来源和适用条款 |
| [Audacity](https://github.com/audacity/audacity) | 用户自行安装，通过公开脚本接口混音与导出 | 不包含其源码、程序或 DLL |
| [Audacity scripting](https://manual.audacityteam.org/man/scripting.html) / [接口参考](https://manual.audacityteam.org/man/scripting_reference.html) / [便携模式](https://manual.audacityteam.org/man/portable_audacity.html) | 参考接口协议、命令和便携设置说明 | 文档链接；示例需按安装版本核对 |
| [FFmpeg](https://ffmpeg.org/) / [许可说明](https://ffmpeg.org/legal.html) | 从本机调用其可执行文件进行音频处理 | 不捆绑二进制；具体构建及使用方式遵循上游条款 |
| [NumPy](https://numpy.org/) / [许可证](https://github.com/numpy/numpy/blob/main/LICENSE.txt) | 用户独立安装的 Python 运行依赖 | 不捆绑库源码或安装包 |
| [Python](https://www.python.org/) / [许可证](https://docs.python.org/3/license.html) | 运行辅助脚本 | 不捆绑解释器 |

本仓库的 MIT License 仅覆盖维护者有权授权的仓库内容，不改变这些依赖、模型、歌曲或录音的许可。
