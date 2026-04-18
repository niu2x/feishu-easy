# feishu-easy

`feishu-easy` 是一个围绕飞书开放平台封装的 Python 工具库与 CLI，提供文档、表格、云盘等常见能力的统一调用方式。

## 目录与分层约定

- `src/feishu_easy/cli/`：CLI 装配、启动参数和命令入口。
- `src/feishu_easy/services/`：用例编排层，优先接收可注入的 `api` 参数，便于测试与复用连接。
- `src/feishu_easy/clients/feishu/`：飞书 API 客户端层（包含 `gateway.py`、`auth.py`、`retry.py`）。
- `src/feishu_easy/convert/` 与 `src/feishu_easy/unified_doc/`：数据转换与统一文档模型。

## 稳定导出（建议依赖）

- 服务层公共入口：`feishu_easy.services`
- 转换层公共入口：`feishu_easy.convert`
- 网关入口：`feishu_easy.feishu_api.FeishuAPI`

建议优先从上述模块导入，避免跨层直接引用内部实现文件。

## 面向依赖方开发者的提交说明

如果你要向本仓库提交 PR（包括功能、修复、文档变更），请遵循以下提交日志约定：

- 提交信息使用中文。
- 提交标题开头必须是两句七言诗，用于概括本次变更。
- 七言诗后可接正文，简述变更目的与影响范围。

推荐模板：

```text
XXXXXXX
XXXXXXX

这里写 1-2 段中文说明：为什么改、改了什么、影响哪里。
```

示例：

```text
重构分层理脉络
导入归一避旧踪

完成目录分层重构，统一导入路径并修复 CLI 启动流程，降低模块耦合与维护成本。
```
