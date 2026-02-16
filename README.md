# csp-crossword-solver
An AI-based crossword puzzle solver that uses CSP (Constraint Satisfaction Problem) algorithms and features AC-3 and backtracking search with heuristics.

Este projeto implementa um motor de inteligência artificial capaz de resolver palavras-cruzadas, modelando o problema como um Constraint Satisfaction Problem (CSP).

Para encontrar a solução ótima, o motor utiliza:

  **Node Consistency**: Garante que cada palavra preenchida respeita o limite de caracteres da estrutura.

  **Arc Consistency (AC-3)**: Reduz o domínio das variáveis ao garantir que as restrições entre palavras vizinhas (interseções) sejam mutuamente possíveis.

  **Backtracking Search**: Algoritmo de busca em profundidade que tenta preencher o puzzle de forma recursiva.

Heurísticas de Otimização:

  _**MRV (Minimum Remaining Values)**_: Escolhe a variável com menos opções restantes no domínio.

  _**Degree Heuristic**_: Prioriza variáveis com mais conexões (conflitos) com outras.
  
  **_Least Constraining Value_**: Escolhe o valor que menos restringe as opções das variáveis vizinhas.

O solver garante a consistência de arco através da condição:
  $$\forall x \in D_i, \exists y \in D_j \text{ tal que } (x, y) \text{ satisfaz a restrição de interseção}$$
