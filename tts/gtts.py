import sys
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import List, Optional

import numpy as np
import soundfile as sf

from google.cloud import texttospeech

# Ensure project root exists
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from logs_setup.logger import Logger

_file_logger = Logger(
    name="google_tts",
    log_file="logs/google_tts.log"
).get_logger()

_console = logging.StreamHandler(sys.stdout)
_console.setLevel(logging.DEBUG)
_console.setFormatter(
    logging.Formatter("[GoogleTTS] %(levelname)s | %(message)s")
)

if not any(
    isinstance(h, logging.StreamHandler)
    and h.stream is sys.stdout
    for h in _file_logger.handlers
):
    _file_logger.addHandler(_console)

logger = _file_logger


class GoogleTTS:

    def __init__(
        self,
        language_code: str = None,
        voice_name: str = None
    ):

        self.client = texttospeech.TextToSpeechClient()

        self.language_code = (
            language_code
            or os.getenv(
                "GOOGLE_TTS_LANGUAGE_CODE",
                "hi-IN"
            )
        )

        self.voice_name = (
            voice_name
            or os.getenv(
                "GOOGLE_TTS_VOICE_NAME",
                "hi-IN-Standard-A"
            )
        )

        self._sample_rate = int(
            os.getenv(
                "GOOGLE_TTS_SAMPLE_RATE",
                24000
            )
        )

        logger.info(
            f"Google TTS initialized | "
            f"language={self.language_code} | "
            f"voice={self.voice_name}"
        )

    @property
    def sample_rate(self) -> int:
        return self._sample_rate

    def _synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        language_code: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 0.0,
        volume_gain_db: float = 0.0,
    ):
        voice_name = voice or self.voice_name
        lang = language_code or self.language_code

        synthesis_input = texttospeech.SynthesisInput(
            text=text
        )

        voice_params = texttospeech.VoiceSelectionParams(
            language_code=lang,
            name=voice_name
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=speed,
            pitch=pitch,
            volume_gain_db=volume_gain_db,
            sample_rate_hertz=self.sample_rate
        )

        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice_params,
            audio_config=audio_config
        )

        return response.audio_content

    def text_to_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        language_code: Optional[str] = None,
        output_path: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 0.0,
        volume_gain_db: float = 0.0,
    ):
        if output_path is None:
            output_path = (
                f"output_"
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            )

        logger.info(
            f"Generating speech | voice={voice} | language_code={language_code or self.language_code}"
        )

        audio_content = self._synthesize(
            text=text,
            voice=voice,
            language_code=language_code,
            speed=speed,
            pitch=pitch,
            volume_gain_db=volume_gain_db,
        )

        # Write as a proper WAV so downstream audio players can decode it
        audio_int16 = np.frombuffer(audio_content, dtype=np.int16)
        audio_float32 = audio_int16.astype(np.float32) / 32768.0
        sf.write(output_path, audio_float32, self.sample_rate, subtype="PCM_16")

        logger.info(f"Speech generated and saved to {output_path}")

        return output_path

    def generate_audio_stream(
        self,
        text: str,
        voice: Optional[str] = None,
        language_code: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 0.0,
        volume_gain_db: float = 0.0,
        chunk_samples: int = 4096,
        **kwargs,
    ):
        """
        Streaming-compatible generator — yields float32 np.ndarray chunks.

        Google Standard TTS is non-streaming; we synthesize the full response
        once then chunk the LINEAR16 PCM into float32 numpy arrays so the
        calling pipeline can treat Google identically to Kokoro / Indic Parler.
        """
        logger.info(
            f"Streaming speech | voice={voice or self.voice_name} | "
            f"language={language_code or self.language_code} | "
            f"text_preview={text[:60]!r}"
        )

        audio_content = self._synthesize(
            text=text,
            voice=voice,
            language_code=language_code,
            speed=speed,
            pitch=pitch,
            volume_gain_db=volume_gain_db,
        )

        # Convert LINEAR16 raw PCM bytes → float32 numpy array
        audio_int16 = np.frombuffer(audio_content, dtype=np.int16)
        audio_float32 = audio_int16.astype(np.float32) / 32768.0

        for i in range(0, len(audio_float32), chunk_samples):
            yield audio_float32[i:i + chunk_samples]

    def batch_process(
        self,
        input_texts: List[str],
        output_dir: str,
        voice: Optional[str] = None,
        speed: float = 1.0
    ):

        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(
            parents=True,
            exist_ok=True
        )

        logger.info(
            f"Batch processing "
            f"{len(input_texts)} files"
        )

        generated_files = []

        for idx, text in enumerate(input_texts):

            output_file = (
                output_dir_path /
                f"output_{idx + 1:03d}.wav"
            )

            self.text_to_speech(
                text=text,
                voice=voice,
                output_path=str(output_file),
                speed=speed
            )

            generated_files.append(
                str(output_file)
            )

        logger.info(
            "Batch processing completed"
        )

        return generated_files

    def list_voices(
        self,
        language_code: Optional[str] = None
    ):

        response = self.client.list_voices()

        voices = []

        for voice in response.voices:

            if (
                language_code
                and language_code
                not in voice.language_codes
            ):
                continue

            voices.append(
                {
                    "name": voice.name,
                    "languages": list(
                        voice.language_codes
                    ),
                    "gender": voice.ssml_gender.name,
                    "sample_rate": (
                        voice.natural_sample_rate_hertz
                    )
                }
            )

        return voices

    def estimate_cost(
        self,
        text: str,
        cost_per_million_chars: float = 4.0
    ):

        chars = len(text)

        cost_usd = (
            chars / 1_000_000
        ) * cost_per_million_chars

        return {
            "characters": chars,
            "estimated_cost_usd": round(
                cost_usd,
                6
            )
        }


if __name__ == "__main__":

    tts = GoogleTTS(
        language_code="hi-IN",
        voice_name="hi-IN-Standard-A"
    )
    gujarati_text = """
    નમસ્તે, તમારું કેમ ચાલે છે?
    આજે હવામાન ખૂબ સારું છે.
    મને ગુજરાતી ભાષા ગમે છે.
    હું દરરોજ સવારે ચાલવા જાઉં છું.
    કૃપા કરીને મને મદદ કરો.
    મારા મિત્રો ખૂબ સારા છે.
    મને ચા પીવી ગમે છે.
    અમે આજે બજારમાં જઈ રહ્યા છીએ.
    તમારો દિવસ શુભ રહે.
    આ પુસ્તક ખૂબ રસપ્રદ છે.
    """
    gujarati_text2 = """
    Namaste, tamaaru kem chaale chhe?
    Aaje havaamaan khub saarun chhe.
    Mane Gujarati bhaasha game chhe.
    Hun darroj savaare chaalvaa jaun chhun.
    Krupaa karine mane madad karo.
    Maaraa mitro khub saaraa chhe.
    Mane chaa peevi game chhe.
    Ame aaje bajaarmaa jai rahyaa chhiye.
    Tamaaro divas shubh rahe.
    Aa pustak khub rasprad chhe.
    """
    output_file = tts.text_to_speech(
        text=gujarati_text2,
        speed=1.0,
        output_path="gujrati2_output.wav"
    )

    print(output_file)