from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModelForCausalLM
)

import torch


class InteligenciaArtificial:

    def __init__(self):

        self.quantidadeCaracter = 3000

        modelo = "Qwen/Qwen2.5-Coder-1.5B-Instruct"

        # Verifica se CUDA está disponível
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA não está disponível.")

        print("=" * 50)
        print("JARVAS")
        print("GPU:", torch.cuda.get_device_name(0))
        print("=" * 50)

        # Tokenizador
        self.tokenizer = AutoTokenizer.from_pretrained(modelo)

        # Modelo em FLOAT16
        self.modelo = AutoModelForCausalLM.from_pretrained(
            modelo,
            dtype=torch.float16
        )

        # Coloca o modelo na RTX
        self.modelo = self.modelo.to("cuda")

        # Pipeline usando GPU
        self.ia = pipeline(
            "text-generation",
            model=self.modelo,
            tokenizer=self.tokenizer,
            device=0
        )

    def inferencia(self, pergunta):

        prompt = f"""
Você é JARVAS, um assistente especializado em programação e tecnologia.

REGRAS OBRIGATÓRIAS:
1. Responda sempre em português do Brasil.
2. Responda somente à pergunta apresentada.
3. Seja claro, direto e objetivo.
4. Sua resposta deve ter no máximo {self.quantidadeCaracter} caracteres.
5. Não adicione informações desnecessárias.
6. Sempre finalize a resposta com ponto final.
7. Se precisar explicar código, seja conciso e mostre apenas o código necessário.

Pergunta do usuário:
{pergunta}

Resposta:
"""

        resposta = self.ia(
            prompt,
            max_new_tokens=120,
            temperature=0.3,
            do_sample=True
        )

        texto = resposta[0]["generated_text"][len(prompt):].strip()

        print(texto)

        return texto