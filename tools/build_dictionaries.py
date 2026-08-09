from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


SOURCE_URL = "https://github.com/skywind3000/ECDICT"

AI_TERMS = {
    line.strip().casefold()
    for line in """
accelerator
accuracy
activation
agent
algorithm
alignment
allocation
annotation
API
architecture
array
artificial intelligence
attention
authentication
authorization
automation
availability
backpropagation
bandwidth
batch
benchmark
bias
binary
branch
cache
checkpoint
classification
client
cloud
cluster
clustering
code
compiler
complexity
concurrency
consistency
constant
container
context
convolution
corpus
CPU
database
data structure
dataset
deadlock
debug
decoder
deep learning
deployment
derivative
distillation
distributed
distribution
dropout
edge computing
embedding
encoder
encryption
entropy
epoch
evaluation
exception
explainability
exploit
feature
fine-tuning
firewall
framework
function
generation
generative artificial intelligence
GPU
gradient
graph
hallucination
hash
hyperparameter
index
inference
interface
interpreter
interpretability
iteration
kernel
label
language model
latency
layer
linked list
loss
machine learning
malware
matrix
memory
merge
metric
model
multimodal
mutex
network
neural network
neuron
normalization
objective
operating system
optimization
overfitting
packet
parallelism
parameter
partition
pipeline
precision
prediction
pretraining
privacy
probability
process
prompt
protocol
pruning
quantization
query
queue
reasoning
recall
recursion
regression
regularization
reinforcement learning
replication
repository
retrieval
robustness
runtime
safety
sampling
schema
search
security
semaphore
sequence
server
sharding
socket
sorting
sparsity
speech recognition
stack
storage
supervised learning
synthetic data
tensor
thread
throughput
token
tokenizer
training
transaction
transformer
traversal
tree
underfitting
unsupervised learning
variable
variance
vector
version control
virtualization
vulnerability
weight
""".splitlines()
    if line.strip()
}

MANUAL_AI_ENTRIES = {
    "backpropagation": ("/ˌbækprɒpəˈɡeɪʃən/", "n. an algorithm that computes gradients backward through a neural network", "n. 反向传播；神经网络中由输出层向输入层计算梯度的算法"),
    "deep learning": ("/ˌdiːp ˈlɜːnɪŋ/", "n. machine learning based on neural networks with many layers", "n. 深度学习；使用多层神经网络进行表示学习的方法"),
    "edge computing": ("/ˌedʒ kəmˈpjuːtɪŋ/", "n. processing data near the place where it is generated rather than in a central cloud", "n. 边缘计算；在接近数据产生位置的设备或节点上处理数据"),
    "explainability": ("/ɪkˌspleɪnəˈbɪləti/", "n. the degree to which a model's behavior and outputs can be understood", "n. 可解释性；模型行为及输出可被人理解的程度"),
    "generative artificial intelligence": ("/ˈdʒenərətɪv ˌɑːtɪfɪʃəl ɪnˈtelɪdʒəns/", "n. artificial intelligence that creates new text, images, audio, code, or other content", "n. 生成式人工智能；能够生成文本、图像、音频或代码等新内容的人工智能"),
    "hyperparameter": ("/ˌhaɪpəpəˈræmɪtə/", "n. a configuration value chosen before or during model training rather than learned from data", "n. 超参数；训练前或训练过程中设定而非从数据中学习的参数"),
    "language model": ("/ˈlæŋɡwɪdʒ ˌmɒdl/", "n. a model that represents the probability and structure of sequences of language", "n. 语言模型；对语言序列的概率及结构进行建模的模型"),
    "pretraining": ("/ˌpriːˈtreɪnɪŋ/", "n. training a model on broad data before adapting it to a specific task", "n. 预训练；在面向具体任务调整之前先使用大规模通用数据训练模型"),
    "reinforcement learning": ("/ˌriːɪnˈfɔːsmənt ˈlɜːnɪŋ/", "n. machine learning in which an agent learns by receiving rewards or penalties", "n. 强化学习；智能体通过奖励或惩罚信号学习策略的方法"),
    "sharding": ("/ˈʃɑːdɪŋ/", "n. dividing a database or model across multiple independent partitions", "n. 分片；将数据库或模型划分到多个独立分区的技术"),
    "synthetic data": ("/sɪnˌθetɪk ˈdeɪtə/", "n. artificially generated data designed to resemble real observations", "n. 合成数据；人工生成并模拟真实观测特征的数据"),
    "tokenizer": ("/ˈtəʊkənaɪzə/", "n. software that converts text into tokens that a language model can process", "n. 分词器；将文本转换为语言模型可处理标记的软件"),
    "underfitting": ("/ˌʌndəˈfɪtɪŋ/", "n. failure of a model to learn important patterns in its training data", "n. 欠拟合；模型未能学习训练数据中重要规律的现象"),
    "version control": ("/ˈvɜːʃən kənˌtrəʊl/", "n. a system for tracking and managing changes to files and source code", "n. 版本控制；跟踪并管理文件或源代码变更的系统"),
}


PART_NAMES = {
    "n": "noun",
    "v": "verb",
    "vt": "transitive verb",
    "vi": "intransitive verb",
    "a": "adjective",
    "s": "adjective",
    "adj": "adjective",
    "adv": "adverb",
    "r": "adverb",
    "prep": "preposition",
    "conj": "conjunction",
    "pron": "pronoun",
    "num": "number",
}
PART_PATTERN = re.compile(
    r"(?:^|\n)\s*(n|v|vt|vi|a|s|adj|adv|r|prep|conj|pron|num)\.",
    re.IGNORECASE,
)


def clean_text(value: str) -> str:
    value = value.replace("\\r", "").replace("\\n", "\n").replace("\r", "")
    lines = [line.strip() for line in value.splitlines()]
    lines = [line for line in lines if line and not line.startswith("[网络]")]
    return "\n".join(lines)


def infer_part(definition: str, translation: str) -> str:
    found: list[str] = []
    for match in PART_PATTERN.finditer(definition + "\n" + translation):
        name = PART_NAMES[match.group(1).casefold()]
        if name not in found:
            found.append(name)
    return " / ".join(found[:3]) if found else "word"


def load_existing(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {str(item["word"]).casefold(): item for item in payload.get("words", [])}


def make_entry(row: dict[str, str], existing: dict[str, dict[str, Any]]) -> dict[str, str]:
    word = row["word"].strip()
    previous = existing.get(word.casefold(), {})
    definition = clean_text(row.get("definition", "")) or "See the Chinese definition below."
    translation = clean_text(row.get("translation", ""))
    phonetic = row.get("phonetic", "").strip()
    if phonetic and not phonetic.startswith("/"):
        phonetic = f"/{phonetic}/"
    curated = bool(str(previous.get("example", "")).strip())
    return {
        "word": word,
        "phonetic": str(previous.get("phonetic", "")).strip() if curated else phonetic,
        "part": str(previous.get("part", "")).strip() if curated else infer_part(definition, translation),
        "definition": str(previous.get("definition", "")).strip() if curated else definition,
        "translation": translation or str(previous.get("translation", "")).strip(),
        "example": str(previous.get("example", "")).strip(),
    }


def write_dictionary(
    path: Path,
    dictionary_id: str,
    name: str,
    description: str,
    rows: list[dict[str, str]],
) -> None:
    existing = load_existing(path)
    entries = [make_entry(row, existing) for row in rows]
    entries.sort(key=lambda item: item["word"].casefold())
    payload = {
        "id": dictionary_id,
        "name": name,
        "description": description,
        "source": SOURCE_URL,
        "words": entries,
    }
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{name}: {len(entries)} words -> {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build bilingual dictionaries from ECDICT")
    parser.add_argument("source", type=Path, help="path to ecdict.csv")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "dictionaries",
    )
    args = parser.parse_args()

    graduate: dict[str, dict[str, str]] = {}
    cet6: dict[str, dict[str, str]] = {}
    ai: dict[str, dict[str, str]] = {}
    with args.source.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            word_key = row["word"].strip().casefold()
            tags = set((row.get("tag") or "").split())
            if "ky" in tags:
                graduate.setdefault(word_key, row)
            if "cet6" in tags:
                cet6.setdefault(word_key, row)
            if word_key in AI_TERMS:
                ai.setdefault(word_key, row)

    # Fill modern AI terms that are not yet present in ECDICT.
    ai_path = args.output / "ai-cs.json"
    for word, (phonetic, definition, translation) in MANUAL_AI_ENTRIES.items():
        ai.setdefault(
            word,
            {
                "word": word,
                "phonetic": phonetic,
                "definition": definition,
                "translation": translation,
                "pos": "noun",
            },
        )

    args.output.mkdir(parents=True, exist_ok=True)
    write_dictionary(
        args.output / "graduate-core.json",
        "graduate-core",
        "Graduate Core",
        "考研英语大纲核心词汇 · English and Chinese definitions",
        list(graduate.values()),
    )
    write_dictionary(
        ai_path,
        "ai-cs",
        "AI & CS",
        "人工智能与计算机科学核心术语 · English and Chinese definitions",
        list(ai.values()),
    )
    write_dictionary(
        args.output / "cet6.json",
        "cet6",
        "CET-6",
        "大学英语六级大纲词汇 · English and Chinese definitions",
        list(cet6.values()),
    )
    unresolved = sorted(AI_TERMS - ai.keys())
    if unresolved:
        print(f"AI terms not found ({len(unresolved)}): {', '.join(unresolved)}")


if __name__ == "__main__":
    main()
