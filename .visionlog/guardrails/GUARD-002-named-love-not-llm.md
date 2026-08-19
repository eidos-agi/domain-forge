# GUARD-002 — Named love rubric, not an LLM

The love score is a bounded sum of named factors in `score.py`.

Do not replace it with a model call. Agents already have opinions; this tool exists to make the opinion inspectable. If the rubric is wrong, change the factors and the tests.
