from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from InnoTester.Core.Assignments.Models import Assignment


IKB = InlineKeyboardButton


#region constant

CHOOSE_ASSIGNMENT_CB = "choose_assignment"
CHOOSE_ASSIGNMENT_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [IKB(text="Choose Assignment", callback_data=CHOOSE_ASSIGNMENT_CB)]
    ]
)
CHANGE_ASSIGNMENT_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [IKB(text="Change Assignment", callback_data=CHOOSE_ASSIGNMENT_CB)]
    ]
)


CHOOSE_ASSIGNMENT_SHARE_CB = "choose_assignment_share"
CHOOSE_ASSIGNMENT_SHARE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [IKB(text="Choose Assignment", callback_data=CHOOSE_ASSIGNMENT_SHARE_CB)]
    ]
)
SHARE_REFERENCE_CB = "share_reference"
SHARE_TESTGEN_CB = "share_testgen"
SHARE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            IKB(text="Reference", callback_data=SHARE_REFERENCE_CB),
            IKB(text="TestGen", callback_data=SHARE_TESTGEN_CB)
        ],
        [IKB(text="Change Assignment", callback_data=CHOOSE_ASSIGNMENT_SHARE_CB)]
    ]
)

SHARE_CANCEL_CB = "share_cancel"
SHARE_CANCEL_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [IKB(text="Cancel", callback_data=SHARE_CANCEL_CB)]
    ]
)

ASSIGNMENT_CB_PREFIX = "assignment_"
STOP_CB_PREFIX = "stop_"

#endregion


#region builders

# TODO: make paginated list for more assignments
def assigListKeyboard(
        assignments: list[Assignment],
        chosen: Assignment = None
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for a in assignments:
        builder.button(text=str(a), callback_data=f"{ASSIGNMENT_CB_PREFIX}{a.id}")
    builder.adjust(1, repeat=True)
    return builder.as_markup()


def stopTestKeyboard(username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [IKB(text="Stop Testing", callback_data=f"{STOP_CB_PREFIX}{username}")]
        ]
    )

#endregion
