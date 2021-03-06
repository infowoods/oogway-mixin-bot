import logging

import basic_reply
import commander
from mixinsdk.types.message import (MessageView, pack_message, pack_post_data,
                                    pack_text_data)
from thisbot.constants import APP_NAME
from thisbot.init import mixin_bot_config, mixin_client, operation
from thisbot.types import MessageUser


def send_text_to_user(text, conversation_id, quote_message_id=None):
    mixin_client.blaze.send_message(
        pack_message(
            pack_text_data(text), conversation_id, quote_message_id=quote_message_id
        )
    )


def send_post_to_user(text, conversation_id, quote_message_id=None):
    mixin_client.blaze.send_message(
        pack_message(
            pack_post_data(text), conversation_id, quote_message_id=quote_message_id
        )
    )


def notice_operator(text):
    logging.warn(f"notice operator: {text}")
    text = f"{APP_NAME}:\n```" + text + "\n```"
    mixin_client.blaze.send_message(pack_post_data(text), operation.notice_conv_id)


def handle_text(msguser: MessageUser, msgview: MessageView):
    # limit size
    if len(msgview.data_decoded) > 8192:
        send_text_to_user("✗ Command too long", msgview.conversation_id)
        return

    msg_text = msgview.data_decoded

    # clean text command
    cmd = msg_text.strip()
    cmd = cmd.lstrip("/")
    sign_str = "@" + mixin_bot_config.mixin_id + " "
    cmd = cmd.replace(sign_str, "")

    logging.info(f"user command: {cmd}")

    ctx = commander.CommandContext(msguser, msgview)
    commander.handle(ctx, cmd)

    for msg in ctx.replying_msgs:
        mixin_client.blaze.send_message(msg)


def handle_media(msguser: MessageUser, msgview: MessageView):
    text = f"{msgview.category}\n\n```\n{msgview.data_decoded}\n```"
    send_post_to_user(text, msgview.conversation_id)


def handle_conversation_actions(msgview: MessageView):
    # print(msgview.data_decoded)
    participant_id = msgview.data_decoded.get("participant_id")
    if participant_id != mixin_client.blaze.config.client_id:
        return
    # 是对本机器人账号的操作才关心和处理
    action = msgview.data_decoded.get("action")
    if action == "ADD":
        logging.info(f"被加入了群聊会话: {msgview.conversation_id}")

        text = basic_reply.get_welcome()
        send_text_to_user(text, msgview.conversation_id)

        return
    elif action == "REMOVE":
        logging.info(f"被加入了群聊会话: {msgview.conversation_id}")
        # log to db?
        return
    else:
        logging.warn(f"未知的会话操作: {action}")
        return
