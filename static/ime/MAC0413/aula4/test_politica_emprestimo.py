import pytest
from politica_emprestimo import PoliticaEmprestimo

politica_emprestimo = PoliticaEmprestimo()

def test_emprestimo_atrasado_nao_renovado():
    assert False == politica_emprestimo.pode_renovar("ALUNO", "LIVRO", 1, False, 0)
    assert False == politica_emprestimo.pode_renovar("ALUNO", "MIDIA", 1, False, 0)
    assert False == politica_emprestimo.pode_renovar("ALUNO", "REVISTA", 1, False, 0)
    assert False == politica_emprestimo.pode_renovar("PROFESSOR", "LIVRO", 1, False, 0)
    assert False == politica_emprestimo.pode_renovar("PROFESSOR", "MIDIA", 1, False, 0)
    assert False == politica_emprestimo.pode_renovar("PROFESSOR", "REVISTA", 1, False, 0)

def test_possui_reserva_nao_renovado():
    assert False == politica_emprestimo.pode_renovar("ALUNO", "LIVRO", 0, True, 0)
    assert False == politica_emprestimo.pode_renovar("ALUNO", "MIDIA", 0, True, 0)
    assert False == politica_emprestimo.pode_renovar("ALUNO", "REVISTA", 0, True, 0)
    assert False == politica_emprestimo.pode_renovar("PROFESSOR", "LIVRO", 0, True, 0)
    assert False == politica_emprestimo.pode_renovar("PROFESSOR", "MIDIA", 0, True, 0)
    assert False == politica_emprestimo.pode_renovar("PROFESSOR", "REVISTA", 0, True, 0)

def test_midia_nao_renovado():
    assert False == politica_emprestimo.pode_renovar("ALUNO", "MIDIA", 0, False, 0)
    assert False == politica_emprestimo.pode_renovar("PROFESSOR", "MIDIA", 0, False, 0)

def test_revista_nao_renovado():
    assert True == politica_emprestimo.pode_renovar("ALUNO", "REVISTA", 0, False, 0)
    assert False == politica_emprestimo.pode_renovar("ALUNO", "REVISTA", 0, False, 1)
    assert True == politica_emprestimo.pode_renovar("PROFESSOR", "REVISTA", 0, False, 0)
    assert False == politica_emprestimo.pode_renovar("PROFESSOR", "REVISTA", 0, False, 1)

def test_livro_renovado_por_aluno():
    assert True == politica_emprestimo.pode_renovar("ALUNO", "LIVRO", 0, False, 0)
    assert True == politica_emprestimo.pode_renovar("ALUNO", "LIVRO", 0, False, 1)
    assert False == politica_emprestimo.pode_renovar("ALUNO", "LIVRO", 0, False, 2)

def test_livro_renovado_por_professor():
    assert True == politica_emprestimo.pode_renovar("PROFESSOR", "LIVRO", 0, False, 0)
    assert True == politica_emprestimo.pode_renovar("PROFESSOR", "LIVRO", 0, False, 1)
    assert True == politica_emprestimo.pode_renovar("PROFESSOR", "LIVRO", 0, False, 2)
    assert False == politica_emprestimo.pode_renovar("PROFESSOR", "LIVRO", 0, False, 3)

def test_value_error_em_entrada_errada():
    with pytest.raises(ValueError):
        politica_emprestimo.pode_renovar("DOCENTE", "LIVRO", 0, False, 0)

    with pytest.raises(ValueError):
        politica_emprestimo.pode_renovar("PROFESSOR", "ALGUMA COISA", 0, False, 0)

    with pytest.raises(ValueError):
        politica_emprestimo.pode_renovar("FUNCIONARIO", "GIZ", 0, False, 0)

def test_renovacoes_realizadas_negativo():
    with pytest.raises(ValueError):
        politica_emprestimo.pode_renovar("ALUNO", "LIVRO", 0, False, -1)
    with pytest.raises(ValueError):
        politica_emprestimo.pode_renovar("PROFESSOR", "LIVRO", 0, False, -1)

def test_aluno_tem_prazo_correto_emprestimo():
    assert 14 == politica_emprestimo.prazo_emprestimo("ALUNO", "LIVRO")
    assert 7 == politica_emprestimo.prazo_emprestimo("ALUNO", "REVISTA")
    assert 3 == politica_emprestimo.prazo_emprestimo("ALUNO", "MIDIA")

def test_professor_tem_prazo_correto_emprestimo():
    assert 30 == politica_emprestimo.prazo_emprestimo("PROFESSOR", "LIVRO")
    assert 14 == politica_emprestimo.prazo_emprestimo("PROFESSOR", "REVISTA")
    assert 7 == politica_emprestimo.prazo_emprestimo("PROFESSOR", "MIDIA")

def test_multa_zero_sem_atraso():
    assert 0.0 == politica_emprestimo.calcular_multa("LIVRO", 0)
    assert 0.0 == politica_emprestimo.calcular_multa("REVISTA", 0)
    assert 0.0 == politica_emprestimo.calcular_multa("MIDIA", 0)

def test_multa_correta_ate_dez_dias():
    for i in range(1, 11):
        assert 1.0*i == politica_emprestimo.calcular_multa("LIVRO", i)
        assert 1.5*i == politica_emprestimo.calcular_multa("REVISTA", i)
        assert 3.0*i == politica_emprestimo.calcular_multa("MIDIA", i)

def test_multa_correta_apos_dez_dias():
    assert 12.0 == politica_emprestimo.calcular_multa("LIVRO", 11)
    assert 18.0 == politica_emprestimo.calcular_multa("REVISTA", 11)
    assert 36.0 == politica_emprestimo.calcular_multa("MIDIA", 11)

def test_multa_correta_dias_negativos():
    assert 0.0 == politica_emprestimo.calcular_multa("LIVRO", -1)
    assert 0.0 == politica_emprestimo.calcular_multa("REVISTA", -1)
    assert 0.0 == politica_emprestimo.calcular_multa("MIDIA", -1)

