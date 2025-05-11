from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from InnoTester.Core.InnoTesterBot import *
from InnoTester.Utils.Keyboards import *


@dp.callback_query(F.data == CHOOSE_ASSIGNMENT_CB)
async def onOpenAssignmentsList(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    assignments = assignmentsManager.cached
    chosenAssignment = data.get("assignment")

    data["assignment"] = None
    await state.set_data(data)

    await query.message.edit_text(
        text="Here are all the assignments:",
        reply_markup=assigListKeyboard(assignments, chosenAssignment)
    )


@dp.callback_query(F.data.startswith(ASSIGNMENT_CB_PREFIX))
async def onChooseAssignment(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    id = query.data.split("_")[1]
    assignment = await assignmentsManager.getAssignment(id)

    if not assignment.is_configured():
        await query.answer(
            "This assignment is not yet configured :(\n"
            "If you have a reference solution or a test generator\n"
            "contact us, be a hero!",
            show_alert=True
        ); return

    data["assignment"] = assignment
    await state.set_data(data)

    await query.message.edit_text(
        text=(
            "Chosen Assignment:\n"
            f"{str(assignment)}\n"
            "Now you can send your code"
        ),
        reply_markup=CHANGE_ASSIGNMENT_KB
    )
