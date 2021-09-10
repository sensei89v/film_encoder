import enum


class VideoFileStatus(enum.Enum):
    new = enum.auto()
    in_loading = enum.auto()
    in_process = enum.auto()
    success = enum.auto()
    failed = enum.auto()

