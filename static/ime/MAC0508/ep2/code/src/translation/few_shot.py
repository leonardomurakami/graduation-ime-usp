"""Few-shot translation with fine-tuning."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import torch
from torch.utils.data import Dataset
from tqdm import tqdm
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    EarlyStoppingCallback,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)

from ..config import DEVICE, MODELS_DIR, PT_LANG_CODE, TA_LANG_CODE


@dataclass
class TrainingConfig:
    batch_size: int = 8
    learning_rate: float = 4e-5
    num_epochs: int = 30
    warmup_steps: int = 100
    weight_decay: float = 0.01
    max_source_length: int = 128
    max_target_length: int = 128
    early_stopping_patience: int = 5
    early_stopping_threshold: float = 0.01
    eval_steps: int = 50
    save_steps: int = 100
    logging_steps: int = 10
    gradient_accumulation_steps: int = 8
    fp16: bool = torch.cuda.is_available()


PREFIXES = {
    "pt_to_ta": "translate Portuguese to Tupi: ",
    "ta_to_pt": "translate Tupi to Portuguese: ",
}


class NLLBDataset(Dataset):
    def __init__(self, source_texts, target_texts, tokenizer, src_lang, tgt_lang, max_length=128):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang
        
        # Pre-tokenize everything
        self.examples = []
        for src, tgt in zip(source_texts, target_texts):
            tokenizer.src_lang = src_lang
            src_enc = tokenizer(src, max_length=max_length, truncation=True)
            
            tokenizer.src_lang = tgt_lang  
            tgt_enc = tokenizer(tgt, max_length=max_length, truncation=True)
            
            self.examples.append({
                "input_ids": src_enc["input_ids"],
                "attention_mask": src_enc["attention_mask"],
                "labels": tgt_enc["input_ids"],
            })
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        return self.examples[idx]


class FewShotTrainer:
    def __init__(self, model_name: str, config: TrainingConfig = None):
        self.model_name = model_name
        self.config = config or TrainingConfig()
        self.is_nllb = "nllb" in model_name.lower()
        
        print(f"Inicializando FewShotTrainer")
        print(f"  Modelo: {model_name}")
        print(f"  Tipo: NLLB")
        print(f"  Dispositivo: {DEVICE}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    def _create_datasets(self, train_df, val_df, direction):
        src_col = "portugues" if direction == "pt_to_ta" else "tupi_antigo"
        tgt_col = "tupi_antigo" if direction == "pt_to_ta" else "portugues"
        
        print(f"  Criando datasets para {direction}...")
        
        if self.is_nllb:
            src_lang = PT_LANG_CODE if direction == "pt_to_ta" else TA_LANG_CODE
            tgt_lang = TA_LANG_CODE if direction == "pt_to_ta" else PT_LANG_CODE
            train_ds = NLLBDataset(train_df[src_col].tolist(), train_df[tgt_col].tolist(), self.tokenizer, src_lang, tgt_lang, self.config.max_source_length)
            val_ds = NLLBDataset(val_df[src_col].tolist(), val_df[tgt_col].tolist(), self.tokenizer, src_lang, tgt_lang, self.config.max_source_length)
        
        print(f"  Train: {len(train_ds)}, Val: {len(val_ds)}")
        return train_ds, val_ds
    
    def train(self, train_df: pd.DataFrame, val_df: pd.DataFrame, direction: str = "pt_to_ta", output_dir: Path = None) -> str:
        if output_dir is None:
            output_dir = MODELS_DIR / f"{self.model_name.replace('/', '_')}_{direction}"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{'='*60}")
        print(f"Treinando: {direction}")
        print(f"{'='*60}")
        
        model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        train_ds, val_ds = self._create_datasets(train_df, val_df, direction)
        
        # Debug: check first example
        ex = train_ds[0]
        print(f"  Sample input_ids length: {len(ex['input_ids'])}")
        print(f"  Sample labels length: {len(ex['labels'])}")
        
        data_collator = DataCollatorForSeq2Seq(
            tokenizer=self.tokenizer,
            model=model,
            padding=True,
            label_pad_token_id=-100,
        )
        
        training_args = Seq2SeqTrainingArguments(
            output_dir=str(output_dir),
            num_train_epochs=self.config.num_epochs,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            save_total_limit=2,
            fp16=self.config.fp16,
            per_device_train_batch_size=self.config.batch_size,
            per_device_eval_batch_size=self.config.batch_size,
            learning_rate=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
            warmup_steps=self.config.warmup_steps,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            eval_strategy="steps",
            eval_steps=self.config.eval_steps,
            save_strategy="steps",
            save_steps=self.config.save_steps,
            logging_steps=self.config.logging_steps,
            predict_with_generate=True,
            generation_max_length=self.config.max_target_length,
            report_to="none",
        )
        
        trainer = Seq2SeqTrainer(
            model=model,
            args=training_args,
            train_dataset=train_ds,
            eval_dataset=val_ds,
            data_collator=data_collator,
            processing_class=self.tokenizer,
            callbacks=[EarlyStoppingCallback(
                early_stopping_patience=self.config.early_stopping_patience,
                early_stopping_threshold=self.config.early_stopping_threshold,
            )],
        )
        
        trainer.train()
        
        final_path = output_dir / "final"
        trainer.save_model(str(final_path))
        self.tokenizer.save_pretrained(str(final_path))
        print(f"Modelo salvo em: {final_path}")
        return str(final_path)
    
    def translate(self, model_path: str, texts: list[str], direction: str = "pt_to_ta", max_length: int = 128, num_beams: int = 5) -> list[str]:
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model.to(DEVICE)
        model.eval()
        
        translations = []
        for text in tqdm(texts, desc="Traduzindo"):
            if self.is_nllb:
                src_lang = PT_LANG_CODE if direction == "pt_to_ta" else TA_LANG_CODE
                tgt_lang = TA_LANG_CODE if direction == "pt_to_ta" else PT_LANG_CODE
                tokenizer.src_lang = src_lang
                inputs = tokenizer(text, return_tensors="pt", max_length=max_length, truncation=True).to(DEVICE)
                with torch.no_grad():
                    outputs = model.generate(**inputs, forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt_lang), max_length=max_length, num_beams=num_beams)
            else:
                input_text = PREFIXES[direction] + text
                inputs = tokenizer(input_text, return_tensors="pt", max_length=max_length, truncation=True).to(DEVICE)
                with torch.no_grad():
                    outputs = model.generate(**inputs, max_length=max_length, num_beams=num_beams)
            
            translations.append(tokenizer.decode(outputs[0], skip_special_tokens=True))
        
        return translations
