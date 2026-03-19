---
description: How to add a new Content Source to WhatYouSaid
---

# 📥 Workflow: Add New Content Source

This workflow describes the end-to-end process for integrating a new data source (e.g., Instagram, TikTok, LinkedIn) into the `WhatYouSaid` ecosystem.

## 1. Domain (Entities and Enums)
- [ ] Add the new type to the `ContentSourceType` Enum in `src/domain/enums/`.
- [ ] Define specific fields for the new source in the corresponding entity in `src/domain/entities/`.

## 2. Infrastructure (Extraction and Processing)
- [ ] Create a new Extractor class in `src/infrastructure/extractors/` inheriting from `IBaseExtractor`.
- [ ] Implement the `extract` method to download content and metadata.
- [ ] (Optional) If necessary, create a new `Repository` if the source requires unique persistent storage.

## 3. Application (Use Cases)
- [ ] Check if `ProcessContentSource` needs specific logic for the new type.
- [ ] Ensure that `Embeddings` and vectorization are being correctly called for the new format.

## 4. Presentation (API)
- [ ] Add the new type to the Pydantic Schemas in `src/presentation/api/schemas/content_source.py`.
- [ ] If there are new endpoints, add them in `src/presentation/api/routes/content_sources.py`.

## 5. Testing
- [ ] Create integration tests in `tests/infrastructure/extractors/` to validate data capture from samples.
- [ ] Add a full-flow test in `tests/api/test_content_sources.py`.

---
// turbo-all
## Quick Verification
Run `pytest tests/infrastructure/extractors/test_your_new_extractor.py`
