class PoliticaEmprestimo:

    PRAZOS = {
        "ALUNO": {
            "LIVRO": 14,
            "REVISTA": 7,
            "MIDIA": 3
        },
        "PROFESSOR": {
            "LIVRO": 30,
            "REVISTA": 14,
            "MIDIA": 7
        }
    }

    TAXAS_MULTA = {
        "LIVRO": 1.0,
        "REVISTA": 1.5,
        "MIDIA": 3.0
    }

    @staticmethod
    def _validar_perfil(perfil):
        if perfil not in PoliticaEmprestimo.PRAZOS:
            raise ValueError("Perfil inválido")

    @staticmethod
    def _validar_material(material):
        if material not in PoliticaEmprestimo.TAXAS_MULTA:
            raise ValueError("Material inválido")

    @staticmethod
    def prazo_emprestimo(perfil, material):
        PoliticaEmprestimo._validar_perfil(perfil)
        PoliticaEmprestimo._validar_material(material)

        return PoliticaEmprestimo.PRAZOS[perfil][material]

    @staticmethod
    def calcular_multa(material, dias_atraso):
        PoliticaEmprestimo._validar_material(material)

        if dias_atraso <= 0:
            return 0.0

        taxa = PoliticaEmprestimo.TAXAS_MULTA[material]

        dias_normais = min(dias_atraso, 10)
        dias_agravados = max(dias_atraso - 10, 0)

        return (
            dias_normais * taxa
            + dias_agravados * taxa * 2
        )

    @staticmethod
    def pode_renovar(
        perfil,
        material,
        dias_atraso,
        possui_reserva,
        renovacoes_realizadas
    ):
        PoliticaEmprestimo._validar_perfil(perfil)
        PoliticaEmprestimo._validar_material(material)

        if renovacoes_realizadas < 0:
            raise ValueError(
                "Número de renovações inválido"
            )

        if dias_atraso > 0 or possui_reserva:
            return False

        if material == "MIDIA":
            return False

        if material == "REVISTA":
            return renovacoes_realizadas < 1

        limite = 2 if perfil == "ALUNO" else 3

        return renovacoes_realizadas < limite