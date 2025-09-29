class AudioInputMixin:
    """Mixin to add Speech-to-Text (audio input) capability to BaseModel subclasses.

    Adds the "audio" modality flag and provides a default `_prepare_audio_payload` helper that
    converts various audio representations (bytes, filepath, or pathlib.Path) into raw bytes that
    can be forwarded to the underlying client implementation.
    """

    # Extend capabilities advertised by the subclass
    supported_modalities = {"text", "audio"}

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------
    def _prepare_audio_payload(self, audio):  # noqa: D401, N802 (follow existing naming style)
        """Return *raw bytes* for an audio input.

        Accepts one of:
            • *bytes* / *bytearray*
            • *str* or *pathlib.Path* pointing to an audio file.

        Raises:
            TypeError – when the provided object cannot be interpreted as audio data.
        """
        from pathlib import Path

        # Already raw bytes
        if isinstance(audio, (bytes, bytearray)):
            return bytes(audio)

        # File-path like objects
        if isinstance(audio, (str, Path)):
            return Path(audio).expanduser().resolve().read_bytes()

        raise TypeError(f"Unsupported audio input type: {type(audio)}") 