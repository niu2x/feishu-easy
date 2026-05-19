# AGENTS.md

本文件面向本仓库的开发者与自动化 Agent，只记录“容易做错/猜错”的约束。

## 1) 先看哪里（高优先级）

- 先读 `pyproject.toml`（入口、依赖、Python 版本）和 `README.md`（对外约定）。
- 本仓库目前无 CI、无测试目录、无 pre-commit 配置；不要假设存在标准流水线。

## 2) 运行与验证（已验证可用）

- 使用 `uv` 执行命令，Python 要求 `>=3.13`（见 `pyproject.toml`）。
- CLI 入口脚本是 `feishu-easy = "feishu_easy:app"`。
- 改动后最小可用验证：

```bash
uv run python - <<'PY'
import importlib
import pkgutil

import feishu_easy

errs = []
mods = [m.name for m in pkgutil.walk_packages(feishu_easy.__path__, feishu_easy.__name__ + ".")]
for name in mods:
    try:
        importlib.import_module(name)
    except Exception as exc:
        errs.append((name, type(exc).__name__, str(exc)))

print(f"TOTAL_ERRORS={len(errs)}")
PY
```

期望结果是 `TOTAL_ERRORS=0`。

## 3) 代码结构（按职责改）

- `src/feishu_easy/cli/`: Typer CLI 装配与启动前处理（认证、日志）。
- `src/feishu_easy/services/`: 用例编排层（调用 API 客户端 + 转换逻辑）。
- `src/feishu_easy/clients/feishu/`: 飞书 API 客户端实现层（替代旧 `feishu_api_parts`）。
- `src/feishu_easy/convert/from_feishu/`: 各资源到 `unified_doc` 的转换。
- `src/feishu_easy/unified_doc/`: 统一文档模型与 Markdown 渲染。

注意：`src/feishu_easy/feishu_api_parts/` 仅剩缓存目录，不应再新增或引用该层。

## 4) 认证与参数陷阱

- 默认模式依赖环境变量 `FEISHU_APP_ID`、`FEISHU_APP_SECRET`（`cli/bootstrap.py`）。
- 日志级别通过 CLI 参数 `--log-level`。
- `--run-as-user` 分支调用 `acquire_user_access_token()`（`services/auth_service.py`），当前为 stub（`raise NotImplementedError`），实现时需确认用户授权流程与依赖。
- `convert` CLI 目前只暴露 `--from doc|docx|sheet`，即使 service 层支持 `bitable`，CLI 侧并未开放。

## 5) 提交日志强制规则（全仓库生效）

- 所有 commit message 必须使用中文。
- 开头必须是两句七言诗（每句 7 个汉字），两句之间保留一个空格并写在同一行总结改动。
- 七言诗后补充中文正文，说明动机、关键改动、影响范围。

格式：

```text
<七言诗第一句> <七言诗第二句>

<中文正文>
```

若发现最近提交不合规，且提交尚未推送，优先修正为合规格式。

## 6) Python 3.13 代码约定（实用）

- 新文件默认使用 `from __future__ import annotations`，降低前向引用与循环依赖场景的类型负担。
- 统一使用现代类型语法：`list[str]`、`dict[str, Any]`、`X | None`。
- 需要在运行时解析注解时，使用 `typing.get_type_hints()`，不要直接依赖 `__annotations__` 的字面值。
- 保持 Pydantic v2 风格：`model_validate` / `model_dump`，不要混用 v1 API。
- 命令行参数尽早校验（CLI 层），避免把非法输入下沉到 `services`。
