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

def test_convert_whiteboard_pie_chart_keeps_ratio_and_labels() -> None:
    data = {
        "nodes": [
            {
                "id": "title",
                "type": "text_shape",
                "x": 104.76,
                "y": -84.75,
                "width": 230.46,
                "height": 34.75,
                "text": {"text": "Request Distribution"},
            },
            {
                "id": "p1",
                "type": "composite_shape",
                "x": 0,
                "y": 0,
                "width": 440,
                "height": 440,
                "style": {"fill_color": "#d6dcf3"},
                "composite_shape": {
                    "type": "pie",
                    "pie": {"start_radial_line_angle": 54, "central_angle": 144, "radius": 55},
                },
            },
            {
                "id": "p2",
                "type": "composite_shape",
                "x": 0,
                "y": 0,
                "width": 440,
                "height": 440,
                "style": {"fill_color": "#8569cb"},
                "composite_shape": {
                    "type": "pie",
                    "pie": {
                        "start_radial_line_angle": 162,
                        "central_angle": 108,
                        "radius": 55,
                    },
                },
            },
            {
                "id": "p3",
                "type": "composite_shape",
                "x": 0,
                "y": 0,
                "width": 440,
                "height": 440,
                "style": {"fill_color": "#fef1ce"},
                "composite_shape": {
                    "type": "pie",
                    "pie": {"start_radial_line_angle": 234, "central_angle": 72, "radius": 55},
                },
            },
            {
                "id": "p4",
                "type": "composite_shape",
                "x": 0,
                "y": 0,
                "width": 440,
                "height": 440,
                "style": {"fill_color": "#5178c6"},
                "composite_shape": {
                    "type": "pie",
                    "pie": {"start_radial_line_angle": 270, "central_angle": 36, "radius": 55},
                },
            },
            {
                "id": "l1-box",
                "type": "composite_shape",
                "x": 490,
                "y": 172.5,
                "width": 20,
                "height": 20,
                "style": {"fill_color": "#d6dcf3"},
                "composite_shape": {"type": "rect"},
            },
            {
                "id": "l1-text",
                "type": "text_shape",
                "x": 515,
                "y": 172.5,
                "width": 31,
                "height": 20,
                "text": {"text": "docx"},
            },
            {
                "id": "l2-box",
                "type": "composite_shape",
                "x": 490,
                "y": 197.5,
                "width": 20,
                "height": 20,
                "style": {"fill_color": "#8569cb"},
                "composite_shape": {"type": "rect"},
            },
            {
                "id": "l2-text",
                "type": "text_shape",
                "x": 515,
                "y": 197.5,
                "width": 24,
                "height": 20,
                "text": {"text": "doc"},
            },
            {
                "id": "l3-box",
                "type": "composite_shape",
                "x": 490,
                "y": 222.5,
                "width": 20,
                "height": 20,
                "style": {"fill_color": "#fef1ce"},
                "composite_shape": {"type": "rect"},
            },
            {
                "id": "l3-text",
                "type": "text_shape",
                "x": 515,
                "y": 222.5,
                "width": 35,
                "height": 20,
                "text": {"text": "sheet"},
            },
            {
                "id": "l4-box",
                "type": "composite_shape",
                "x": 490,
                "y": 247.5,
                "width": 20,
                "height": 20,
                "style": {"fill_color": "#5178c6"},
                "composite_shape": {"type": "rect"},
            },
            {
                "id": "l4-text",
                "type": "text_shape",
                "x": 515,
                "y": 247.5,
                "width": 35,
                "height": 20,
                "text": {"text": "other"},
            },
        ]
    }

    block = convert_whiteboard_to_mermaid_code_block(data)

    assert block.attrs.get("language") == "mermaid"
    assert len(block.inlines) == 1
    assert block.inlines[0].text.startswith("pie showData")
    assert "title Request Distribution" in block.inlines[0].text
    assert '"docx" : 40' in block.inlines[0].text
    assert '"doc" : 30' in block.inlines[0].text
    assert '"sheet" : 20' in block.inlines[0].text
    assert '"other" : 10' in block.inlines[0].text

def test_convert_whiteboard_flowchart_low_confidence_returns_none(caplog) -> None:
    data = {
        "nodes": [
            {
                "id": "n1",
                "type": "composite_shape",
                "x": 0,
                "y": 0,
                "width": 100,
                "height": 60,
                "text": {"text": "A"},
                "composite_shape": {"type": "rect"},
            },
            {
                "id": "n2",
                "type": "composite_shape",
                "x": 180,
                "y": 0,
                "width": 100,
                "height": 60,
                "text": {"text": "B"},
                "composite_shape": {"type": "rect"},
            },
            {
                "id": "n3",
                "type": "composite_shape",
                "x": 360,
                "y": 0,
                "width": 100,
                "height": 60,
                "text": {"text": "C"},
                "composite_shape": {"type": "rect"},
            },
            {
                "id": "n4",
                "type": "composite_shape",
                "x": 540,
                "y": 0,
                "width": 100,
                "height": 60,
                "text": {"text": "D"},
                "composite_shape": {"type": "rect"},
            },
        ]
    }

    with caplog.at_level(logging.WARNING):
        block = convert_whiteboard_to_mermaid_code_block(data)

    assert block is None
    assert "low confidence" in caplog.text
    assert "fallback to board link" in caplog.text
