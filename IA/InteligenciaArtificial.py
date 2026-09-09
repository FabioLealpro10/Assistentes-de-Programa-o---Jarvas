from transformers import AutoTokenizer, AutoModelForCausalLM

import os
import torch

MODELO_PADRAO = os.environ.get(
    "JARVAS_IA_MODELO",
    "Qwen/Qwen2.5-Coder-1.5B-Instruct",
)

BACKENDS_VALIDOS = ("auto", "cuda", "cpu", "directml")


def detectar_backend():
    """
    Escolhe onde a IA vai rodar.

    Variável de ambiente JARVAS_IA_DEVICE:
      - auto     → detecta sozinho (padrão)
      - cuda     → força GPU NVIDIA
      - directml → força GPU AMD/Intel no Windows (DirectML)
      - cpu      → força processador (funciona em qualquer PC)
    """
    preferido = os.environ.get("JARVAS_IA_DEVICE", "auto").lower().strip()

    if preferido == "cpu":
        return "cpu", torch.device("cpu"), "CPU (escolhido manualmente)"

    if preferido == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError(
                "JARVAS_IA_DEVICE=cuda, mas CUDA não está disponível. "
                "Verifique drivers NVIDIA e instale PyTorch com suporte CUDA, "
                "ou use JARVAS_IA_DEVICE=cpu."
            )
        nome_gpu = torch.cuda.get_device_name(0)
        return "cuda", torch.device("cuda"), f"NVIDIA CUDA — {nome_gpu}"

    if preferido == "directml":
        try:
            import torch_directml
        except ImportError as exc:
            raise RuntimeError(
                "JARVAS_IA_DEVICE=directml, mas torch-directml não está instalado. "
                "Execute: pip install torch-directml"
            ) from exc
        device = torch_directml.device()
        return "directml", device, "GPU AMD/Intel — DirectML (Windows)"

    if preferido not in ("auto", ""):
        raise RuntimeError(
            f"JARVAS_IA_DEVICE='{preferido}' é inválido. "
            f"Use um destes: {', '.join(BACKENDS_VALIDOS)}."
        )

    # auto — tenta NVIDIA, depois DirectML (AMD), depois CPU
    if torch.cuda.is_available():
        nome_gpu = torch.cuda.get_device_name(0)
        return "cuda", torch.device("cuda"), f"NVIDIA CUDA — {nome_gpu} (auto)"

    try:
        import torch_directml
        device = torch_directml.device()
        return "directml", device, "GPU AMD/Intel — DirectML (auto)"
    except ImportError:
        pass

    return "cpu", torch.device("cpu"), "CPU (nenhuma GPU compatível detectada)"


def info_backend():
    """Retorna descrição do backend sem carregar o modelo."""
    try:
        _, _, descricao = detectar_backend()
        return descricao
    except RuntimeError as exc:
        return f"Erro: {exc}"


class InteligenciaArtificial:

    def __init__(self, modelo=None):
        self.quantidadeCaracter = 3000
        self.modelo_nome = modelo or MODELO_PADRAO

        self.backend, self.device, self.device_descricao = detectar_backend()
        usar_fp16 = self.backend == "cuda"
        dtype = torch.float16 if usar_fp16 else torch.float32

        print("=" * 50)
        print("JARVAS — Inteligência Artificial")
        print(f"Modelo : {self.modelo_nome}")
        print(f"Backend: {self.backend}")
        print(f"Device : {self.device_descricao}")
        print("=" * 50)

        self.tokenizer = AutoTokenizer.from_pretrained(self.modelo_nome)

        self.modelo = AutoModelForCausalLM.from_pretrained(
            self.modelo_nome,
            torch_dtype=dtype,
        )
        self.modelo.to(self.device)
        self.modelo.eval()


    def inferencia(self, pergunta):

        mensagens = [
            {
                "role": "system",
                "content": f"""
    Você é JARVAS, um assistente especializado em programação e tecnologia.

    REGRAS:
    - Responda sempre em português do Brasil.
    - Responda diretamente à pergunta do usuário.
    - Seja claro e objetivo.
    - Explique o necessário para resolver o problema.
    - Quando houver código, forneça o código completo necessário.
    - Não interrompa exemplos de código.
    - Não invente informações.
    - Não repita a pergunta do usuário.
    """
            },
            {
                "role": "user",
                "content": pergunta
            }
        ]

        texto_prompt = self.tokenizer.apply_chat_template(
            mensagens,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer(
            texto_prompt,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            output = self.modelo.generate(
                **inputs,
                max_new_tokens=500,
                temperature=0.2,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        novos_tokens = output[0][inputs["input_ids"].shape[1]:]

        texto = self.tokenizer.decode(
            novos_tokens,
            skip_special_tokens=True
        ).strip()

        print(texto)

        return texto