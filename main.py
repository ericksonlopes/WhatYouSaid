from pprint import pprint

from youtube_transcript_api import FetchedTranscript

from src.config.settings import settings
from src.infrastructure.extractors.youtube_transcript_processor_extractor import YoutubeTranscriptExtractor
from src.infrastructure.services.model_loader_service import ModelLoaderService
from src.infrastructure.services.youtube_text_temporal_splitter_service import YoutubeTranscriptSplitterService

if __name__ == '__main__':
    v_id = "VQnM8Y3RIyM"
    languages = ["pt"]

    model = settings.MODEL_EMBEDDING_NAME
    model_loader = ModelLoaderService(model)

    ytp = YoutubeTranscriptExtractor()

    fetch: FetchedTranscript = ytp.fetch_transcript(video_id=v_id, languages=languages)

    ytts = YoutubeTranscriptSplitterService(model_loader)
    result = ytts.split_transcript(fetch, mode="tokens", tokens_per_chunk=512, token_overlap=5)
    pprint(result)
