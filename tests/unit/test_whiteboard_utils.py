from __future__ import annotations

import logging

from feishu_easy.convert.from_feishu.utils import convert_whiteboard_to_mermaid_code_block


def test_convert_whiteboard_flowchart_supports_lifeline_and_table_nodes(
    caplog,
) -> None:
    data = {
        "nodes": [
            {
                "id": "life-1",
                "type": "life_line",
                "x": 0,
                "y": 0,
                "width": 80,
                "height": 120,
                "text": {"text": "调用者"},
                "lifeline": {"type": "actor_lifeline"},
            },
            {
                "id": "uml-1",
                "type": "table_uml",
                "x": 200,
                "y": 0,
                "width": 180,
                "height": 100,
                "table": {"title": "UserService"},
            },
            {
                "id": "er-1",
                "type": "table_er",
                "x": 420,
                "y": 0,
                "width": 180,
                "height": 100,
                "table": {"title": "users"},
            },
            {
                "id": "conn-1",
                "type": "connector",
                "connector": {
                    "start": {
                        "attached_object": {"id": "life-1"},
                        "arrow_style": "none",
                    },
                    "end": {
                        "attached_object": {"id": "uml-1"},
                        "arrow_style": "line_arrow",
                    },
                },
            },
            {
                "id": "conn-2",
                "type": "connector",
                "connector": {
                    "start": {
                        "attached_object": {"id": "uml-1"},
                        "arrow_style": "none",
                    },
                    "end": {
                        "attached_object": {"id": "er-1"},
                        "arrow_style": "line_arrow",
                    },
                },
            },
        ]
    }

    with caplog.at_level(logging.WARNING):
        block = convert_whiteboard_to_mermaid_code_block(data)

    assert block.attrs.get("language") == "mermaid"
    assert len(block.inlines) == 1
    assert "flowchart" in block.inlines[0].text
    assert "调用者" in block.inlines[0].text
    assert "UserService" in block.inlines[0].text
    assert "users" in block.inlines[0].text
    assert "no supported composite_shape nodes" not in caplog.text
    assert "unsupported node types: life_line" not in caplog.text
    assert "unsupported node types: table_uml" not in caplog.text
    assert "unsupported node types: table_er" not in caplog.text


def test_convert_whiteboard_flowchart_supports_more_composite_shape_types(caplog) -> None:
    data = {
        "nodes": [
            {
                "id": "start",
                "type": "composite_shape",
                "x": 0,
                "y": 0,
                "width": 80,
                "height": 60,
                "text": {"text": "开始"},
                "composite_shape": {"type": "state_start"},
            },
            {
                "id": "step",
                "type": "composite_shape",
                "x": 180,
                "y": 0,
                "width": 120,
                "height": 60,
                "text": {"text": "处理"},
                "composite_shape": {"type": "rect"},
            },
            {
                "id": "slice",
                "type": "composite_shape",
                "x": 360,
                "y": 0,
                "width": 120,
                "height": 60,
                "text": {"text": "统计"},
                "composite_shape": {"type": "pie"},
            },
            {
                "id": "end",
                "type": "composite_shape",
                "x": 540,
                "y": 0,
                "width": 80,
                "height": 60,
                "text": {"text": "结束"},
                "composite_shape": {"type": "state_end"},
            },
            {
                "id": "line-1",
                "type": "connector",
                "connector": {
                    "start": {
                        "attached_object": {"id": "start"},
                        "arrow_style": "none",
                    },
                    "end": {
                        "attached_object": {"id": "step"},
                        "arrow_style": "line_arrow",
                    },
                },
            },
            {
                "id": "line-2",
                "type": "connector",
                "connector": {
                    "start": {
                        "attached_object": {"id": "step"},
                        "arrow_style": "none",
                    },
                    "end": {
                        "attached_object": {"id": "slice"},
                        "arrow_style": "line_arrow",
                    },
                },
            },
            {
                "id": "line-3",
                "type": "connector",
                "connector": {
                    "start": {
                        "attached_object": {"id": "slice"},
                        "arrow_style": "none",
                    },
                    "end": {
                        "attached_object": {"id": "end"},
                        "arrow_style": "line_arrow",
                    },
                },
            },
        ]
    }

    with caplog.at_level(logging.WARNING):
        block = convert_whiteboard_to_mermaid_code_block(data)

    assert block.attrs.get("language") == "mermaid"
    assert len(block.inlines) == 1
    assert "flowchart" in block.inlines[0].text
    assert "unsupported composite_shape types: state_end, state_start" not in caplog.text
    assert "unsupported composite_shape types: pie, rect" not in caplog.text
