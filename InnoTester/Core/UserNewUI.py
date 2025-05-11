import asyncio
from aiogram import F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from InnoTester.Core.InnoTesterBot import *
from InnoTester.Utils.Keyboards import *


@dp.message(CommandStart())
async def onCmdStart(message: Message, state: FSMContext):
    data = await state.get_data()
    
    last_message: Message = data.get("last_message")
    if last_message: await last_message.delete()

    last_message = await message.answer(
        "Welcome to InnoTester, blah blah",
        reply_markup=CHOOSE_ASSIGNMENT_KB
    )

    data["last_message"] = last_message
    await state.set_data(data)


@dp.callback_query(F.data == CHOOSE_ASSIGNMENT_CB)
async def onOpenAssignmentsList(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data["last_message"] = query.message

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
    data["last_message"] = query.message

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


@dp.message(F.document)
async def onDocument(message: Message, state: FSMContext):
    data = await state.get_data()

    assignment = data.get("assignment")
    last_message: Message = data.get("last_message")


    if not message.from_user.username:
        await message.answer(
            "To use the bot you need to have a @username\n"
            "Set one in the Telegram settings to proceed"
        ); return


    if last_message: # That's important, to delete the message before document sent
        await last_message.delete()    


    if not assignment:
        last_message = await message.answer(
            text="You need first to choose the assignment",
            reply_markup=CHOOSE_ASSIGNMENT_KB
        )
        data["last_message"] = last_message
        await state.set_data(data)
        return

    last_message = await message.answer(
        text=(
            "Testing started\n"
            f"Assignment: {assignment}"
        ),
        reply_markup=stopTestKeyboard(message.from_user.username)
    )

    data["last_message"] = last_message
    await state.set_data(data)

    # SOME TESTING CODE HERE # 
    await asyncio.sleep(5)
    # SOME TESTING CODE HERE # 

    await last_message.edit_text(
        text=(
            "Testing finished\n"
            "Feedback: perfect code, all good\n"
        ),
        reply_markup=CHANGE_ASSIGNMENT_KB
    )


@dp.callback_query(F.data.startswith(STOP_CB_PREFIX))
async def onStopTesting(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    assignment = data.get("assignment")

    if not assignment:
        await query.message.edit_text(
            text="You need first to choose the assignment",
            reply_markup=CHOOSE_ASSIGNMENT_KB
        ); return

    await query.message.edit_text(
        text=(
            "Testing stopped\n"
            f"Assignment: {assignment}\n"
            "Now you can send your code"
        ),
        reply_markup=CHANGE_ASSIGNMENT_KB
    )
