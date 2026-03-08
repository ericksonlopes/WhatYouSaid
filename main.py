import logging

from src.infrastructure.services.model_loader_service import ModelLoaderService
from src.infrastructure.services.transcript_processor_service import TranscriptProcessorService

logging.getLogger("transformers").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

if __name__ == '__main__':
    model = "paraphrase-multilingual-MiniLM-L12-v2"
    model_loader = ModelLoaderService(model)
    model_instance = model_loader.model

    tp = TranscriptProcessorService()

    v_id = "VQnM8Y3RIyM"
    languages = ["pt"]

    fetch = tp.fetch_transcript(video_id=v_id, languages=languages)

    # pprint(fetch)
