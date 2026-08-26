from central_atendimento import CentralAtendimento, Prioridade, Chamado



def test_id_repetido():
    central = CentralAtendimento()
    
    c1 = Chamado(
        "1234",
        "",
        Prioridade.ALTA
    )
    c2 = Chamado(
        "1234",
        "",
        Prioridade.BAIXA
    )

    assert central.adicionar(c1) == True
    assert central.adicionar(c2) == False

def test_central_vazia():
    central = CentralAtendimento()
    assert central.quantidade_pendentes() == 0
    assert central.atender_proximo() is None
    assert central.pendentes() == []
    assert central.cancelar("123") == False

def test_prioridade_unica():
    central = CentralAtendimento()
    
    c1 = Chamado(
        "1234",
        "",
        Prioridade.ALTA
    )
    c2 = Chamado(
        "5678",
        "",
        Prioridade.ALTA
    )
    
    assert central.adicionar(c1) == True
    assert central.adicionar(c2) == True
    
    assert central.quantidade_pendentes() == 2
    assert central.pendentes() == [c1, c2]
    
    assert central.atender_proximo() == c1
    assert central.atender_proximo() == c2
    assert central.atender_proximo() is None
    assert central.quantidade_pendentes() == 0
    assert central.pendentes() == []
    assert central.cancelar("1234") == False

def test_prioridades_misturadas():
    central = CentralAtendimento()
    
    c1 = Chamado(
        "1234",
        "",
        Prioridade.ALTA
    )
    c2 = Chamado(
        "5678",
        "",
        Prioridade.BAIXA
    )
    c3 = Chamado(
        "9012",
        "",
        Prioridade.MEDIA
    )
    
    assert central.adicionar(c1) == True
    assert central.adicionar(c2) == True
    assert central.adicionar(c3) == True
    
    assert central.quantidade_pendentes() == 3
    assert central.pendentes() == [c1, c3, c2]

    assert central.atender_proximo() == c1
    assert central.atender_proximo() == c3
    assert central.atender_proximo() == c2
    assert central.atender_proximo() is None
    assert central.quantidade_pendentes() == 0
    assert central.pendentes() == []
    assert central.cancelar("1234") == False

def test_cancelar_chamado():
    central = CentralAtendimento()
    
    c1 = Chamado(
        "1234",
        "",
        Prioridade.ALTA
    )
    
    assert central.adicionar(c1) == True
    assert central.quantidade_pendentes() == 1
    assert central.pendentes() == [c1]
    
    assert central.cancelar("1234") == True
    assert central.quantidade_pendentes() == 0
    assert central.pendentes() == []
    assert central.cancelar("1234") == False

def test_adicionar_chamados_apos_atender():
    central = CentralAtendimento()
    
    c1 = Chamado(
        "1234",
        "",
        Prioridade.ALTA
    )
    c2 = Chamado(
        "5678",
        "",
        Prioridade.BAIXA
    )
    
    assert central.adicionar(c1) == True
    assert central.adicionar(c2) == True
    
    assert central.quantidade_pendentes() == 2
    assert central.pendentes() == [c1, c2]
    
    assert central.atender_proximo() == c1
    
    c3 = Chamado(
        "9012",
        "",
        Prioridade.MEDIA
    )
    
    assert central.adicionar(c3) == True
    assert central.quantidade_pendentes() == 2
    assert central.pendentes() == [c3, c2]
    
    assert central.atender_proximo() == c3
    assert central.atender_proximo() == c2
    assert central.atender_proximo() is None
    assert central.quantidade_pendentes() == 0
    assert central.pendentes() == []
    assert central.cancelar("1234") == False

def test_pendentes_nao_modifica_estado():
    central = CentralAtendimento()
    
    c1 = Chamado(
        "1234",
        "",
        Prioridade.ALTA
    )
    c2 = Chamado(
        "5678",
        "",
        Prioridade.BAIXA
    )
    
    assert central.adicionar(c1) == True
    assert central.adicionar(c2) == True
    
    pendentes_initial = central.pendentes()
    assert len(pendentes_initial) == 2
    
    pendentes_after = central.pendentes()
    assert pendentes_after is not pendentes_initial
    assert pendentes_after == pendentes_initial
    
    assert central.quantidade_pendentes() == 2
    assert central.pendentes() == [c1, c2]