import os
import time

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


# =========================================================
# CONFIGURAÇÕES
# =========================================================

MODELO_PADRAO = os.environ.get(
    "JARVAS_IA_MODELO",
    "Qwen/Qwen2.5-Coder-1.5B-Instruct",
)

BACKENDS_VALIDOS = (
    "auto",
    "cuda",
    "cpu",
    "directml",
)


# =========================================================
# DETECTAR BACKEND
# =========================================================

def detectar_backend():

    preferido = os.environ.get(
        "JARVAS_IA_DEVICE",
        "auto"
    ).lower().strip()


    # =====================================================
    # CPU
    # =====================================================

    if preferido == "cpu":

        return (
            "cpu",
            torch.device("cpu"),
            "CPU (escolhido manualmente)"
        )


    # =====================================================
    # NVIDIA CUDA
    # =====================================================

    if preferido == "cuda":

        if not torch.cuda.is_available():

            raise RuntimeError(
                "JARVAS_IA_DEVICE=cuda, "
                "mas CUDA não está disponível."
            )

        nome_gpu = torch.cuda.get_device_name(0)

        return (
            "cuda",
            torch.device("cuda"),
            f"NVIDIA CUDA — {nome_gpu}"
        )


    # =====================================================
    # AMD / INTEL - DIRECTML
    # =====================================================

    if preferido == "directml":

        try:

            import torch_directml

        except ImportError as exc:

            raise RuntimeError(
                "JARVAS_IA_DEVICE=directml, "
                "mas torch-directml não está instalado.\n\n"
                "Execute:\n"
                "python -m pip install torch-directml"
            ) from exc


        device = torch_directml.device()


        return (
            "directml",
            device,
            "GPU AMD/Intel — DirectML"
        )


    # =====================================================
    # VALIDAR CONFIGURAÇÃO
    # =====================================================

    if preferido not in ("auto", ""):

        raise RuntimeError(
            f"JARVAS_IA_DEVICE='{preferido}' é inválido.\n"
            f"Use: {', '.join(BACKENDS_VALIDOS)}"
        )


    # =====================================================
    # AUTO → NVIDIA
    # =====================================================

    if torch.cuda.is_available():

        nome_gpu = torch.cuda.get_device_name(0)

        return (
            "cuda",
            torch.device("cuda"),
            f"NVIDIA CUDA — {nome_gpu}"
        )


    # =====================================================
    # AUTO → DIRECTML
    # =====================================================

    try:

        import torch_directml

        device = torch_directml.device()


        return (
            "directml",
            device,
            "GPU AMD/Intel — DirectML"
        )


    except ImportError:

        pass


    # =====================================================
    # AUTO → CPU
    # =====================================================

    return (
        "cpu",
        torch.device("cpu"),
        "CPU"
    )


# =========================================================
# INFORMAÇÕES DO BACKEND
# =========================================================

def info_backend():

    try:

        _, _, descricao = detectar_backend()

        return descricao

    except RuntimeError as exc:

        return f"Erro: {exc}"


# =========================================================
# INTELIGÊNCIA ARTIFICIAL
# =========================================================

class InteligenciaArtificial:


    def __init__(self, modelo=None):

        # -------------------------------------------------
        # Configurações
        # -------------------------------------------------

        self.quantidadeCaracter = 3000

        self.modelo_nome = (
            modelo or MODELO_PADRAO
        )


        # -------------------------------------------------
        # Detectar dispositivo
        # -------------------------------------------------

        (
            self.backend,
            self.device,
            self.device_descricao
        ) = detectar_backend()


        # -------------------------------------------------
        # Precisão
        # -------------------------------------------------

        if self.backend == "cuda":

            dtype = torch.float16


        elif self.backend == "directml":

            # DirectML + AMD
            dtype = torch.float16


        else:

            dtype = torch.float32


        self.dtype = dtype


        # -------------------------------------------------
        # Informações
        # -------------------------------------------------

        print()
        print("=" * 60)
        print("JARVAS — INTELIGÊNCIA ARTIFICIAL")
        print("=" * 60)

        print(
            f"Modelo  : {self.modelo_nome}"
        )

        print(
            f"Backend : {self.backend}"
        )

        print(
            f"Device  : {self.device_descricao}"
        )

        print(
            f"DType   : {self.dtype}"
        )

        print(
            f"CPU     : {os.cpu_count()} threads disponíveis"
        )

        print("=" * 60)


        # -------------------------------------------------
        # Tokenizer
        # -------------------------------------------------

        print()
        print("Carregando tokenizer...")

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.modelo_nome
        )

        print("Tokenizer carregado.")


        # -------------------------------------------------
        # Modelo
        # -------------------------------------------------

        print()
        print("Carregando modelo...")


        self.modelo = AutoModelForCausalLM.from_pretrained(
                self.modelo_nome,
                torch_dtype=self.dtype,
            )

        print("Modelo carregado na RAM.")


        # -------------------------------------------------
        # GPU
        # -------------------------------------------------

        print()
        print(
            f"Enviando modelo para: {self.device_descricao}"
        )


        self.modelo = self.modelo.to(
            self.device
        )


        # -------------------------------------------------
        # Modo avaliação
        # -------------------------------------------------

        self.modelo.eval()


        print()
        print("Modelo enviado para o dispositivo.")
        print("JARVAS pronto.")

        print("=" * 60)
        print()


    # =====================================================
    # INFERÊNCIA
    # =====================================================

    def inferencia(self, pergunta):

        inicio = time.time()


        # -------------------------------------------------
        # Mensagens
        # -------------------------------------------------

        mensagens = [

            {
                "role": "system",

                "content": """
Você é JARVAS, um assistente especializado
em programação e tecnologia.

REGRAS:

- Responda sempre em português do Brasil.
- Responda diretamente à pergunta do usuário.
- Seja claro e objetivo.
- Explique somente o necessário.
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


        # -------------------------------------------------
        # Chat Template
        # -------------------------------------------------

        texto_prompt = (
            self.tokenizer.apply_chat_template(

                mensagens,

                tokenize=False,

                add_generation_prompt=True
            )
        )


        # -------------------------------------------------
        # Tokenização
        # -------------------------------------------------

        inputs = self.tokenizer(

            texto_prompt,

            return_tensors="pt",

            truncation=True,

            max_length=4096
        )


        # -------------------------------------------------
        # Enviar entrada para GPU
        # -------------------------------------------------

        inputs = {

            chave: valor.to(self.device)

            for chave, valor in inputs.items()
        }


        # -------------------------------------------------
        # Inferência
        # -------------------------------------------------

        print("Executando inferência...")

        inicio_geracao = time.time()


        with torch.no_grad():

            output = self.modelo.generate(

                **inputs,

                max_new_tokens=500,

                temperature=0.2,

                do_sample=True,

                use_cache=True,

                pad_token_id=(
                    self.tokenizer.eos_token_id
                ),
            )


        fim_geracao = time.time()


        # -------------------------------------------------
        # Remover prompt
        # -------------------------------------------------

        input_length = (
            inputs["input_ids"].shape[1]
        )


        novos_tokens = output[0][
            input_length:
        ]


        # -------------------------------------------------
        # Decodificar
        # -------------------------------------------------

        texto = self.tokenizer.decode(

            novos_tokens,

            skip_special_tokens=True

        ).strip()


        # -------------------------------------------------
        # Estatísticas
        # -------------------------------------------------

        tempo_total = time.time() - inicio

        tempo_geracao = (
            fim_geracao - inicio_geracao
        )

        quantidade_tokens = (
            len(novos_tokens)
        )


        if tempo_geracao > 0:

            tokens_por_segundo = (
                quantidade_tokens /
                tempo_geracao
            )

        else:

            tokens_por_segundo = 0


        # -------------------------------------------------
        # Resultado
        # -------------------------------------------------

        print()
        print("=" * 60)
        print("RESPOSTA DA IA")
        print("=" * 60)

        print(texto)

        print("=" * 60)

        print(
            f"Tokens gerados : {quantidade_tokens}"
        )

        print(
            f"Tempo geração  : {tempo_geracao:.2f}s"
        )

        print(
            f"Velocidade     : "
            f"{tokens_por_segundo:.2f} tokens/s"
        )

        print(
            f"Tempo total    : {tempo_total:.2f}s"
        )

        print("=" * 60)
        print()


        return texto