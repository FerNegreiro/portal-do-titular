from collections import deque
from datetime import datetime, timedelta


class RelogioAjustavel:
    def __init__(self):
        self.deslocamento = timedelta()

    def __call__(self) -> datetime:
        return datetime.now() + self.deslocamento

    def avancar(self, dias: int) -> None:
        self.deslocamento += timedelta(days=dias)


class CaixaDeEntrada:
    def __init__(self, relogio, limite: int = 50):
        self._relogio = relogio
        self.mensagens = deque(maxlen=limite)

    def __call__(self, destino: str, mensagem: str) -> None:
        print(f"[e-mail para {destino}] {mensagem}", flush=True)
        self.mensagens.appendleft({
            "momento": self._relogio().isoformat(timespec="seconds"),
            "destino": destino,
            "mensagem": mensagem,
        })
