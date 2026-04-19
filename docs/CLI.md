# feishu-easy CLI 使用手册

本文档覆盖 `feishu-easy` 当前暴露的全部命令行接口，面向日常使用与排障。

## 1. 快速开始

### 1.1 环境要求

- Python: `>=3.13`
- 推荐运行器: `uv`
- CLI 入口: `feishu-easy`

示例（仓库内直接运行）：

```bash
uv run feishu-easy --help
```

### 1.2 认证模式

`feishu-easy` 支持两种认证模式：

1) 默认应用身份认证（推荐批处理/服务脚本）

- 依赖环境变量：
  - `FEISHU_APP_ID`
  - `FEISHU_APP_SECRET`
- 可将变量放在 `.env` 中，CLI 启动时会自动加载。

2) 用户身份认证（`--run-as-user`）

- 启动 OAuth 授权流程（会打开浏览器）。
- 当前会请求以下 scope：
  - `docx:document.block:convert`
  - `board:whiteboard:node:read`
  - `board:whiteboard:node:create`

### 1.3 全局选项

所有命令都支持以下全局参数（放在子命令前）：

- `--run-as-user`：切换到用户身份认证
- `--log-level TEXT`：日志级别，支持 `DEBUG/INFO/WARNING/ERROR/CRITICAL`，默认 `INFO`

示例：

```bash
uv run feishu-easy --log-level DEBUG get-tenant-access-token
uv run feishu-easy --run-as-user board list-whiteboard-node wbcnxxxx
```

---

## 2. 命令总览

顶层命令：

- `get-tenant-access-token`
- `wiki ...`
- `board ...`
- `bitable ...`
- `drive ...`
- `doc ...`
- `docx ...`
- `flow ...`
- `sheets ...`

提示：命令名中统一使用中划线（例如 `get-space-node`）。

---

## 3. 顶层命令

### 3.1 `get-tenant-access-token`

用途：获取 tenant access token 信息（JSON 输出）。

示例：

```bash
uv run feishu-easy get-tenant-access-token
```

---

## 4. `wiki` 命令组

### 4.1 `wiki get-space-node`

用途：查询知识库节点详情。

参数：

- `node_token`（必填，参数）: Wiki 节点 token

示例：

```bash
uv run feishu-easy wiki get-space-node wikinodexxxx
```

### 4.2 `wiki get-space`

用途：查询知识库空间信息。

参数：

- `space_id`（必填，参数）: 空间 ID（整数）
- `--lang TEXT`（可选）: 语言，默认 `zh`

示例：

```bash
uv run feishu-easy wiki get-space 123456 --lang en
```

### 4.3 `wiki update-node-title`

用途：更新节点标题。

参数：

- `node_token`（必填，参数）
- `title`（必填，参数）

示例：

```bash
uv run feishu-easy wiki update-node-title wikinodexxxx "新的标题"
```

### 4.4 `wiki move-space-node`

用途：移动节点到指定父节点（可跨空间）。

参数：

- `node_token`（必填，参数）: 待移动节点
- `space_id`（必填，参数）: 当前空间 ID
- `--target-parent-token TEXT`（必填）: 目标父节点 token
- `--target-space-id INTEGER`（可选）: 目标空间 ID

示例：

```bash
uv run feishu-easy wiki move-space-node wikinodexxxx 123456 --target-parent-token wikiparentxxxx
```

### 4.5 `wiki create-space-node-origin`

用途：创建原生节点（origin）。

参数：

- `space_id`（必填，参数）
- `--obj-type [file|docx|bitable|doc|sheet|mindnote|shortcut|slides]`（必填）
- `--parent-node-token TEXT`（必填）
- `--title TEXT`（必填）

示例：

```bash
uv run feishu-easy wiki create-space-node-origin 123456 --obj-type docx --parent-node-token wikiparentxxxx --title "周报"
```

### 4.6 `wiki create-space-node-shortcut`

用途：创建快捷方式节点（shortcut）。

参数：

- `space_id`（必填，参数）
- `--obj-type [file|docx|bitable|doc|sheet|mindnote|shortcut|slides]`（必填）
- `--parent-node-token TEXT`（必填）
- `--title TEXT`（必填）
- `--origin-node-token TEXT`（必填）: 被引用原节点 token

示例：

```bash
uv run feishu-easy wiki create-space-node-shortcut 123456 --obj-type docx --parent-node-token wikiparentxxxx --title "文档快捷方式" --origin-node-token wikioriginxxxx
```

### 4.7 `wiki list-space`

用途：列出当前可见知识库空间。

示例：

```bash
uv run feishu-easy wiki list-space
```

### 4.8 `wiki list-space-member`

用途：列出空间成员。

参数：

- `space_id`（必填，参数）

示例：

```bash
uv run feishu-easy wiki list-space-member 123456
```

### 4.9 `wiki list-space-node`

用途：列出空间节点（可按父节点过滤）。

参数：

- `space_id`（必填，参数）
- `--parent-node-token TEXT`（可选）

示例：

```bash
uv run feishu-easy wiki list-space-node 123456 --parent-node-token wikiparentxxxx
```

---

## 5. `board` 命令组

### 5.1 `board create-plantuml-node`

用途：向白板插入 PlantUML/Mermaid 图节点。

参数：

- `whiteboard_id`（必填，参数）
- `--code TEXT` / `--plant-uml-code TEXT`（二选一）: 图源码字符串
- `--file PATH` / `--plant-uml-file PATH`（二选一）: 图源码文件
- `--syntax [plantuml|mermaid]`（可选，默认 `plantuml`）
- `--style [board|classic]`（可选，默认 `board`）
- `--style-type INTEGER`（可选）: 直接覆盖 style_type（1/2）
- `--syntax-type INTEGER`（可选）: 直接覆盖 syntax_type（1/2）
- `--diagram-type INTEGER`（可选）: PlantUML 图类型
- `--overwrite BOOL`（可选）
- `--parse-mode INTEGER`（可选）

约束：

- `--code` 与 `--file` 必须且只能传一个。
- Mermaid 不支持 classic 样式（`--syntax mermaid` 时不可 `--style classic`）。
- 文件模式会读取 UTF-8 文本。

示例：

```bash
uv run feishu-easy board create-plantuml-node wbcnxxxx --code "@startuml\nAlice -> Bob: hello\n@enduml"
uv run feishu-easy board create-plantuml-node wbcnxxxx --file ./diagram.mmd --syntax mermaid --style board
```

### 5.2 `board list-whiteboard-node`

用途：列出白板节点。

参数：

- `whiteboard_id`（必填，参数）
- `--user-id-type TEXT`（可选，默认 `open_id`）

示例：

```bash
uv run feishu-easy board list-whiteboard-node wbcnxxxx
```

### 5.3 `board download-as-image`

用途：将白板下载为图片。

参数：

- `whiteboard_id`（必填，参数）
- `--output-dir PATH`（可选，默认当前目录）
- `--file-name TEXT`（可选）

示例：

```bash
uv run feishu-easy board download-as-image wbcnxxxx --output-dir ./output --file-name board.png
```

---

## 6. `bitable` 命令组

### 6.1 `bitable get-app`

用途：查询多维表格应用信息。

参数：

- `app_token`（必填，参数）
- `--user-id-type TEXT`（可选）

### 6.2 `bitable list-app-table`

用途：列出应用下的数据表。

参数：

- `app_token`（必填，参数）

### 6.3 `bitable list-app-table-field`

用途：列出数据表字段。

参数：

- `app_token`（必填，参数）
- `table_id`（必填，参数）
- `--view-id TEXT`（可选）
- `--text-field-as-array / --no-text-field-as-array`（可选）
- `--user-id-type TEXT`（可选）

### 6.4 `bitable list-app-table-view`

用途：列出数据表视图。

参数：

- `app_token`（必填，参数）
- `table_id`（必填，参数）
- `--user-id-type TEXT`（可选）

### 6.5 `bitable get-app-table-view`

用途：查询指定视图详情。

参数：

- `app_token`（必填，参数）
- `table_id`（必填，参数）
- `view_id`（必填，参数）
- `--user-id-type TEXT`（可选）

### 6.6 `bitable search-app-table-record`

用途：查询记录（默认行为由服务层定义）。

参数：

- `app_token`（必填，参数）
- `table_id`（必填，参数）
- `--user-id-type TEXT`（可选）

通用示例：

```bash
uv run feishu-easy bitable get-app appcnxxxx
uv run feishu-easy bitable list-app-table appcnxxxx
uv run feishu-easy bitable list-app-table-field appcnxxxx tblxxxx --view-id vewxxxx --text-field-as-array
uv run feishu-easy bitable list-app-table-view appcnxxxx tblxxxx
uv run feishu-easy bitable get-app-table-view appcnxxxx tblxxxx vewxxxx
uv run feishu-easy bitable search-app-table-record appcnxxxx tblxxxx
```

---

## 7. `drive` 命令组

支持的 `file_type` / `doc_type` 枚举：

- `file`
- `docx`
- `bitable`
- `folder`
- `doc`
- `sheet`
- `mindnote`
- `shortcut`
- `slides`

### 7.1 `drive delete-file`

用途：删除云文档文件。

参数：

- `file_token`（必填，参数）
- `--type <file_type>`（必填）

### 7.2 `drive list-file`

用途：列举文件。

参数：

- `--folder-token TEXT`（可选）
- `--order-by TEXT`（可选）
- `--direction TEXT`（可选，常见 `ASC`/`DESC`）
- `--user-id-type TEXT`（可选）

### 7.3 `drive batch-query-meta`

用途：批量查询多个文档元信息。

参数：

- `--doc <doc_type:doc_token>`（必填，可重复）
- `--with-url / --no-with-url`（可选，默认 `--with-url`）
- `--user-id-type TEXT`（可选）

示例：

```bash
uv run feishu-easy drive batch-query-meta --doc docx:doxcnxxxx --doc sheet:shtcnxxxx
```

### 7.4 `drive get-file-statistics`

用途：查询文件统计信息。

参数：

- `file_token`（必填，参数）
- `--type <file_type>`（必填）

### 7.5 `drive list-file-view-record`

用途：查询查看记录。

参数：

- `file_token`（必填，参数）
- `--type <file_type>`（必填）
- `--viewer-id-type TEXT`（可选，默认 `open_id`）
- `--page-size INTEGER`（可选）

### 7.6 `drive list-file-version`

用途：查询文件历史版本。

参数：

- `file_token`（必填，参数）
- `--type <file_type>`（必填）
- `--user-id-type TEXT`（可选）

### 7.7 `drive copy-file`

用途：复制文件。

参数：

- `file_token`（必填，参数）
- `--type <file_type>`（必填）
- `--folder-token TEXT`（必填）: 目标目录
- `--name TEXT`（必填）: 新文件名
- `--user-id-type TEXT`（可选）
- `--extra JSON`（可选）: 必须是 JSON 对象字符串

示例：

```bash
uv run feishu-easy drive copy-file filecnxxxx --type docx --folder-token fldcnxxxx --name "副本-周报"
uv run feishu-easy drive copy-file filecnxxxx --type docx --folder-token fldcnxxxx --name "副本-周报" --extra '{"mount_type":1}'
```

### 7.8 `drive move-file`

用途：移动文件。

参数：

- `file_token`（必填，参数）
- `--type <file_type>`（必填）
- `--folder-token TEXT`（必填）

### 7.9 `drive upload-file`

用途：上传本地文件。

参数：

- `local_file`（必填，参数）: 本地路径
- `--folder-token TEXT`（必填）
- `--file-name TEXT`（可选）: 目标文件名，默认使用本地文件名

### 7.10 `drive download-file`

用途：下载云文档文件。

参数：

- `file_token`（必填，参数）
- `--output-dir PATH`（可选，默认当前目录）
- `--file-name TEXT`（可选）

### 7.11 `drive download-media`

用途：下载媒体文件。

参数：

- `file_token`（必填，参数）
- `--output-dir PATH`（可选，默认当前目录）
- `--file-name TEXT`（可选）

### 7.12 `drive subscribe-file`

用途：订阅文件事件。

参数：

- `file_token`（必填，参数）
- `--type <file_type>`（必填）
- `--event-type TEXT`（必填）

### 7.13 `drive delete-subscribe-file`

用途：取消文件事件订阅。

参数：

- `file_token`（必填，参数）
- `--type <file_type>`（必填）
- `--event-type TEXT`（必填）

### 7.14 `drive get-subscribe-file`

用途：查询订阅状态。

参数：

- `file_token`（必填，参数）
- `--type <file_type>`（必填）
- `--event-type TEXT`（必填）

通用示例：

```bash
uv run feishu-easy drive list-file --folder-token fldcnxxxx --order-by EditedTime --direction DESC
uv run feishu-easy drive upload-file ./demo.pdf --folder-token fldcnxxxx
uv run feishu-easy drive download-file filecnxxxx --output-dir ./downloads
uv run feishu-easy drive move-file filecnxxxx --type docx --folder-token fldcnxxxx
uv run feishu-easy drive subscribe-file filecnxxxx --type docx --event-type file.created_in_folder_v1
```

---

## 8. `doc` 命令组

### 8.1 `doc get-content`

用途：获取旧版 doc 文档内容。

参数：

- `obj_token`（必填，参数）: doc 对象 token

示例：

```bash
uv run feishu-easy doc get-content doccnxxxx
```

---

## 9. `docx` 命令组

### 9.1 `docx get-document`

用途：查询文档信息。

参数：

- `document_id`（必填，参数）

### 9.2 `docx raw-content`

用途：获取文档原始内容。

参数：

- `document_id`（必填，参数）
- `--lang INTEGER`（可选，默认 `0`）

### 9.3 `docx create-document`

用途：在指定目录创建文档。

参数：

- `title`（必填，参数）
- `--folder-token TEXT`（必填）

### 9.4 `docx list-document-block`

用途：列出文档 block。

参数：

- `document_id`（必填，参数）
- `--document-revision-id INTEGER`（可选，默认 `-1`，表示最新）

### 9.5 `docx get-document-block`

用途：查询指定 block 详情。

参数：

- `document_id`（必填，参数）
- `block_id`（必填，参数）
- `--document-revision-id INTEGER`（可选，默认 `-1`）

### 9.6 `docx get-document-block-children`

用途：获取 block 子节点列表。

参数：

- `document_id`（必填，参数）
- `block_id`（必填，参数）

### 9.7 `docx batch-delete-document-block-children`

用途：按区间批量删除 block 子节点。

参数：

- `document_id`（必填，参数）
- `block_id`（必填，参数）
- `start_index`（必填，参数，闭区间起点）
- `end_index`（必填，参数，开区间终点）

通用示例：

```bash
uv run feishu-easy docx get-document doxcnxxxx
uv run feishu-easy docx create-document "会议纪要" --folder-token fldcnxxxx
uv run feishu-easy docx list-document-block doxcnxxxx --document-revision-id -1
uv run feishu-easy docx get-document-block doxcnxxxx blkcnxxxx
```

---

## 10. `flow` 命令组

### 10.1 `flow upload-markdown`

用途：将本地 Markdown 上传到指定知识库节点并转为文档。

参数：

- `markdown_file`（必填，参数）
- `node_token`（必填，参数）
- `--skip-failed-images / --no-skip-failed-images`（可选，默认 `--no-skip-failed-images`）

说明：成功后会在标准错误输出一条结果提示，包含文档 ID 与批次数。

### 10.2 `flow get-markdown`

用途：从知识库节点导出 Markdown 文本。

参数：

- `node_token`（必填，参数）
- `--expand-board / --no-expand-board`（可选）
- `--expand-sheets / --no-expand-sheets`（可选）
- `--expand-bitable / --no-expand-bitable`（可选）

### 10.3 `flow get-unified`

用途：从知识库节点导出统一文档 JSON（`unified_doc`）。

参数：

- `node_token`（必填，参数）
- `--expand-board / --no-expand-board`（可选）
- `--expand-sheets / --no-expand-sheets`（可选）
- `--expand-bitable / --no-expand-bitable`（可选）

示例：

```bash
uv run feishu-easy flow upload-markdown ./README.md wikinodexxxx --skip-failed-images
uv run feishu-easy flow get-markdown wikinodexxxx --expand-sheets --expand-bitable
uv run feishu-easy flow get-unified wikinodexxxx --expand-board
```

---

## 11. `sheets` 命令组

### 11.1 `sheets get-spreadsheet-sheet`

用途：获取单个工作表信息。

参数：

- `spreadsheet_token`（必填，参数）
- `sheet_id`（必填，参数）

### 11.2 `sheets query-spreadsheet-sheet`

用途：查询电子表格下的工作表列表。

参数：

- `spreadsheet_token`（必填，参数）

### 11.3 `sheets get-spreadsheet`

用途：查询电子表格信息。

参数：

- `spreadsheet_token`（必填，参数）
- `--user-id-type TEXT`（可选）

### 11.4 `sheets get-spreadsheet-metainfo`

用途：查询电子表格元信息。

参数：

- `spreadsheet_token`（必填，参数）
- `--ext-fields TEXT`（可选，例如 `protectedRange`）
- `--user-id-type TEXT`（可选）

### 11.5 `sheets create-spreadsheet`

用途：创建电子表格。

参数：

- `title`（必填，参数）
- `--folder-token TEXT`（可选）

### 11.6 `sheets get-sheet-values`

用途：读取单元格值。

参数：

- `spreadsheet_token`（必填，参数）
- `value_range`（必填，参数，例如 `Sheet1!A1:B2`）
- `--value-render-option TEXT`（可选）
- `--date-time-render-option TEXT`（可选）

### 11.7 `sheets get-sheet-content`

用途：读取工作表内容。

参数：

- `spreadsheet_token`（必填，参数）
- `sheet_id`（必填，参数）

通用示例：

```bash
uv run feishu-easy sheets get-spreadsheet shtcnxxxx
uv run feishu-easy sheets create-spreadsheet "销售台账" --folder-token fldcnxxxx
uv run feishu-easy sheets get-sheet-values shtcnxxxx "Sheet1!A1:C20"
uv run feishu-easy sheets get-sheet-content shtcnxxxx f5f9e9
```

---

## 12. 输出、错误与排障

### 12.1 输出约定

- 大多数命令输出 JSON（`ensure_ascii=False`，中文可直接显示）。
- 少数命令返回纯文本（如 `doc get-content`、`flow get-markdown`）。
- `flow upload-markdown` 成功提示写到标准错误（stderr）。

### 12.2 常见错误

- 缺少环境变量：`FEISHU_APP_ID is required` / `FEISHU_APP_SECRET is required`
- 日志级别非法：`Invalid log level`
- 参数校验失败：例如 `--doc` 格式错误、`--extra` 非 JSON 对象
- 文件不存在：例如 `board create-plantuml-node --file` 指向不存在文件

### 12.3 调试建议

```bash
uv run feishu-easy --log-level DEBUG <你的命令>
```

若需要核对参数签名，以 `--help` 为准：

```bash
uv run feishu-easy --help
uv run feishu-easy drive --help
uv run feishu-easy drive copy-file --help
```
