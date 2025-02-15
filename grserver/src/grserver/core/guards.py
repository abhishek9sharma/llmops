from guardrails.hub import BanList, LlamaGuard7B, ToxicLanguage,ProfanityFree

guard_map = {
    "Profanity": ProfanityFree,
    "LlamaGuard7B": LlamaGuard7B(policies=[LlamaGuard7B.POLICY__NO_ILLEGAL_DRUGS]),
    "BanList": BanList(banned_words=["codename", "athena"]),
    "ToxicLanguage": ToxicLanguage,
}

