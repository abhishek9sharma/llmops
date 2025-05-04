from guardrails import OnFailAction
from guardrails.hub import BanList, ProfanityFree

guard_map = {
    "Profanity": ProfanityFree(on_fail=OnFailAction.EXCEPTION),
    "BanList": BanList(
        banned_words=["codename", "athena"], on_fail=OnFailAction.EXCEPTION
    ),
}
