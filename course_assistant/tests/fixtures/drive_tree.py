"""A captured snapshot of the real course Drive, for offline tests.

Folder/file IDs and titles are the genuine ones discovered during Phase 2, so
the fake exercises realistic data. A few edge cases are included deliberately:

- Recordings: Lesson 1 (single part), Lesson 3 (multi-part, out of order +
  unlabeled — synthetic contents under the real folder), Lesson 7 & 11 (empty
  folders → "not uploaded yet").
- Materials: Lesson 2 (flat files), Lesson 7 (single exercise doc), Lesson 10
  (nested HW/ and code/ subfolders), Lesson 14 (single homework doc).
- No folder at all for, e.g., Lesson 99 (→ not found).
"""

from __future__ import annotations

from course_assistant.drive.service import FOLDER_MIME, RawEntry

ROOT_ID = "1GfQBI1btQSoyMLQ7z-_aE4xBnObsO2wO"

_RECORDINGS_ROOT = "1bVrDPbVxsiSTyguWYFEVjovgYbDh9469"
_MATERIALS_ROOT = "1JpwQBI8wi3J5OigcMbAG8YRKLLzXIf48"

# recordings lesson folders
_REC_L1 = "14J5qQTx5pz_aMtiKDcz3ohgElp9A8tHd"
_REC_L3 = "1962um0GLot2fnzVjnNEqjE1GuDjCIOVJ"
_REC_L7 = "1HQv3mIQPqBXVgGWQN3XD2Yf3Tl26Dqy8"
_REC_L11 = "1WhDkf-5lMlgJyF5Di4hz7prXy6FlzRUv"

# materials lesson folders
_MAT_L2 = "12f7hoIT754XmfFVajjLSnxCkIGVf5VZf"
_MAT_L7 = "1zszwWIxb_fBWN5TOSbBxJXqLIO1IA8Iz"
_MAT_L10 = "1Dw1Vlvtt3G6FXuk52ostgZq9armZ_Ntt"
_MAT_L10_HW = "1FsXVGiHGYTk6O_XpepW3gToQRN29p9Ix"
_MAT_L10_CODE = "1rYt_cY82m3Py3Hg-BmO8gzkfz8ovouza"
_MAT_L14 = "1YJ_WJEBaQUjda0MKN6VV0fyzY0KU6fvH"


def _folder(file_id: str, title: str) -> RawEntry:
    return RawEntry(id=file_id, title=title, mime_type=FOLDER_MIME, url=f"folders/{file_id}")


def _file(file_id: str, title: str, mime: str) -> RawEntry:
    return RawEntry(id=file_id, title=title, mime_type=mime, url=f"file/{file_id}/view")


_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
_PDF = "application/pdf"
_MP4 = "video/mp4"
_PY = "text/x-python"


def build_tree() -> tuple[str, dict[str, list[RawEntry]]]:
    """Return ``(root_id, tree)`` for :class:`FakeDriveService`."""
    tree: dict[str, list[RawEntry]] = {
        ROOT_ID: [
            _file("1LvHCMRXOfPqHvPC5Fk9LA8GWY9V195Fz", "Homework Submission Procedure.docx", _DOCX),
            _folder(_RECORDINGS_ROOT, "הקלטות "),
            _folder(_MATERIALS_ROOT, "מצגות "),
        ],
        # --- recordings type-folder ---
        _RECORDINGS_ROOT: [
            _folder(_REC_L1, "Lesson 1"),
            _folder(_REC_L3, "Lesson 3"),
            _folder(_REC_L7, "Lesson 7"),
            _folder(_REC_L11, "Lesson 11"),
        ],
        _REC_L1: [
            _file("1szPuDb5DzwYg7jPcud49XjRWU3zEOGix", "part 1.mp4", _MP4),
        ],
        # multi-part, intentionally out of order + one unlabeled (synthetic contents)
        _REC_L3: [
            _file("rec_l3_p2", "part 2.mp4", _MP4),
            _file("rec_l3_intro", "intro.mp4", _MP4),
            _file("rec_l3_p1", "part 1.mp4", _MP4),
        ],
        _REC_L7: [],  # folder exists, empty → not uploaded yet
        _REC_L11: [],
        # --- materials type-folder ---
        _MATERIALS_ROOT: [
            _folder(_MAT_L2, "Lesson 2"),
            _folder(_MAT_L7, "Lesson 7"),
            _folder(_MAT_L10, "Lesson 10"),
            _folder(_MAT_L14, "Lesson 14"),
        ],
        # flat lesson: homework docs + a slide deck
        _MAT_L2: [
            _file("1wjI7Dy5UuWI2mMUkwlY9PylMZmZXG3PB", "Jupyter-intro-hw.docx", _DOCX),
            _file("1WQpSpwjZlkw3J_-HHdBYSJqN1PhUP5QZ", "HW2 (2).docx", _DOCX),
            _file("1qah246nFVAVYlbSVHnLwFViJ738XtJMj", "Python-intro-hw.docx", _DOCX),
            _file("1XEx-QFFJnHCcfjpAi6YNufSkzcAHjjz9", "lecture2.pptx (1).pdf", _PDF),
        ],
        # single exercise doc (classified as homework)
        _MAT_L7: [
            _file(
                "1BM61VfZsr5Fr0CPo7_OMKC4BmiJ7rpMV",
                "Ubuntu_EC2_Docker_Nginx_Student_Exercise.docx",
                _DOCX,
            ),
        ],
        # nested HW/ and code/ subfolders
        _MAT_L10: [
            _folder(_MAT_L10_HW, "HW"),
            _folder(_MAT_L10_CODE, "code"),
        ],
        _MAT_L10_HW: [
            _file("1Yn2wAKmT4SpTyXAn5hrZ006uvluDfQ9Z", "פרויקט אמצע.docx", _DOCX),
        ],
        _MAT_L10_CODE: [
            _file("1qFl0WRx1QYwyaLFRGzxvcEMZBeCA0d3e", "bedroc_agent.py", _PY),
        ],
        _MAT_L14: [
            _file("1v6pvkGjuxRmGmVoPEk0iCh5v9P7uYWEd", "n8n_hw.docx", _DOCX),
        ],
    }
    return ROOT_ID, tree
