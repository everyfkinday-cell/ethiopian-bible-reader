#!/usr/bin/env python3
"""Unified server for the Ethiopian Bible reader on Hugging Face Spaces.

Serves:
  /                 -> the reader (static files from ./public)
  /piper/voices     -> JSON list of Romanian neural voices
  /piper/tts?voice=NAME&text=...  -> audio/wav

Port: 7860 (Hugging Face Spaces default, overridable via $PORT)
"""
import os
import sys
import io
import json
import wave
import threading
import warnings
import urllib.parse
import posixpath
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

warnings.filterwarnings("ignore")

# --- memory-friendly onnxruntime options (important for Render free 512MB) ---
try:
    import onnxruntime as _ort
    _orig_session = _ort.InferenceSession
    def _lean_session(*args, **kwargs):
        so = kwargs.get("sess_options") or _ort.SessionOptions()
        try:
            so.intra_op_num_threads = 1
            so.inter_op_num_threads = 1
            so.enable_cpu_mem_arena = False
            so.enable_mem_pattern = False
            so.execution_mode = _ort.ExecutionMode.ORT_SEQUENTIAL
        except Exception:
            pass
        kwargs["sess_options"] = so
        return _orig_session(*args, **kwargs)
    _ort.InferenceSession = _lean_session
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(HERE, "public")
VOICE_DIR = os.path.join(HERE, "tts_voices")

VOICES = {
    # id: (file, label, gender, lang, speaker_id)
    "mihai":     ("mihai.onnx",     "Mihai",     "M", "ro-RO", None),
    "thorsten":   ("thorsten.onnx",   "Thorsten",   "M", "de-DE", None),
    "hfc_male":   ("hfc_male.onnx",   "HFC Male",   "M", "en-US", None),
}

_PIPER = {"name": None, "voice": None}
_SYNTH_LOCK = threading.Lock()


def get_voice(name):
    """Load a voice, keeping at most ONE model in memory (Render free = 512MB)."""
    if name not in VOICES:
        return None
    if _PIPER["name"] == name and _PIPER["voice"] is not None:
        return _PIPER["voice"]
    # evict the previously cached voice before loading a new one
    _PIPER["voice"] = None
    _PIPER["name"] = None
    try:
        import gc
        gc.collect()
    except Exception:
        pass
    from piper import PiperVoice
    path = os.path.join(VOICE_DIR, VOICES[name][0])
    v = PiperVoice.load(path)
    _PIPER["voice"] = v
    _PIPER["name"] = name
    return v


def synth_wav(voice, text, length_scale=1.0, speaker_id=None):
    from piper.config import SynthesisConfig
    cfg = SynthesisConfig(length_scale=length_scale, speaker_id=speaker_id)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(voice.config.sample_rate)
        for chunk in voice.synthesize(text, syn_config=cfg):
            wf.writeframes(chunk.audio_int16_bytes)
    return buf.getvalue()


MIME = {
    ".html": "text/html; charset=utf-8", ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8", ".json": "application/json; charset=utf-8",
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".gif": "image/gif", ".svg": "image/svg+xml", ".ico": "image/x-icon",
    ".webp": "image/webp", ".txt": "text/plain; charset=utf-8",
}


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

    def _json(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def _serve_file(self, path):
        if not os.path.isfile(path):
            self.send_error(404, "not found")
            return
        ext = os.path.splitext(path)[1].lower()
        ctype = MIME.get(ext, "application/octet-stream")
        try:
            with open(path, "rb") as f:
                body = f.read()
        except OSError:
            self.send_error(500, "read error")
            return
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "public, max-age=3600")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(u.query)
        path = urllib.parse.unquote(u.path)

        if path == "/piper/voices":
            data = [{"id": k, "label": v[1], "gender": v[2], "lang": v[3]}
                    for k, v in VOICES.items()]
            body = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/piper/tts":
            name = (qs.get("voice", ["mihai"])[0] or "mihai").strip()
            text = (qs.get("text", [""])[0] or "").strip()
            try:
                length_scale = float(qs.get("length_scale", ["1.0"])[0])
            except ValueError:
                length_scale = 1.0
            if not text:
                self._json(400, {"error": "empty text"})
                return
            try:
                with _SYNTH_LOCK:
                    v = get_voice(name)
            except Exception as e:
                import traceback
                self._json(500, {"error": "load failed: " + str(e),
                                 "trace": traceback.format_exc()[-800:]})
                return
            if v is None:
                self._json(404, {"error": "unknown voice: " + name})
                return
            speaker_id = VOICES[name][4]
            try:
                sp = qs.get("speaker", [None])[0]
                if sp is not None and sp != "":
                    speaker_id = int(sp)
            except Exception:
                pass
            if speaker_id is not None and getattr(v.config, "num_speakers", 1) <= speaker_id:
                speaker_id = VOICES[name][4]
            try:
                with _SYNTH_LOCK:
                    wav = synth_wav(v, text[:4000], length_scale, speaker_id)
                print("[tts] voice=%s speaker=%s bytes=%d" % (name, speaker_id, len(wav)), flush=True)
            except Exception as e:
                import traceback
                self._json(500, {"error": "synth failed: " + str(e),
                                 "trace": traceback.format_exc()[-800:]})
                return
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(len(wav)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(wav)
            return

        if path == "/piper/health":
            self._json(200, {"ok": True, "voices": list(VOICES.keys()),
                             "cached": ([_PIPER["name"]] if _PIPER["name"] else [])})
            return

        # static files
        if path == "/" or path == "":
            path = "/index.html"
        safe = posixpath.normpath(path).lstrip("/")
        if safe.startswith(".."):
            self.send_error(403, "forbidden")
            return
        full = os.path.join(PUBLIC_DIR, safe)
        if os.path.isdir(full):
            full = os.path.join(full, "index.html")
        self._serve_file(full)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "7860"))
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print("serving on 0.0.0.0:%d" % port, flush=True)
    srv.serve_forever()
