class AudioOutputMixin:
    """Mixin to add Text-to-Speech (audio output) capability to BaseModel subclasses.

    The mixin only extends the `supported_modalities` set so that framework code can
    introspect capabilities.  Sub-classes are expected to return *bytes* or *bytearray*
    from `_process_response` representing raw audio data (e.g. WAV/MP3).
    """

    supported_modalities = {"text", "audio"}

    # NOTE: No helper methods are strictly required for audio output, but providing a
    # convenience passthrough keeps implementations consistent with other mix-ins.
    # Sub-classes may override `_process_response` if they need custom extraction. 