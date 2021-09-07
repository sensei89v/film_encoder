import enum


class VideoFileStatus(enum.Enum):
    new = enum.auto()
    in_loading = enum.auto()
    loaded = enum.auto()
    in_encoding = enum.auto()
    success = enum.auto()
    failed = enum.auto()

