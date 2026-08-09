from __future__ import annotations

import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ModelPreset:
    id: str
    name: str
    provider: str
    model: str
    base_url: str
    environment_key: str


MODEL_PRESETS = (
    ModelPreset(
        "deepseek-chat",
        "DeepSeek Chat",
        "deepseek",
        "deepseek-chat",
        "https://api.deepseek.com/chat/completions",
        "DEEPSEEK_API_KEY",
    ),
    ModelPreset(
        "deepseek-reasoner",
        "DeepSeek Reasoner",
        "deepseek",
        "deepseek-reasoner",
        "https://api.deepseek.com/chat/completions",
        "DEEPSEEK_API_KEY",
    ),
    ModelPreset(
        "gpt-4o-mini",
        "OpenAI GPT-4o mini",
        "openai",
        "gpt-4o-mini",
        "https://api.openai.com/v1/chat/completions",
        "OPENAI_API_KEY",
    ),
    ModelPreset(
        "gpt-4.1-mini",
        "OpenAI GPT-4.1 mini",
        "openai",
        "gpt-4.1-mini",
        "https://api.openai.com/v1/chat/completions",
        "OPENAI_API_KEY",
    ),
)


def get_preset(preset_id: str) -> ModelPreset:
    return next((preset for preset in MODEL_PRESETS if preset.id == preset_id), MODEL_PRESETS[0])


def resolve_api_key(provider: str = "deepseek") -> str:
    """Resolve a provider credential without displaying or persisting it."""
    preset = next((item for item in MODEL_PRESETS if item.provider == provider), MODEL_PRESETS[0])
    environment_key = os.getenv(preset.environment_key, "").strip()
    if environment_key:
        return environment_key

    pi_binary = shutil.which("pi.cmd") or shutil.which("pi.exe") or shutil.which("pi")
    if not pi_binary:
        return ""
    command = [pi_binary, "auth", "print-api-key", "--provider", provider]
    try:
        if os.name == "nt" and pi_binary.lower().endswith((".cmd", ".bat")):
            result = subprocess.run(
                subprocess.list2cmdline(command),
                shell=True,
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
        else:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


@dataclass(slots=True)
class DeepSeekClient:
    """OpenAI-compatible multi-provider client retained under its old import name."""

    api_key: str = ""
    model: str = "deepseek-chat"
    base_url: str = "https://api.deepseek.com/chat/completions"
    timeout: int = 60
    preset_id: str = "deepseek-chat"
    provider: str = "deepseek"
    display_name: str = "DeepSeek Chat"
    _session_keys: dict[str, str] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        preset = get_preset(self.preset_id if self.preset_id else self.model)
        self._apply_preset(preset)
        if self.api_key.strip():
            self._session_keys[self.provider] = self.api_key.strip()

    @property
    def configured(self) -> bool:
        return bool(self.api_key.strip())

    def _apply_preset(self, preset: ModelPreset) -> None:
        self.preset_id = preset.id
        self.provider = preset.provider
        self.display_name = preset.name
        self.model = preset.model
        self.base_url = preset.base_url

    def select_preset(self, preset_id: str) -> None:
        if self.api_key.strip():
            self._session_keys[self.provider] = self.api_key.strip()
        preset = get_preset(preset_id)
        self._apply_preset(preset)
        self.api_key = self._session_keys.get(self.provider, "") or resolve_api_key(self.provider)
        if self.api_key:
            self._session_keys[self.provider] = self.api_key

    def set_api_key(self, key: str) -> None:
        self.api_key = key.strip()
        if self.api_key:
            self._session_keys[self.provider] = self.api_key

    def explain(
        self,
        query: str,
        history: list[tuple[str, str]],
        dictionary_name: str,
    ) -> str:
        if not self.configured:
            raise RuntimeError(
                f"{self.display_name} API key is not configured. Open settings with g, "
                "press p, paste the provider key, and press Enter."
            )

        system_prompt = (
            "You are VocaBot, a concise English vocabulary tutor. "
            "Explain words and phrases directly in English. Include the precise meaning, "
            "part of speech, pronunciation when useful, one or two natural examples, "
            "common collocations, and one easily confused alternative. Keep ordinary "
            "responses under 140 words. Use compact Markdown, short paragraphs, and no "
            "redundant introduction or conclusion. The learner's active dictionary is "
            f"{dictionary_name}. Do not discuss programming unless it helps explain a word."
        )
        messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        for role, content in history[-8:]:
            if role.casefold() == "you":
                messages.append({"role": "user", "content": content})
            elif not content.startswith("VocaBot error:"):
                messages.append({"role": "assistant", "content": content})
        messages.append({"role": "user", "content": query})

        request = urllib.request.Request(
            self.base_url,
            data=json.dumps(
                {
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.4,
                    "max_tokens": 700,
                    "stream": False,
                }
            ).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key.strip()}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            try:
                detail = json.loads(body).get("error", {}).get("message", body)
            except json.JSONDecodeError:
                detail = body
            raise RuntimeError(f"{self.display_name} HTTP {error.code}: {detail}") from error
        except urllib.error.URLError as error:
            raise RuntimeError(f"{self.display_name} connection failed: {error.reason}") from error

        try:
            return str(payload["choices"][0]["message"]["content"]).strip()
        except (KeyError, IndexError, TypeError) as error:
            raise RuntimeError(f"{self.display_name} returned an unexpected response") from error
