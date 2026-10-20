#!/usr/bin/env python3
"""Local Piper TTS server for the Ethiopian Bible reader.

Endpoints:
  GET /piper/voices            -> JSON list of available voices
  GET /piper/tts?voice=NAME&text=...  -> audio/wav

Run:  python3 piper_server.py [port]
"""
import sys
import os
import io
import json
import wave
import urllib.parse
import warnings
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

warnings.filterwarnings("ignore")

from piper import PiperVoice
from piper.config import SynthesisConfig

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE_DIR = os.path.join(HERE, "tts_voices")

# voice name -> (file, label, gender)
VOICES = {
    "mihai":      ("mihai.onnx",      "Mihai",      "M"),
    "lili":       ("lili.onnx",       "Lili",       "F"),
    "lili-high":  ("lili-high.onnx",  "Lili (HQ)",  "F"),
    "sanda":      ("sanda.onnx",      "Sanda",      "F"),
    "sanda-high": ("sanda-high.onnx", "Sanda (HQ)", "F"),
    "raluca":     ("raluca.onnx",     "Raluca",     "F"),
    "liana":      ("liana.onnx",      "Liana",      "F"),
}

_cache = {}


def get_voice(name):
    if name in _cache:
        return _cache[name]
    if name not in VOICES:
        return None
    path = os.path.join(VOICE_DIR, VOICES[name][0])
    v = PiperVoice.load(path)
    _cache[name] = v
    return v


def synth_wav(voice, text, length_scale=1.0):
    cfg = SynthesisConfig(length_scale=length_scale)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(voice.config.sample_rate)
        for chunk in voice.synthesize(text, syn_config=cfg):
            wf.writeframes(chunk.audio_int16_bytes)
    return buf.getvalue()


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(u.query)

        if u.path == "/piper/voices":
            data = [{"id": k, "label": v[1], "gender": v[2], "lang": "ro-RO"}
                    for k, v in VOICES.items()]
            body = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if u.path == "/piper/tts":
            name = (qs.get("voice", ["mihai"])[0] or "mihai").strip()
            text = (qs.get("text", [""])[0] or "").strip()
            try:
                length_scale = float(qs.get("length_scale", ["1.0"])[0])
            except ValueError:
                length_scale = 1.0
            if not text:
                self.send_error(400, "empty text")
                return
            text = text[:4000]
            v = get_voice(name)
            if v is None:
                self.send_error(404, "unknown voice: " + name)
                return
            try:
                wav = synth_wav(v, text, length_scale)
            except Exception as e:
                self.send_error(500, "synth error: " + str(e))
                return
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(len(wav)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(wav)
            return

        self.send_error(404, "not found")

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8124
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print("piper TTS server on http://127.0.0.1:%d" % port, flush=True)
    srv.serve_forever()
