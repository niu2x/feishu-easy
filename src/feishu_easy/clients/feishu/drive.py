from __future__ import annotations

import zlib
from pathlib import Path
from typing import Any

from lark_oapi.api.drive.v1 import (
    BatchQueryMetaRequest,
    CopyFileRequest,
    CopyFileRequestBody,
    DeleteFileRequest,
    DeleteSubscribeFileRequest,
    DownloadFileRequest,
    DownloadMediaRequest,
    GetFileStatisticsRequest,
    GetSubscribeFileRequest,
    ListFileRequest,
    ListFileVersionRequest,
    ListFileViewRecordRequest,
    MetaRequest,
    MoveFileRequest,
    MoveFileRequestBody,
    RequestDoc,
    SubscribeFileRequest,
    UploadAllFileRequest,
    UploadAllFileRequestBody,
    UploadAllMediaRequest,
    UploadAllMediaRequestBody,
)

from .base import _BaseAPIGroup
from .constants import (
    DRIVE_LIST_FILE_PAGE_SIZE,
    DRIVE_LIST_FILE_VERSION_PAGE_SIZE,
    DRIVE_LIST_FILE_VIEW_RECORD_PAGE_SIZE,
)


class FeishuDriveAPI(_BaseAPIGroup):
    @staticmethod
    def _file_adler32(path: Path) -> str:
        checksum = 1
        with open(path, "rb") as file:
            while chunk := file.read(65536):
                checksum = zlib.adler32(chunk, checksum)
        return str(checksum & 0xFFFFFFFF)

    @staticmethod
    def _build_list_file_request(
        folder_token: str | None,
        order_by: str | None,
        direction: str | None,
        user_id_type: str | None,
        page_token: str | None = None,
    ) -> ListFileRequest:
        request_builder = ListFileRequest.builder().page_size(DRIVE_LIST_FILE_PAGE_SIZE)
        if page_token:
            request_builder = request_builder.page_token(page_token)
        if folder_token:
            request_builder = request_builder.folder_token(folder_token)
        if order_by:
            request_builder = request_builder.order_by(order_by)
        if direction:
            request_builder = request_builder.direction(direction)
        if user_id_type:
            request_builder = request_builder.user_id_type(user_id_type)
        return request_builder.build()

    def list_file(
        self,
        folder_token: str | None = None,
        order_by: str | None = None,
        direction: str | None = None,
        user_id_type: str | None = None,
    ) -> dict[str, Any]:
        option = self._request_option()

        request = self._build_list_file_request(
            folder_token=folder_token,
            order_by=order_by,
            direction=direction,
            user_id_type=user_id_type,
        )

        response = self._call_with_retry(
            "client.drive.v1.file.list",
            lambda: self._parent.client.drive.v1.file.list(request, option),
        )
        result = self._marshal_data(response.data)

        while result.get("has_more"):
            next_page_token = result.get("page_token") or result.get("next_page_token")
            if not next_page_token:
                break

            request = self._build_list_file_request(
                folder_token=folder_token,
                order_by=order_by,
                direction=direction,
                user_id_type=user_id_type,
                page_token=next_page_token,
            )

            response = self._call_with_retry(
                "client.drive.v1.file.list",
                lambda: self._parent.client.drive.v1.file.list(request, option),
            )
            new_result = self._marshal_data(response.data)
            new_result["files"] = result.get("files", []) + new_result.get("files", [])
            result = new_result

        return result

    @staticmethod
    def _build_list_file_view_record_request(
        file_token: str | None,
        file_type: str | None,
        viewer_id_type: str | None,
        page_size: int | None,
        page_token: str | None = None,
    ) -> ListFileViewRecordRequest:
        request_builder = ListFileViewRecordRequest.builder()
        if page_size is not None:
            request_builder = request_builder.page_size(page_size)
        else:
            request_builder = request_builder.page_size(
                DRIVE_LIST_FILE_VIEW_RECORD_PAGE_SIZE
            )
        if page_token:
            request_builder = request_builder.page_token(page_token)
        if file_token:
            request_builder = request_builder.file_token(file_token)
        if file_type:
            request_builder = request_builder.file_type(file_type)
        if viewer_id_type:
            request_builder = request_builder.viewer_id_type(viewer_id_type)
        return request_builder.build()

    @staticmethod
    def _build_list_file_version_request(
        file_token: str,
        obj_type: str,
        page_size: int | None,
        user_id_type: str | None,
        page_token: str | None = None,
    ) -> ListFileVersionRequest:
        request_builder = ListFileVersionRequest.builder().file_token(file_token)
        if page_size is not None:
            request_builder = request_builder.page_size(page_size)
        else:
            request_builder = request_builder.page_size(
                DRIVE_LIST_FILE_VERSION_PAGE_SIZE
            )
        if page_token:
            request_builder = request_builder.page_token(page_token)
        request_builder = request_builder.obj_type(obj_type)
        if user_id_type:
            request_builder = request_builder.user_id_type(user_id_type)
        return request_builder.build()

    def get_file_statistics(
        self,
        file_token: str,
        file_type: str = "file",
    ) -> dict[str, Any]:
        option = self._request_option()
        request = (
            GetFileStatisticsRequest.builder()
            .file_token(file_token)
            .file_type(file_type)
            .build()
        )

        response = self._call_with_retry(
            "client.drive.v1.file_statistics.get",
            lambda: self._parent.client.drive.v1.file_statistics.get(request, option),
        )
        return self._marshal_data(response.data)

    def list_file_view_record(
        self,
        file_token: str,
        file_type: str = "file",
        viewer_id_type: str | None = "open_id",
        page_size: int | None = None,
    ) -> dict[str, Any]:
        option = self._request_option()
        request = self._build_list_file_view_record_request(
            file_token=file_token,
            file_type=file_type,
            viewer_id_type=viewer_id_type,
            page_size=page_size,
        )

        response = self._call_with_retry(
            "client.drive.v1.file_view_record.list",
            lambda: self._parent.client.drive.v1.file_view_record.list(request, option),
        )
        result = self._marshal_data(response.data)

        while result.get("has_more"):
            next_page_token = result.get("page_token") or result.get("next_page_token")
            if not next_page_token:
                break

            request = self._build_list_file_view_record_request(
                file_token=file_token,
                file_type=file_type,
                viewer_id_type=viewer_id_type,
                page_size=page_size,
                page_token=next_page_token,
            )
            response = self._call_with_retry(
                "client.drive.v1.file_view_record.list",
                lambda: self._parent.client.drive.v1.file_view_record.list(
                    request, option
                ),
            )

            new_result = self._marshal_data(response.data)
            merged_result = dict(new_result)
            for key, value in new_result.items():
                current_value = result.get(key)
                if isinstance(value, list) and isinstance(current_value, list):
                    merged_result[key] = current_value + value
            result = merged_result

        return result

    def list_file_version(
        self,
        file_token: str,
        obj_type: str,
        page_size: int | None = None,
        user_id_type: str | None = None,
    ) -> dict[str, Any]:
        page_size = 5

        option = self._request_option()
        request = self._build_list_file_version_request(
            file_token=file_token,
            obj_type=obj_type,
            page_size=page_size,
            user_id_type=user_id_type,
        )

        response = self._call_with_retry(
            "client.drive.v1.file_version.list",
            lambda: self._parent.client.drive.v1.file_version.list(request, option),
        )
        result = self._marshal_data(response.data)

        while result.get("has_more"):
            next_page_token = result.get("page_token") or result.get("next_page_token")
            if not next_page_token:
                break

            request = self._build_list_file_version_request(
                file_token=file_token,
                obj_type=obj_type,
                page_size=page_size,
                user_id_type=user_id_type,
                page_token=next_page_token,
            )

            response = self._call_with_retry(
                "client.drive.v1.file_version.list",
                lambda: self._parent.client.drive.v1.file_version.list(request, option),
            )

            new_result = self._marshal_data(response.data)
            merged_result = dict(new_result)
            for key, value in new_result.items():
                current_value = result.get(key)
                if isinstance(value, list) and isinstance(current_value, list):
                    merged_result[key] = current_value + value
            result = merged_result

        return result

    def delete_file(self, file_token: str, file_type: str = "file") -> dict[str, Any]:
        option = self._request_option()
        request = (
            DeleteFileRequest.builder().file_token(file_token).type(file_type).build()
        )

        response = self._call_with_retry(
            "client.drive.v1.file.delete",
            lambda: self._parent.client.drive.v1.file.delete(request, option),
        )
        return self._marshal_data(response.data)

    def copy_file(
        self,
        file_token: str,
        file_type: str = "file",
        folder_token: str | None = None,
        name: str | None = None,
        user_id_type: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        option = self._request_option()
        request_body_builder = CopyFileRequestBody.builder().type(file_type)
        if folder_token:
            request_body_builder = request_body_builder.folder_token(folder_token)
        if name:
            request_body_builder = request_body_builder.name(name)
        if extra:
            request_body_builder = request_body_builder.extra(extra)

        request_builder = (
            CopyFileRequest.builder()
            .file_token(file_token)
            .request_body(request_body_builder.build())
        )
        if user_id_type:
            request_builder = request_builder.user_id_type(user_id_type)
        request = request_builder.build()

        response = self._call_with_retry(
            "client.drive.v1.file.copy",
            lambda: self._parent.client.drive.v1.file.copy(request, option),
        )
        return self._marshal_data(response.data)

    def move_file(
        self,
        file_token: str,
        file_type: str = "file",
        folder_token: str | None = None,
    ) -> dict[str, Any]:
        option = self._request_option()
        request_body_builder = MoveFileRequestBody.builder().type(file_type)
        if folder_token:
            request_body_builder = request_body_builder.folder_token(folder_token)
        request = (
            MoveFileRequest.builder()
            .file_token(file_token)
            .request_body(request_body_builder.build())
            .build()
        )

        response = self._call_with_retry(
            "client.drive.v1.file.move",
            lambda: self._parent.client.drive.v1.file.move(request, option),
        )
        return self._marshal_data(response.data)

    def batch_query_meta(
        self,
        request_docs: list[tuple[str, str]],
        with_url: bool = True,
        user_id_type: str | None = None,
    ) -> dict[str, Any]:
        option = self._request_option()
        docs = [
            RequestDoc.builder().doc_token(doc_token).doc_type(doc_type).build()
            for doc_token, doc_type in request_docs
        ]

        request_builder = BatchQueryMetaRequest.builder().request_body(
            MetaRequest.builder().request_docs(docs).with_url(with_url).build()
        )
        if user_id_type:
            request_builder = request_builder.user_id_type(user_id_type)
        request = request_builder.build()

        response = self._call_with_retry(
            "client.drive.v1.meta.batch_query",
            lambda: self._parent.client.drive.v1.meta.batch_query(request, option),
        )
        return self._marshal_data(response.data)

    def upload_file(
        self,
        local_file: Path,
        folder_token: str,
        file_name: str | None = None,
    ) -> dict[str, Any]:
        if not local_file.exists():
            raise FileNotFoundError(f"File not found: {local_file}")
        if not local_file.is_file():
            raise ValueError(f"Not a regular file: {local_file}")

        option = self._request_option()
        resolved_file_name = file_name or local_file.name
        file_size = local_file.stat().st_size
        checksum = self._file_adler32(local_file)

        with open(local_file, "rb") as file:
            request = (
                UploadAllFileRequest.builder()
                .request_body(
                    UploadAllFileRequestBody.builder()
                    .file_name(resolved_file_name)
                    .parent_type("explorer")
                    .parent_node(folder_token)
                    .size(str(file_size))
                    .checksum(checksum)
                    .file(file)
                    .build()
                )
                .build()
            )

            response = self._call_with_retry(
                "client.drive.v1.file.upload_all",
                lambda: self._parent.client.drive.v1.file.upload_all(request, option),
            )

        return self._marshal_data(response.data)

    def download_file(self, file_token: str) -> tuple[str, bytes]:
        option = self._request_option()
        request = DownloadFileRequest.builder().file_token(file_token).build()

        response = self._call_with_retry(
            "client.drive.v1.file.download",
            lambda: self._parent.client.drive.v1.file.download(request, option),
        )

        if not isinstance(response.file_name, str) or not response.file_name:
            raise RuntimeError(
                "client.drive.v1.file.download failed: file_name missing"
            )
        if response.file is None:
            raise RuntimeError(
                "client.drive.v1.file.download failed: file stream missing"
            )

        return response.file_name, bytes(response.file.read())

    def download_media(self, file_token: str) -> tuple[str, bytes]:
        option = self._request_option()
        request = DownloadMediaRequest.builder().file_token(file_token).build()

        response = self._call_with_retry(
            "client.drive.v1.media.download",
            lambda: self._parent.client.drive.v1.media.download(request, option),
        )

        if not isinstance(response.file_name, str) or not response.file_name:
            raise RuntimeError(
                "client.drive.v1.media.download failed: file_name missing"
            )
        if response.file is None:
            raise RuntimeError(
                "client.drive.v1.media.download failed: file stream missing"
            )

        return response.file_name, bytes(response.file.read())

    def upload_media(
        self,
        local_file: Path,
        parent_type: str,
        parent_node: str,
        file_name: str | None = None,
        extra: dict[str, Any] | None = None,
        checksum: str | None = None,
    ) -> dict[str, Any]:
        if not local_file.exists():
            raise FileNotFoundError(f"File not found: {local_file}")
        if not local_file.is_file():
            raise ValueError(f"Not a regular file: {local_file}")

        option = self._request_option()
        resolved_file_name = file_name or local_file.name
        file_size = local_file.stat().st_size
        resolved_checksum = checksum or self._file_adler32(local_file)

        with open(local_file, "rb") as file:
            request_body_builder = (
                UploadAllMediaRequestBody.builder()
                .file_name(resolved_file_name)
                .parent_type(parent_type)
                .parent_node(parent_node)
                .size(str(file_size))
                .checksum(resolved_checksum)
            )
            if extra:
                request_body_builder = request_body_builder.extra(extra)

            request = (
                UploadAllMediaRequest.builder()
                .request_body(request_body_builder.file(file).build())
                .build()
            )

            response = self._call_with_retry(
                "client.drive.v1.media.upload_all",
                lambda: self._parent.client.drive.v1.media.upload_all(request, option),
            )

        return self._marshal_data(response.data)

    def subscribe_file(
        self,
        file_token: str,
        file_type: str,
        event_type: str,
    ) -> dict[str, Any]:
        option = self._request_option()
        request = (
            SubscribeFileRequest.builder()
            .file_token(file_token)
            .file_type(file_type)
            .event_type(event_type)
            .build()
        )

        self._call_with_retry(
            "client.drive.v1.file.subscribe",
            lambda: self._parent.client.drive.v1.file.subscribe(request, option),
        )
        return {"success": True}

    def delete_subscribe_file(
        self,
        file_token: str,
        file_type: str,
        event_type: str,
    ) -> dict[str, Any]:
        option = self._request_option()
        request = (
            DeleteSubscribeFileRequest.builder()
            .file_token(file_token)
            .file_type(file_type)
            .event_type(event_type)
            .build()
        )

        self._call_with_retry(
            "client.drive.v1.file.delete_subscribe",
            lambda: self._parent.client.drive.v1.file.delete_subscribe(request, option),
        )
        return {"success": True}

    def get_subscribe_file(
        self,
        file_token: str,
        file_type: str,
        event_type: str,
    ) -> dict[str, Any]:
        option = self._request_option()
        request = (
            GetSubscribeFileRequest.builder()
            .file_token(file_token)
            .file_type(file_type)
            .event_type(event_type)
            .build()
        )

        response = self._call_with_retry(
            "client.drive.v1.file.get_subscribe",
            lambda: self._parent.client.drive.v1.file.get_subscribe(request, option),
        )
        return self._marshal_data(response.data)
