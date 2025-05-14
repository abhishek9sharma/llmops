from fastapp import ServeModelFastAPI
from ray import serve
from ray.serve import ingress
# from fastapi import Request
from starlette.requests import Request

# Initialize the model server
grounded_ai_hal_judge = ServeModelFastAPI(
    model_path="/mnt/g/PersonalProjects/hfmodels/phi3.5-hallucination-judge",
    model_type="peft",
    task_type="text-generation",
    quantized=True,
    peft_adapter_path="/mnt/g/PersonalProjects/hfmodels/Phi-3.5-mini-instruct",
)


@serve.deployment
@ingress(grounded_ai_hal_judge.app)
class GroundedAIHalJudgeRayServe:
    pass


grounded_ai_hal_judge_ray_serve = GroundedAIHalJudgeRayServe.bind()
