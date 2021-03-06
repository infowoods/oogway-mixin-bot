import logging

from mixinsdk.types.message import pack_message, pack_text_data

from . import querier
from .methods import parse_process
from .types import CommandContext, CommandError


def handle(ctx: CommandContext, command: str):
    processes = command.split("|")

    try:
        for prc in processes:
            prog_name, args = parse_process(prc)
            ctx.cur_prog_name = prog_name
            program = select_program(prog_name)
            ctx.pipe_data = program(ctx, args)  # execute program to process
    except CommandError as e:
        text = f"✗ Command error: {e.prog_name} : {e.message}"
        msg = pack_message(pack_text_data(text), ctx.msgview.conversation_id)
        ctx.replying_msgs.append(msg)
    except Exception:
        logging.error(f"✗ Command exception of {ctx.cur_prog_name}", exc_info=True)
        text = f"✗ Command error: {ctx.cur_prog_name} : An exception occurred"
        msg = pack_message(pack_text_data(text), ctx.msgview.conversation_id)
        ctx.replying_msgs.append(msg)


def select_program(prog_name: str):
    prog_name = prog_name.lower()
    # oogway
    if prog_name in ["hi", "hello", "你好"]:
        return querier.oogway.hi
    if prog_name in ["source", "源码"]:
        return querier.oogway.get_source_code
    if prog_name in ["help", "帮助"]:
        return querier.oogway.help
    if prog_name in ["user"]:
        return querier.oogway.current_user_info
    if prog_name in ["conv"]:
        return querier.oogway.current_conversation_info
    if prog_name in ["oogway", "master"]:
        return querier.oogway.master_pearls
    if prog_name in ["translate", "tr", "翻译", "翻"]:
        return querier.translate.handle

    # mixin
    if prog_name in ["asset"]:
        return querier.mixin.asset

    if prog_name in ["wiki", "wikipedia"]:
        return querier.wiki.handle

    if prog_name in ["size"]:
        return querier.size.handle

    # else
    return querier.oogway.command_not_found
