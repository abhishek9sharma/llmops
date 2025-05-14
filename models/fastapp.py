from typing import Any, Dict, List, Optional

import ray
from base import ModelLoader
from fastapi import FastAPI
from pydantic import BaseModel


class PredictRequest(BaseModel):
    text: str
    max_length: int = 128
    top_k: int = 1


class ServeModelFastAPI:
    def __init__(self, **loader_kwargs):
        self.app = FastAPI()
        self.model_loader = ModelLoader(**loader_kwargs)
        self.model_loader.load_model()
        print(f"Loaded Model: {self.model_loader}")

        @self.app.get("/status")
        def index():
            return {"status": "running", "model": self.model_loader.get_metadata()}

        @self.app.post("/predict")
        async def predict(request: PredictRequest) -> Dict[str, Any]:
            prediction = self.model_loader.predict_input(**request.dict())
            return {"prediction": prediction}


# # Initialize the model server
# model_server = ServeModelFastAPI(
#     model_path="/mnt/g/PersonalProjects/hfmodels/phi3.5-hallucination-judge",
#     model_type="peft",
#     task_type="text-generation",
#     quantized=True,
#     peft_adapter_path="/mnt/g/PersonalProjects/hfmodels/Phi-3.5-mini-instruct"
# )

# # Run the FastAPI app
# if __name__ == "__main__":

#     import uvicorn

#     uvicorn.run(model_server.app, host="0.0.0.0", port=8001)
