# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# model_id = "google/t5-efficient-mini"
# tokenizer = AutoTokenizer.from_pretrained(model_id)
# model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
# summarizer = pipeline("summarization", model=model, tokenizer=tokenizer, device=-1)

def summarizer(input: str) -> str:
    return "summary of following:" + input
