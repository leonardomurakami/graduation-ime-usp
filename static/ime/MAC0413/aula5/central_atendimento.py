from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class Prioridade(Enum):
    ALTA = 1
    MEDIA = 2
    BAIXA = 3


@dataclass(frozen=True)
class Chamado:
    id: str
    descricao: str
    prioridade: Prioridade


class CentralAtendimento:

    def __init__(self):
        self.chamados = {
            Prioridade.ALTA: [],
            Prioridade.MEDIA: [],
            Prioridade.BAIXA: []
        }

    def adicionar(self, chamado: Chamado) -> bool:
        """
        Adiciona um chamado à central.

        Retorna:
            True  - se o chamado foi adicionado.
            False - se já existir um chamado pendente com o mesmo ID.
        """
        for prioridade in [Prioridade.ALTA, Prioridade.MEDIA, Prioridade.BAIXA]:
            for c in self.chamados[prioridade]:
                if c.id == chamado.id:
                    return False
        self.chamados[chamado.prioridade].append(chamado)
        return True


    def atender_proximo(self) -> Optional[Chamado]:
        """
        Remove e retorna o próximo chamado.

        Prioridade:
            ALTA > MEDIA > BAIXA

        Entre chamados da mesma prioridade deve ser respeitada
        a ordem de chegada.

        Retorna None caso não existam chamados pendentes.
        """
        for prioridade in [Prioridade.ALTA, Prioridade.MEDIA, Prioridade.BAIXA]:
            if self.chamados[prioridade]:
                return self.chamados[prioridade].pop(0)
        return None

    def cancelar(self, id: str) -> bool:
        """
        Cancela um chamado pendente.

        Retorna:
            True  - se o chamado foi removido.
            False - se o ID não corresponder a um chamado pendente.
        """
        for prioridade in [Prioridade.ALTA, Prioridade.MEDIA, Prioridade.BAIXA]:
            for c in self.chamados[prioridade]:
                if c.id == id:
                    self.chamados[prioridade].remove(c)
                    return True
        return False

    def pendentes(self) -> List[Chamado]:
        """
        Retorna os chamados pendentes na ordem em que seriam atendidos.

        A consulta não deve alterar o estado da central.

        Modificar a lista retornada também não deve modificar
        a central.
        """
        pendentes = []
        for prioridade in [Prioridade.ALTA, Prioridade.MEDIA, Prioridade.BAIXA]:
            pendentes += self.chamados[prioridade]
        return pendentes

    def quantidade_pendentes(self) -> int:
        """
        Retorna a quantidade de chamados atualmente pendentes.
        """
        pendentes = 0
        for prioridade in [Prioridade.ALTA, Prioridade.MEDIA, Prioridade.BAIXA]:
            pendentes += len(self.chamados[prioridade])
        return pendentes