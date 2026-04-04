from typing import Annotated
import shutil
import os
import tempfile

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form

from src.infrastructure.repositories.storage.storage import StorageService
from src.application.use_cases.manage_voice_profiles import (
    RegisterNewVoiceProfileUseCase,
    ListRegisteredVoiceProfilesUseCase,
    DeleteVoiceProfileUseCase,
    TrainVoiceProfileFromSpeakerSegmentUseCase,
    ListVoiceAudioFilesUseCase,
    DeleteVoiceAudioFileUseCase,
)
from src.presentation.api.dependencies import (
    get_register_voice_profile_use_case,
    get_list_voice_profiles_use_case,
    get_delete_voice_profile_use_case,
    get_train_voice_from_speaker_use_case,
    get_list_voice_audio_files_use_case,
    get_delete_voice_audio_file_use_case,
)
from src.presentation.api.schemas.voice_profile_requests import (
    VoiceProfileRegistrationRequest,
    VoiceProfileTrainingFromSpeakerRequest,
)

router = APIRouter()


@router.post("", responses={400: {"description": "Bad Request"}})
async def register_new_voice_profile(
    request: VoiceProfileRegistrationRequest,
    use_case: Annotated[
        RegisterNewVoiceProfileUseCase, Depends(get_register_voice_profile_use_case)
    ],
):
    try:
        voice_id = use_case.execute(
            request.name, request.audio_path, force=request.force
        )
        return {"status": "success", "voice_id": voice_id, "name": request.name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/upload", responses={400: {"description": "Bad Request"}})
async def upload_and_register_new_voice_profile(
    use_case: Annotated[
        RegisterNewVoiceProfileUseCase, Depends(get_register_voice_profile_use_case)
    ],
    name: str = Form(...),
    file: UploadFile = File(...),
    force: bool = Form(False),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        voice_id = use_case.execute(name, temp_path, force=force)
        return {"status": "success", "voice_id": voice_id, "name": name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)


@router.post(
    "/train-from-speaker",
    responses={
        400: {"description": "Bad Request"},
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"},
    },
)
async def train_voice_profile_from_existing_speaker_segment(
    request: VoiceProfileTrainingFromSpeakerRequest,
    use_case: Annotated[
        TrainVoiceProfileFromSpeakerSegmentUseCase,
        Depends(get_train_voice_from_speaker_use_case),
    ],
):
    try:
        voice_id = use_case.execute(
            diarization_id=request.diarization_id,
            speaker_label=request.speaker_label,
            name=request.name,
            force=request.force,
        )
        return {"status": "success", "voice_id": voice_id, "name": request.name}
    except ValueError as e:
        raise HTTPException(
            status_code=404 if "not found" in str(e) else 400, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_all_registered_voice_profiles(
    use_case: Annotated[
        ListRegisteredVoiceProfilesUseCase, Depends(get_list_voice_profiles_use_case)
    ],
):
    return use_case.execute()


@router.delete("/{name}", responses={404: {"description": "Not Found"}})
async def delete_existing_voice_profile(
    name: str,
    use_case: Annotated[
        DeleteVoiceProfileUseCase, Depends(get_delete_voice_profile_use_case)
    ],
):
    try:
        use_case.execute(name)
        return {
            "status": "success",
            "message": f"Voice profile '{name}' successfully removed",
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Voice profile '{name}' not found")


@router.get("/{voice_id}/audios")
async def list_voice_audio_files(
    voice_id: str,
    use_case: Annotated[
        ListVoiceAudioFilesUseCase, Depends(get_list_voice_audio_files_use_case)
    ],
):
    return use_case.execute(voice_id)


@router.delete("/audios/{s3_key:path}", responses={404: {"description": "Not Found"}})
async def delete_voice_audio_file(
    s3_key: str,
    use_case: Annotated[
        DeleteVoiceAudioFileUseCase, Depends(get_delete_voice_audio_file_use_case)
    ],
):
    try:
        use_case.execute(s3_key)
        return {"status": "success", "message": "Audio file deleted"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/audios/{s3_key:path}", responses={404: {"description": "Not Found"}})
async def get_voice_audio_url(
    s3_key: str,
):
    """Retorna uma URL assinada para acessar um arquivo de áudio de perfil de voz."""
    try:
        storage = StorageService()
        url = storage.get_presigned_url(s3_key)
        return {"url": url, "s3_key": s3_key}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
