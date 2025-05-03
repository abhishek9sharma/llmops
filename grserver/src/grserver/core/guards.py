from guardrails import OnFailAction
from guardrails.hub import BanList, ProfanityFree

# LlamaGuard7B, ProfanityFree, ToxicLanguage

guard_map = {
    "Profanity": ProfanityFree(on_fail=OnFailAction.EXCEPTION),
    # "LlamaGuard7B": LlamaGuard7B(policies=[LlamaGuard7B.POLICY__NO_ILLEGAL_DRUGS]),
    "BanList": BanList(
        banned_words=["codename", "athena"], on_fail=OnFailAction.EXCEPTION
    ),
    # "ToxicLanguage": ToxicLanguage,
}
