from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum


@dataclass(frozen=True)
class LabelLog:
    log_hash: str
    user_hash: str
    annotation_hash: str
    data_hash: str
    feature_hash: str
    action: Action
    label_name: str
    time_taken: int
    created_at: datetime.datetime
    frame: int


class Action(IntEnum):
    ADD = 0
    EDIT = 1
    DELETE = 2
    START = 3
    END = 4
    MARK_AS_NOT_LABELLED = 5
    MARK_AS_IN_PROGRESS = 6
    MARK_AS_LABELLED = 7
    MARK_AS_REVIEW_REQUIRED = 8
    MARK_AS_REVIEWED = 9
    MARK_AS_REVIEWED_TWICE = 10
    SUBMIT_TASK = 11
    APPROVE_LABEL = 12
    REJECT_LABEL = 13
    CLICK_SAVE = 14
    CLICK_UNDO = 15
    CLICK_REDO = 16
    CLICK_BULK = 17
    CLICK_ZOOM = 19
    CLICK_BRIGHTNESS = 20
    CLICK_HOTKEYS = 21
    CLICK_SETTINGS = 22
