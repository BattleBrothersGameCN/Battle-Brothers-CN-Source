# Mod Source Configuration

本仓库用 `mods/<mod-id>/` 管理 Mod 文本提取输入。优先使用 Git submodule 固定到上游源码 tag 或 commit；仓库内不保留本地下载或解包副本。

## 目录规范

- `data/`: 原版游戏源码输入。
- `mods/<mod-id>/`: 可复现的 Mod 源码输入，推荐为 submodule。

## manifest.json 字段

- `id`: 组件 ID，使用稳定英文短名，例如 `reforged`。
- `type`: 原版使用 `base`，Mod 使用 `mod`。
- `input_path`: 文本提取输入目录，相对仓库根目录。
- `output_path`: 输出到 Battle-Brothers-CN 项目的 JSON 目录。
- `name`: 展示名称。
- `description`: 来源或补充说明。
- `version`: 当前接入的 Mod 版本。
- `project_id`: ParaTranz 项目 ID；未建项目时填 `0` 会在同步工具中跳过。
- `package_name`: 生成汉化包文件名。
- `detect`: 安装检测用 glob，按 Battle Brothers `data` 目录下的 zip 文件名填写。
- `required`: 是否为必选组件；原版为 `true`，Mod 通常为 `false`。

## Reforged

当前接入：

- 名称: Battle Brothers - Reforged
- Nexus: https://www.nexusmods.com/battlebrothers/mods/765
- GitHub: https://github.com/Battle-Modders/mod-reforged
- 版本: `0.9.2`
- submodule 路径: `mods/reforged`
- 固定 commit: `7b8ca29e4d171e027064cdea9d391c976f9d0124`
- ParaTranz project_id: `19677`

更新 Reforged 版本时：

```bash
git -C mods/reforged fetch --tags
git -C mods/reforged checkout <version>
```

然后同步修改 `manifest.json` 中 `version`，执行一次文本提取，确认输出目录没有异常后再提交。

本地只提取某一个 job 时传入 `--job`：

```bash
python tools/extract_text.py /path/to/Battle-Brothers-CN --job reforged
```

GitHub Actions 手动触发时可填写 `job_id`。默认值 `all` 会提取全部 jobs；填写 `base` 或 `reforged` 会只提取对应 job。

Mod 翻译流程使用已支持 Mods 的 bb-translator 版本，例如 `v2.0.0` 或更新版本：

https://github.com/shabbywu/bb-translator/releases/tag/v2.0.0
