from __future__ import annotations

import logging
import re
from typing import Any

from ...unified_doc import Block, BlockType, InlineText

logger = logging.getLogger(__name__)

def number(value: Any, default: float = 0.0) -> float:
    if isinstance(value, int | float):
        return float(value)
    return default

def extract_dict(data: Any, path: str) -> Any:
    current: Any = data
    for part in path.split("/"):
        if isinstance(current, dict):
            if part not in current:
                return None
            current = current[part]
            continue

        if isinstance(current, list):
            try:
                index = int(part)
            except ValueError:
                return None
            if index < 0 or index >= len(current):
                return None
            current = current[index]
            continue

        return None

    return current

def convert_whiteboard_to_mermaid_code_block(data: dict[str, Any]) -> Block | None:
    raw_nodes = data.get("nodes", [])
    if not isinstance(raw_nodes, list):
        logger.warning(
            "Board expand skipped: invalid whiteboard payload, `nodes` is not a list"
        )
        return None

    node_types = {
        str(node_type)
        for item in raw_nodes
        if isinstance(item, dict)
        for node_type in [item.get("type")]
        if node_type is not None
    }

    has_flowchart_nodes = bool(
        node_types.intersection(
            {
                "composite_shape",
                "connector",
                "text_shape",
                "table",
                "table_uml",
                "table_er",
                "life_line",
            }
        )
    )
    has_mind_map_nodes = "mind_map" in node_types

    if has_flowchart_nodes:
        return _convert_whiteboard_flowchart(raw_nodes)
    if has_mind_map_nodes:
        return _convert_whiteboard_mindmap(raw_nodes)

    logger.warning(
        "Board expand skipped: no supported nodes, available types: %s",
        ", ".join(sorted(node_types)) if node_types else "(none)",
    )
    return None

def _convert_whiteboard_flowchart(raw_nodes: list[Any]) -> Block | None:
    pie_chart_block = _convert_whiteboard_pie_chart(raw_nodes)
    if pie_chart_block is not None:
        return pie_chart_block

    supported_types = {
        "composite_shape",
        "connector",
        "text_shape",
        "image",
        "table",
        "table_uml",
        "table_er",
        "life_line",
    }
    unsupported_types = {
        str(node_type)
        for item in raw_nodes
        if isinstance(item, dict)
        for node_type in [item.get("type")]
        if node_type is not None and node_type not in supported_types
    }
    if unsupported_types:
        logger.warning(
            "Board flowchart conversion encountered unsupported node types: %s",
            ", ".join(sorted(unsupported_types)),
        )

    id_alias: dict[str, str] = {}
    used_aliases: set[str] = set()

    def alias_of(raw_id: str) -> str:
        alias = id_alias.get(raw_id)
        if alias is not None:
            return alias

        base = re.sub(r"[^a-zA-Z0-9_]", "_", raw_id)
        base = re.sub(r"_+", "_", base).strip("_")
        if not base:
            base = "n"
        if not base[0].isalpha():
            base = f"n_{base}"

        candidate = base
        index = 1
        while candidate in used_aliases:
            index += 1
            candidate = f"{base}_{index}"

        used_aliases.add(candidate)
        id_alias[raw_id] = candidate
        return candidate

    def parse_text(node: dict[str, Any]) -> str:
        text = node.get("text")
        if isinstance(text, dict):
            return str(text.get("text", ""))
        if isinstance(text, str):
            return text
        return ""

    def parse_node_label(node: dict[str, Any]) -> str:
        text = parse_text(node).strip()
        if text:
            return text

        node_type = node.get("type")
        if node_type in {"table", "table_uml", "table_er"}:
            table = node.get("table")
            if isinstance(table, dict):
                title = table.get("title")
                if isinstance(title, str) and title.strip():
                    return title

        if node_type == "life_line":
            lifeline = node.get("lifeline")
            if isinstance(lifeline, dict):
                lifeline_type = lifeline.get("type")
                if isinstance(lifeline_type, str) and lifeline_type.strip():
                    return lifeline_type

        raw_id = node.get("id")
        if isinstance(raw_id, str):
            return raw_id
        return ""

    def esc(text: str) -> str:
        cleaned = text.strip()
        cleaned = re.sub(r"\r\n|\r|\n", "<br/>", cleaned)
        cleaned = cleaned.replace('"', "'")
        return cleaned or "(空)"

    def y_center(node: dict[str, Any]) -> float:
        y = node.get("y")
        h = node.get("height")
        y_val = float(y) if isinstance(y, int | float) else 0.0
        h_val = float(h) if isinstance(h, int | float) else 0.0
        return y_val + h_val / 2

    def x_center(node: dict[str, Any]) -> float:
        x = node.get("x")
        w = node.get("width")
        x_val = float(x) if isinstance(x, int | float) else 0.0
        w_val = float(w) if isinstance(w, int | float) else 0.0
        return x_val + w_val / 2

    node_decl: dict[str, str] = {}
    node_y: dict[str, float] = {}
    node_center: dict[str, tuple[float, float]] = {}
    text_shapes: list[tuple[float, str]] = []
    unknown_composite_shape_types: set[str] = set()

    for raw_node in raw_nodes:
        if not isinstance(raw_node, dict):
            continue
        raw_id = raw_node.get("id")
        if not isinstance(raw_id, str):
            continue

        node_type = raw_node.get("type")
        if node_type == "image":
            continue

        if node_type == "text_shape":
            text_shapes.append((y_center(raw_node), esc(parse_text(raw_node))))
            continue

        if node_type != "composite_shape":
            continue

        alias = alias_of(raw_id)
        label = esc(parse_node_label(raw_node))
        shape_type = raw_node.get("composite_shape", {}).get("type")

        if shape_type == "diamond":
            node_decl[raw_id] = f"{alias}{{{label}}}"
        elif shape_type == "round_rect2":
            node_decl[raw_id] = f"{alias}([{label}])"
        elif shape_type in {"state_start", "state_end"}:
            node_decl[raw_id] = f"{alias}(({label}))"
        elif shape_type in {"rect", "pie"}:
            node_decl[raw_id] = f'{alias}["{label}"]'
        else:
            if shape_type not in (None, "round_rect"):
                unknown_composite_shape_types.add(str(shape_type))
            node_decl[raw_id] = f'{alias}["{label}"]'

        node_y[raw_id] = y_center(raw_node)
        node_center[raw_id] = (x_center(raw_node), y_center(raw_node))

    for raw_node in raw_nodes:
        if not isinstance(raw_node, dict):
            continue
        raw_id = raw_node.get("id")
        if not isinstance(raw_id, str):
            continue
        node_type = raw_node.get("type")
        if node_type not in {"table", "table_uml", "table_er", "life_line"}:
            continue

        alias = alias_of(raw_id)
        label = esc(parse_node_label(raw_node))
        node_decl[raw_id] = f'{alias}["{label}"]'
        node_y[raw_id] = y_center(raw_node)
        node_center[raw_id] = (x_center(raw_node), y_center(raw_node))

    if unknown_composite_shape_types:
        logger.warning(
            "Board flowchart conversion encountered unsupported composite_shape types: %s",
            ", ".join(sorted(unknown_composite_shape_types)),
        )

    if not node_decl:
        logger.warning(
            "Board flowchart conversion skipped: no supported composite_shape nodes"
        )
        return None

    def get_connector_node_id(connector: dict[str, Any], side: str) -> str | None:
        side_data = connector.get(side)
        if isinstance(side_data, dict):
            attached = side_data.get("attached_object")
            if isinstance(attached, dict):
                attached_id = attached.get("id")
                if isinstance(attached_id, str) and attached_id:
                    return attached_id

        fallback = connector.get(f"{side}_object")
        if isinstance(fallback, dict):
            fallback_id = fallback.get("id")
            if isinstance(fallback_id, str) and fallback_id:
                return fallback_id

        return None

    def get_arrow_style(connector: dict[str, Any], side: str) -> str:
        side_data = connector.get(side)
        if isinstance(side_data, dict):
            style = side_data.get("arrow_style")
            if isinstance(style, str):
                return style
        return "none"

    def get_connector_caption(connector: dict[str, Any]) -> str:
        captions = connector.get("captions", {}).get("data", [])
        if not isinstance(captions, list):
            return ""
        for item in captions:
            if not isinstance(item, dict):
                continue
            text = str(item.get("text", "")).strip()
            if text:
                return esc(text)
        return ""

    edge_records: list[tuple[str, str, str]] = []
    for raw_node in raw_nodes:
        if not isinstance(raw_node, dict) or raw_node.get("type") != "connector":
            continue

        connector = raw_node.get("connector")
        if not isinstance(connector, dict):
            continue

        start_id = get_connector_node_id(connector, "start")
        end_id = get_connector_node_id(connector, "end")
        if not isinstance(start_id, str) or not isinstance(end_id, str):
            continue

        if start_id not in node_decl:
            start_alias = alias_of(start_id)
            node_decl[start_id] = f'{start_alias}["{esc(start_id)}"]'
        if end_id not in node_decl:
            end_alias = alias_of(end_id)
            node_decl[end_id] = f'{end_alias}["{esc(end_id)}"]'

        start_style = get_arrow_style(connector, "start")
        end_style = get_arrow_style(connector, "end")

        src = alias_of(start_id)
        dst = alias_of(end_id)
        arrow = "---"

        if start_style != "none" and end_style != "none":
            arrow = "<-->"
        elif start_style != "none" and end_style == "none":
            src, dst = dst, src
            arrow = "-->"
        elif end_style != "none":
            arrow = "-->"

        caption = get_connector_caption(connector)
        if caption:
            edge_records.append((start_id, end_id, f"{src} {arrow}|{caption}| {dst}"))
        else:
            edge_records.append((start_id, end_id, f"{src} {arrow} {dst}"))

    adjacency: dict[str, set[str]] = {node_id: set() for node_id in node_decl}
    for start_id, end_id, _ in edge_records:
        adjacency.setdefault(start_id, set()).add(end_id)
        adjacency.setdefault(end_id, set()).add(start_id)

    components: list[list[str]] = []
    visited: set[str] = set()
    for node_id in sorted(node_decl, key=alias_of):
        if node_id in visited:
            continue
        stack = [node_id]
        visited.add(node_id)
        component: list[str] = []
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbor in adjacency.get(current, set()):
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                stack.append(neighbor)
        components.append(component)

    if not components:
        return None

    isolated_nodes = [
        node_id for node_id, neighbors in adjacency.items() if not neighbors and node_id in node_decl
    ]
    singleton_components = [component for component in components if len(component) == 1]
    node_count = len(node_decl)
    edge_count = len(edge_records)

    low_confidence_reasons: list[str] = []
    if node_count >= 4 and edge_count == 0:
        low_confidence_reasons.append("no connectors")
    if node_count >= 4 and len(singleton_components) == len(components):
        low_confidence_reasons.append("all components are isolated single nodes")
    if node_count >= 6 and len(isolated_nodes) / max(node_count, 1) >= 0.7:
        low_confidence_reasons.append("most nodes are isolated")

    if low_confidence_reasons:
        logger.warning(
            "Board flowchart conversion low confidence (%s): nodes=%d edges=%d components=%d isolated=%d; fallback to board link",
            ", ".join(low_confidence_reasons),
            node_count,
            edge_count,
            len(components),
            len(isolated_nodes),
        )
        return None

    sorted_titles = sorted(text_shapes, key=lambda item: item[0])

    def infer_direction(component_ids: list[str]) -> str:
        component_set = set(component_ids)
        horizontal_motion = 0.0
        vertical_motion = 0.0

        for start_id, end_id, _ in edge_records:
            if start_id not in component_set or end_id not in component_set:
                continue
            start_center = node_center.get(start_id)
            end_center = node_center.get(end_id)
            if start_center is None or end_center is None:
                continue
            horizontal_motion += abs(end_center[0] - start_center[0])
            vertical_motion += abs(end_center[1] - start_center[1])

        if horizontal_motion == 0 and vertical_motion == 0:
            x_values = [node_center[node_id][0] for node_id in component_ids if node_id in node_center]
            y_values = [node_center[node_id][1] for node_id in component_ids if node_id in node_center]
            if x_values and y_values:
                x_span = max(x_values) - min(x_values)
                y_span = max(y_values) - min(y_values)
                return "LR" if x_span > y_span else "TD"
            return "TD"

        return "LR" if horizontal_motion > vertical_motion else "TD"

    mermaid_blocks: list[Block] = []
    for component in components:
        component_sorted = sorted(component, key=alias_of)
        component_set = set(component_sorted)

        lines: list[str] = [f"flowchart {infer_direction(component_sorted)}"]

        if sorted_titles:
            y_values = [node_y[node_id] for node_id in component_sorted if node_id in node_y]
            if y_values:
                center_y = sum(y_values) / len(y_values)
                _, nearest_title = min(
                    sorted_titles,
                    key=lambda item: abs(item[0] - center_y),
                )
                lines.append(f"%% {nearest_title}")

        for raw_id in component_sorted:
            lines.append(f"  {node_decl[raw_id]}")

        for start_id, end_id, edge_line in edge_records:
            if start_id in component_set and end_id in component_set:
                lines.append(f"  {edge_line}")

        mermaid_blocks.append(_build_mermaid_code_block("\n".join(lines)))

    if len(mermaid_blocks) == 1:
        return mermaid_blocks[0]

    return Block(type=BlockType.Passthrough, children=mermaid_blocks)

def _convert_whiteboard_pie_chart(raw_nodes: list[Any]) -> Block | None:
    pie_groups: dict[tuple[float, float, float, float], list[dict[str, Any]]] = {}
    rect_nodes: list[dict[str, Any]] = []
    text_nodes: list[dict[str, Any]] = []

    for raw_node in raw_nodes:
        if not isinstance(raw_node, dict):
            continue
        node_type = raw_node.get("type")

        if node_type == "text_shape":
            text_nodes.append(raw_node)
            continue

        if node_type != "composite_shape":
            continue

        composite_shape = raw_node.get("composite_shape")
        if not isinstance(composite_shape, dict):
            continue

        shape_type = composite_shape.get("type")
        if shape_type == "rect":
            rect_nodes.append(raw_node)
            continue

        if shape_type != "pie":
            continue

        pie = composite_shape.get("pie")
        if not isinstance(pie, dict):
            continue

        central_angle = pie.get("central_angle")
        if not isinstance(central_angle, int | float) or central_angle <= 0:
            continue

        key = (
            round(number(raw_node.get("x")), 3),
            round(number(raw_node.get("y")), 3),
            round(number(raw_node.get("width")), 3),
            round(number(raw_node.get("height")), 3),
        )
        pie_groups.setdefault(key, []).append(raw_node)

    if not pie_groups:
        return None

    pie_nodes = max(pie_groups.values(), key=len)
    if len(pie_nodes) < 2:
        return None

    def extract_text(node: dict[str, Any]) -> str:
        text = node.get("text")
        if isinstance(text, dict):
            return str(text.get("text", "")).strip()
        if isinstance(text, str):
            return text.strip()
        return ""

    def center(node: dict[str, Any]) -> tuple[float, float]:
        x = number(node.get("x"))
        y = number(node.get("y"))
        w = number(node.get("width"))
        h = number(node.get("height"))
        return x + w / 2, y + h / 2

    legend_by_color: dict[str, str] = {}
    for rect_node in rect_nodes:
        style = rect_node.get("style")
        if not isinstance(style, dict):
            continue
        fill_color = style.get("fill_color")
        if not isinstance(fill_color, str) or not fill_color:
            continue

        rx, ry = center(rect_node)
        rw = number(rect_node.get("width"))
        best_text: tuple[float, str] | None = None
        for text_node in text_nodes:
            text = extract_text(text_node)
            if not text:
                continue
            tx, ty = center(text_node)
            if tx < rx + rw * 0.5:
                continue
            distance = abs(ty - ry) + max(0.0, tx - rx - rw)
            if best_text is None or distance < best_text[0]:
                best_text = (distance, text)

        if best_text is not None:
            legend_by_color.setdefault(fill_color.lower(), best_text[1])

    def pick_title() -> str | None:
        bx, by = center(pie_nodes[0])
        best: tuple[float, str] | None = None
        for text_node in text_nodes:
            text = extract_text(text_node)
            if not text or re.fullmatch(r"\d+(?:\.\d+)?%", text):
                continue
            tx, ty = center(text_node)
            if ty >= by:
                continue
            distance = abs(tx - bx) + abs(ty - by)
            if best is None or distance < best[0]:
                best = (distance, text)
        if best is None:
            return None
        return best[1]

    title = pick_title()

    def normalize_value(value: float) -> str:
        rounded = round(value, 2)
        if rounded.is_integer():
            return str(int(rounded))
        return f"{rounded:.2f}".rstrip("0").rstrip(".")

    pie_nodes_sorted = sorted(
        pie_nodes,
        key=lambda item: float(
            number(
                item.get("composite_shape", {}).get("pie", {}).get("start_radial_line_angle")
            )
        ),
    )

    used_labels: set[str] = set()
    lines: list[str] = ["pie showData"]
    if title:
        safe_title = title.replace('"', "'")
        lines.append(f"  title {safe_title}")

    for index, pie_node in enumerate(pie_nodes_sorted, start=1):
        composite_shape = pie_node.get("composite_shape", {})
        pie = composite_shape.get("pie", {})
        central_angle = number(pie.get("central_angle"))
        value = central_angle / 360 * 100

        style = pie_node.get("style")
        fill_color = ""
        if isinstance(style, dict):
            candidate = style.get("fill_color")
            if isinstance(candidate, str):
                fill_color = candidate.lower()

        label = legend_by_color.get(fill_color, "")
        if not label:
            label = f"part_{index}"
        if label in used_labels:
            label = f"{label}_{index}"
        used_labels.add(label)

        safe_label = label.replace('"', "'")
        lines.append(f'  "{safe_label}" : {normalize_value(value)}')

    return _build_mermaid_code_block("\n".join(lines))

def _convert_whiteboard_mindmap(raw_nodes: list[Any]) -> Block:
    nodes: dict[str, dict[str, Any]] = {}
    for node in raw_nodes:
        if not isinstance(node, dict):
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str):
            continue
        if node.get("type") == "mind_map":
            nodes[node_id] = node

    children_map: dict[str, list[str]] = {}
    for node in nodes.values():
        parent_id = node.get("mind_map", {}).get("parent_id", "")
        if parent_id and parent_id in nodes:
            children_map.setdefault(parent_id, []).append(node["id"])

    root_nodes = [
        node
        for node in nodes.values()
        if not node.get("mind_map", {}).get("parent_id")
    ]
    if not root_nodes:
        if nodes:
            logger.warning(
                "Board mindmap conversion encountered unsupported structure: root node missing"
            )
        else:
            logger.warning(
                "Board mindmap conversion skipped: no supported mind_map nodes"
            )
        return _empty_mermaid_code_block()

    def escape_text(text: str) -> str:
        cleaned = text.strip()
        cleaned = re.sub(r"[\r\n]+", " ", cleaned)
        cleaned = cleaned.replace('"', "'")
        return cleaned or "(空)"

    def get_text(node: dict[str, Any]) -> str:
        text = node.get("text", {})
        if isinstance(text, dict):
            return str(text.get("text", ""))
        return str(text)

    def render_node(node_id: str, depth: int = 0) -> list[str]:
        node = nodes[node_id]
        text = escape_text(get_text(node))
        indent = "  " * (depth + 2)
        lines = [f"{indent}{text}"]
        for child_id in children_map.get(node_id, []):
            lines.extend(render_node(child_id, depth + 1))
        return lines

    root = root_nodes[0]
    root_text = escape_text(get_text(root))
    lines = ["mindmap", f"  root(({root_text}))"]
    for child_id in children_map.get(root["id"], []):
        lines.extend(render_node(child_id, 0))

    return Block(
        type=BlockType.Code,
        inlines=[InlineText(text="\n".join(lines), marks=[])],
        attrs={"language": "mermaid"},
    )

def _empty_mermaid_code_block() -> Block:
    return Block(type=BlockType.Code, attrs={"language": "mermaid"})

def _build_mermaid_code_block(content: str) -> Block:
    return Block(
        type=BlockType.Code,
        inlines=[InlineText(text=content, marks=[])],
        attrs={"language": "mermaid"},
    )
