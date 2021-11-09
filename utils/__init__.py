from nonebot.adapters import cqhttp
from nonebot.adapters import Bot, Event
from nonebot.rule import Rule
from nonebot.typing import T_State


def is_group_message() -> Rule:

    async def _is(bot: "Bot", event: "Event", state: T_State) -> bool:
        if event.get_type() != "message":
            return False
        return hasattr(event, 'group_id')

    return Rule(_is)


def is_poke_message() -> Rule:

    async def _is(bot: "Bot", event: "Event", state: T_State) -> bool:
        return event.get_event_name() == "notice.notify.poke"

    return Rule(_is)
