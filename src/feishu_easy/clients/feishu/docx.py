from __future__ import annotations

from typing import Any

from lark_oapi.api.docx.v1 import (
    BatchDeleteDocumentBlockChildrenRequest,
    BatchDeleteDocumentBlockChildrenRequestBody,
    ConvertDocumentRequest,
    ConvertDocumentRequestBody,
    CreateDocumentBlockDescendantRequest,
    CreateDocumentRequest,
    CreateDocumentRequestBody,
    GetDocumentBlockRequest,
    GetDocumentBlockChildrenRequest,
    GetDocumentRequest,
    ListDocumentBlockRequest,
    PatchDocumentBlockRequest,
    RawContentDocumentRequest,
)

from .base import _BaseAPIGroup


class FeishuDocxAPI(_BaseAPIGroup):
    def get_document(self, document_id: str) -> dict[str, Any]:
        option = self._request_option()
        request = GetDocumentRequest.builder().document_id(document_id).build()

        response = self._call_with_retry(
            "client.docx.v1.document.get",
            lambda: self._parent.client.docx.v1.document.get(request, option),
        )
        return self._marshal_data(response.data)

    def create_document(self, title: str, folder_token: str) -> dict[str, Any]:
        option = self._request_option()
        request = (
            CreateDocumentRequest.builder()
            .request_body(
                CreateDocumentRequestBody.builder()
                .folder_token(folder_token)
                .title(title)
                .build()
            )
            .build()
        )

        response = self._call_with_retry(
            "client.docx.v1.document.create",
            lambda: self._parent.client.docx.v1.document.create(request, option),
        )
        return self._marshal_data(response.data)

    def raw_content(self, document_id: str, lang: int = 0) -> dict[str, Any]:
        option = self._request_option()
        request = (
            RawContentDocumentRequest.builder()
            .document_id(document_id)
            .lang(lang)
            .build()
        )

        response = self._call_with_retry(
            "client.docx.v1.document.raw_content",
            lambda: self._parent.client.docx.v1.document.raw_content(request, option),
        )
        return self._marshal_data(response.data)

    def convert_document(self, content: str, content_type: str) -> dict[str, Any]:
        option = self._request_option()
        request = (
            ConvertDocumentRequest.builder()
            .request_body(
                ConvertDocumentRequestBody.builder()
                .content_type(content_type)
                .content(content)
                .build()
            )
            .build()
        )

        response = self._call_with_retry(
            "client.docx.v1.document.convert",
            lambda: self._parent.client.docx.v1.document.convert(request, option),
        )
        return self._marshal_data(response.data)

    def create_document_block_descendant(
        self, document_id: str, block_id: str, request_body: dict[str, Any]
    ) -> dict[str, Any]:
        option = self._request_option()
        request = (
            CreateDocumentBlockDescendantRequest.builder()
            .document_revision_id(-1)
            .document_id(document_id)
            .block_id(block_id)
            .request_body(request_body)
            .build()
        )

        response = self._call_with_retry(
            "client.docx.v1.document_block_descendant.create",
            lambda: self._parent.client.docx.v1.document_block_descendant.create(
                request, option
            ),
        )
        return self._marshal_data(response.data)

    def get_document_block_children(
        self, document_id: str, block_id: str
    ) -> dict[str, Any]:
        option = self._request_option()
        request = (
            GetDocumentBlockChildrenRequest.builder()
            .document_revision_id(-1)
            .page_size(500)
            .with_descendants(False)
            .document_id(document_id)
            .block_id(block_id)
            .build()
        )

        response = self._call_with_retry(
            "client.docx.v1.document_block_children.get",
            lambda: self._parent.client.docx.v1.document_block_children.get(
                request, option
            ),
        )
        result = self._marshal_data(response.data)

        while result.get("has_more"):
            request = (
                GetDocumentBlockChildrenRequest.builder()
                .document_revision_id(-1)
                .page_size(500)
                .page_token(result["page_token"])
                .with_descendants(False)
                .document_id(document_id)
                .block_id(block_id)
                .build()
            )

            response = self._call_with_retry(
                "client.docx.v1.document_block_children.get",
                lambda: self._parent.client.docx.v1.document_block_children.get(
                    request, option
                ),
            )

            new_result = self._marshal_data(response.data)
            new_result["items"] = result["items"] + new_result["items"]
            result = new_result

        return result

    def get_document_block(
        self,
        document_id: str,
        block_id: str,
        document_revision_id: int = -1,
    ) -> dict[str, Any]:
        option = self._request_option()
        request = (
            GetDocumentBlockRequest.builder()
            .document_id(document_id)
            .block_id(block_id)
            .document_revision_id(document_revision_id)
            .build()
        )

        response = self._call_with_retry(
            "client.docx.v1.document_block.get",
            lambda: self._parent.client.docx.v1.document_block.get(request, option),
        )
        return self._marshal_data(response.data)

    def batch_delete_document_block_children(
        self, document_id: str, block_id: str, start_index: int, end_index: int
    ) -> dict[str, Any]:
        option = self._request_option()
        request = (
            BatchDeleteDocumentBlockChildrenRequest.builder()
            .document_revision_id(-1)
            .document_id(document_id)
            .block_id(block_id)
            .request_body(
                BatchDeleteDocumentBlockChildrenRequestBody.builder()
                .start_index(start_index)
                .end_index(end_index)
                .build()
            )
            .build()
        )

        response = self._call_with_retry(
            "client.docx.v1.document_block_children.batch_delete",
            lambda: self._parent.client.docx.v1.document_block_children.batch_delete(
                request, option
            ),
        )
        return self._marshal_data(response.data)

    def list_document_block(
        self,
        document_id: str,
        document_revision_id: int = -1,
    ) -> dict[str, Any]:
        page_size = 500
        option = self._request_option()
        request = (
            ListDocumentBlockRequest.builder()
            .document_id(document_id)
            .page_size(page_size)
            .document_revision_id(document_revision_id)
            .build()
        )

        response = self._call_with_retry(
            "client.docx.v1.document_block.list",
            lambda: self._parent.client.docx.v1.document_block.list(request, option),
        )
        result = self._marshal_data(response.data)

        while result.get("has_more"):
            request = (
                ListDocumentBlockRequest.builder()
                .document_id(document_id)
                .page_size(page_size)
                .document_revision_id(document_revision_id)
                .page_token(result["page_token"])
                .build()
            )
            response = self._call_with_retry(
                "client.docx.v1.document_block.list",
                lambda: self._parent.client.docx.v1.document_block.list(
                    request, option
                ),
            )
            new_result = self._marshal_data(response.data)
            new_result["items"] = result["items"] + new_result["items"]
            result = new_result

        return result

    def patch_document_block(
        self,
        document_id: str,
        block_id: str,
        request_body: dict[str, Any],
        document_revision_id: int = -1,
    ) -> dict[str, Any]:
        option = self._request_option()
        request = (
            PatchDocumentBlockRequest.builder()
            .document_revision_id(document_revision_id)
            .block_id(block_id)
            .document_id(document_id)
            .request_body(request_body)
            .build()
        )

        response = self._call_with_retry(
            "client.docx.v1.document_block.patch",
            lambda: self._parent.client.docx.v1.document_block.patch(request, option),
        )
        return self._marshal_data(response.data)
