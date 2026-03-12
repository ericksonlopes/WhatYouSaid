# Instruções do Copilot / Colaboradores

Este arquivo orienta o GitHub Copilot, ferramentas automatizadas e colaboradores sobre convenções, comandos e boas práticas para trabalhar neste repositório "what-you-said".

## Visão geral
- Linguagem: Python
- Estrutura principal:
  - `src/` — código-fonte
  - `tests/` — testes automatizados
  - `alembic/`, `alembic.ini` — migrações de banco (Alembic)
  - `main.py` — ponto de entrada
  - `pyproject.toml`, `mypy.ini`, `pytest.ini` — configurações de ferramenta

## Setup local
1. Criar e ativar um ambiente virtual (Windows):
   - python -m venv .venv
   - .\.venv\Scripts\Activate
2. Instalar dependências:
   - Exemplo (uv): `uv install` e `uv sync`
   - Instalar localmente em modo editável: `python -m pip install -e .`
3. Conferir configurações em `pyproject.toml` e `mypy.ini` antes de rodar verificações.

## Executar
- Entrada principal (exemplo):
  - `python main.py`  (ou `python -m main` dependendo do entrypoint)
- Para tarefas específicas, consulte `README.md`.

## Testes e qualidade
- Rodar testes: `pytest -q` ou `python -m pytest`
- Checagem de tipos: `mypy src tests`
- Formatação: `black .` e `isort .` (quando aplicável)
- Sempre executar testes e checagens antes de commitar.

## Migrações de banco (Alembic)
- Aplicar migrações: `alembic upgrade head`
- Criar nova revisão (autogerada):
  - `alembic revision --autogenerate -m "descrição"`
- Revisar o arquivo de migration antes de aplicar em produção.

## Regras para alterações (diretrizes do Copilot / contribuidores)
- Fazer alterações cirúrgicas e focadas; não modifique código não relacionado.
- Para mudanças que afetam design, API ou múltiplos arquivos, criar um plano antes de implementar (veja seção "Planejamento").
- Atualizar documentação e testes quando alterar comportamento público.
- Não commitar segredos, credenciais ou arquivos binários grandes.
- Verificar `mypy` e `pytest` após mudanças.

## Planejamento e tarefas (fluxo recomendado)
- Mudanças complexas: criar um `plan.md` no diretório de sessão (ferramentas automatizadas podem usar um caminho de sessão) descrevendo problema, abordagem e tarefas.
- Usar a tabela `todos` (quando disponível) para rastrear tarefas maiores.

## Commits e PRs
- Mensagem de commit: assunto curto, linha em branco, corpo explicativo quando necessário.
- Trailler de commit obrigatório (INCLUIR em todos os commits):

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>

- Abrir PRs pequenas e específicas. Rodar CI localmente quando possível.

## Boas práticas para o Copilot CLI / Assistente Automatizado
- Preferir alterações pequenas, testáveis e revertíveis.
- Usar `create` / `edit` para alterações de arquivo (evitar criar arquivos temporários no repositório).
- Antes de rodar comandos, verificar o contexto do projeto (`pyproject.toml`, `README.md`).
- Em ambientes Windows, usar caminhos com backslashes `\\`.

## Arquivos importantes
- `pyproject.toml` — declara dependências e configurações de tooling
- `README.md` — visão do projeto e instruções para usuários
- `mypy.ini`, `pytest.ini` — configurações de qualidade
- `alembic/` — histórico de migrações

## Checklist antes de commitar
- [ ] Todos os testes passam
- [ ] `mypy` não apresenta erros relevantes
- [ ] Código formatado (`black`, `isort`)
- [ ] Documentação atualizada (se aplicável)
- [ ] Mensagem de commit contém o trailer obrigatório

## Contato
- Para dúvidas sobre arquitetura ou decisões, abra uma issue no repositório.

---

Essas instruções foram escritas para facilitar contribuições seguras e consistentes. Ajuste conforme necessário ao evoluir o projeto.
