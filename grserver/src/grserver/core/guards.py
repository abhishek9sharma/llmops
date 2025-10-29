from guardrails import OnFailAction
from guardrails.hub import GuardrailsPII, ToxicLanguage

guard_map = {
    "Toxic": ToxicLanguage(validation_method="sentence", threshold=0.5),
    "PII": GuardrailsPII(entities=["PERSON"], on_fail=OnFailAction.FIX),
}
