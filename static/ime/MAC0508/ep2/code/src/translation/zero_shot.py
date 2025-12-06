"""Zero-shot translation."""

import torch
from tqdm import tqdm
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from ..config import DEVICE, PT_LANG_CODE, TA_LANG_CODE


PREFIXES = {
    "pt_to_ta": "translate Portuguese to Tupi: ",
    "ta_to_pt": "translate Tupi to Portuguese: ",
}


class ZeroShotTranslator:
    """Zero-shot translator supporting NLLB (language codes)"""
    
    def __init__(self, model_name: str, device: str = DEVICE):
        self.model_name = model_name
        self.device = device
        self.is_nllb = "nllb" in model_name.lower()
        
        print(f"Carregando modelo: {model_name}")
        print(f"Dispositivo: {device}")
        print(f"Modo: {'NLLB (language codes)' if self.is_nllb else 'mT5 (prompts)'}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.model.to(device)
        self.model.eval()
        
        print("Modelo carregado!")
    
    def translate(self, text: str, direction: str = "pt_to_ta", max_length: int = 128, num_beams: int = 5) -> str:
        if self.is_nllb:
            return self._translate_nllb(text, direction, max_length, num_beams)
        else:
            return self._translate_mt5(text, direction, max_length, num_beams)
    
    def _translate_nllb(self, text: str, direction: str, max_length: int, num_beams: int) -> str:
        src_lang = PT_LANG_CODE if direction == "pt_to_ta" else TA_LANG_CODE
        tgt_lang = TA_LANG_CODE if direction == "pt_to_ta" else PT_LANG_CODE
        
        self.tokenizer.src_lang = src_lang
        inputs = self.tokenizer(text, return_tensors="pt", max_length=max_length, truncation=True).to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(tgt_lang),
                max_length=max_length,
                num_beams=num_beams,
            )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    def _translate_mt5(self, text: str, direction: str, max_length: int, num_beams: int) -> str:
        input_text = PREFIXES[direction] + text
        inputs = self.tokenizer(input_text, return_tensors="pt", max_length=max_length, truncation=True).to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_length=max_length, num_beams=num_beams)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    def translate_batch(self, texts: list[str], direction: str = "pt_to_ta", max_length: int = 128, num_beams: int = 5) -> list[str]:
        return [self.translate(text, direction, max_length, num_beams) for text in tqdm(texts, desc=f"Traduzindo ({direction})")]
