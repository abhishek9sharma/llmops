import os

import onnxruntime
import torch
from peft import PeftModel
from sentence_transformers import SentenceTransformer
from transformers import (AutoModel, AutoModelForCausalLM,
                          AutoModelForSequenceClassification,
                          AutoModelForTokenClassification, AutoTokenizer,
                          BitsAndBytesConfig)


class ModelLoader:
    def __init__(
        self,
        model_path: str,
        model_type: str,
        task_type: str = None,
        peft_adapter_path: str = None,
        quantized: bool = False,
    ):
        """
        model_path: HF model ID or local path
        model_type: ['hf', 'onnx', 'peft', 'sentence_transformer']
        task_type: e.g. 'text-classification', 'text-generation' (for HF/PEFT)
        peft_adapter_path: optional PEFT adapter path
        quantized: if True, load PyTorch models in 8-bit using bitsandbytes
        """
        self.model_path = model_path
        self.model_name = os.path.basename(model_path)
        self.model_type = model_type.lower()
        self.task_type = task_type.lower() if task_type else None
        self.peft_adapter_path = peft_adapter_path
        self.quantized = quantized
        self.model = None
        self.tokenizer = None

    def load_model(self):
        if self.model_type == "hf":
            self.model, self.tokenizer = self._load_hf_model()
        elif self.model_type == "onnx":
            self.model = self._load_onnx_model()
        elif self.model_type == "peft":
            self.model, self.tokenizer = self._load_peft_model()
        elif self.model_type == "sentence_transformer":
            self.model = self._load_sentence_transformer()
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
        return self.model

    def _load_hf_model(self):
        print(
            f"Loading HF model '{self.model_path}' (quantized={self.quantized}) for task '{self.task_type}'..."
        )
        tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        # Ensure the tokenizer has a pad_token
        if tokenizer.pad_token is None:
            if tokenizer.eos_token is not None:
                tokenizer.pad_token = tokenizer.eos_token
            else:
                tokenizer.add_special_tokens({"pad_token": "[PAD]"})
        model_cls = self._get_model_class_for_task()

        if self.quantized:
            quant_config = BitsAndBytesConfig(load_in_8bit=True)
            model = model_cls.from_pretrained(
                self.model_path, quantization_config=quant_config, device_map="auto"
            )
        else:
            model = model_cls.from_pretrained(self.model_path)

        return model, tokenizer

    def _load_peft_model(self):
        if not self.peft_adapter_path:
            raise ValueError("PEFT adapter path must be provided.")

        print(
            f"Loading PEFT model base '{self.model_path}' with adapter '{self.peft_adapter_path}' (quantized={self.quantized})..."
        )
        tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        # Ensure the tokenizer has a pad_token
        if tokenizer.pad_token is None:
            if tokenizer.eos_token is not None:
                tokenizer.pad_token = tokenizer.eos_token
            else:
                tokenizer.add_special_tokens({"pad_token": "[PAD]"})
        model_cls = self._get_model_class_for_task()

        if self.quantized:
            quant_config = BitsAndBytesConfig(load_in_8bit=True)
            base_model = model_cls.from_pretrained(
                self.model_path, quantization_config=quant_config, device_map="auto"
            )
        else:
            base_model = model_cls.from_pretrained(self.model_path)

        try:
            peft_model = PeftModel.from_pretrained(base_model, self.peft_adapter_path)
            peft_model = peft_model.merge_and_unload()
        except Exception as e:
            print(
                f"Warning: Failed to merge and unload PEFT model. Using base model. Error: {e}"
            )
            peft_model = base_model

        return peft_model, tokenizer

    def _load_onnx_model(self):
        print(f"Loading ONNX model from '{self.model_path}'...")
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"ONNX model path not found: {self.model_path}")
        session = onnxruntime.InferenceSession(self.model_path)
        return session

    def _load_sentence_transformer(self):
        print(
            f"Loading SentenceTransformer (quantized={self.quantized}) from '{self.model_path}'..."
        )
        if self.quantized:
            print(
                "Note: SentenceTransformer quantization not supported in this loader."
            )
        return SentenceTransformer(self.model_path)

    def _get_model_class_for_task(self):
        task_map = {
            "text-classification": AutoModelForSequenceClassification,
            "text-generation": AutoModelForCausalLM,
            "token-classification": AutoModelForTokenClassification,
        }
        if self.task_type not in task_map:
            raise ValueError(f"Unsupported task type: {self.task_type}")
        return task_map[self.task_type]

    def get_tokenizer(self):
        return self.tokenizer

    def predict_input(self, text: str, max_length: int = 128, top_k: int = 1):
        if self.model_type == "sentence_transformer":
            return self.model.encode(text)

        elif self.model_type in ["hf", "peft"]:
            if not self.tokenizer:
                raise ValueError("Tokenizer not loaded.")

            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=max_length,
            ).to(self.model.device)

            outputs = self.model(**inputs)

            if self.task_type == "text-classification":
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
                top_probs, top_labels = torch.topk(probs, top_k)
                return [
                    {"label": int(label), "score": float(score)}
                    for label, score in zip(top_labels[0], top_probs[0])
                ]

            elif self.task_type == "text-generation":
                outputs = self.model.generate(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs.get("attention_mask", None),
                    max_length=max_length,
                )
                return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            elif self.task_type == "token-classification":
                tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
                predictions = torch.argmax(outputs.logits, dim=2)[0]
                return [
                    {"token": token, "label_id": int(label)}
                    for token, label in zip(tokens, predictions)
                ]

            return outputs  # fallback

        elif self.model_type == "onnx":
            inputs = self.tokenizer(
                text, return_tensors="np", padding=True, truncation=True
            )
            input_feed = {k: v for k, v in inputs.items()}
            output_names = [o.name for o in self.model.get_outputs()]
            outputs = self.model.run(output_names, input_feed)
            return outputs

        else:
            raise ValueError("Unsupported model type for prediction.")

    def get_metadata(self):
        return {
            "model_path": self.model_path,
            "model_type": self.model_type,
            "task_type": self.task_type,
            "quantized": getattr(self, "quantized", False),
        }
