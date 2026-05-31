"""Unit tests for classify_intent (pure logic, no DB, no HTTP)."""

import pytest
from app.services.llm_client import classify_intent


# ── GREETING ──────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("msg", [
    "hola", "hi", "hello", "hey", "buenas", "bye", "chao", "ok",
    "gracias", "muchas gracias", "de nada", "adiós",
])
def test_single_word_greetings(msg):
    assert classify_intent(msg) == "GREETING"


@pytest.mark.parametrize("msg", [
    "hola buenos días",
    "buenas tardes",
    "buenas noches",
    "muchas gracias de nada",
    "ok vale",
])
def test_multi_word_greetings(msg):
    assert classify_intent(msg) == "GREETING"


def test_greeting_case_insensitive():
    assert classify_intent("HOLA") == "GREETING"
    assert classify_intent("Gracias") == "GREETING"


# ── CONFIRMATION ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize("msg", [
    "ya está",
    "solucionado",
    "resuelto",
    "me ha servido",
    "ya funciona",
    "está funcionando",
])
def test_confirmation_keywords(msg):
    assert classify_intent(msg) == "CONFIRMATION"


# ── NEGATION ─────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("msg", [
    "no funciona",
    "no me funciona",
    "no sirve",
    "sigue sin funcionar",
    "no ha servido",
    "aún no funciona",
])
def test_negation_keywords(msg):
    assert classify_intent(msg) == "NEGATION"


# ── QUESTION (default) ────────────────────────────────────────────────────────

@pytest.mark.parametrize("msg", [
    "¿Cómo hago el alta de un empleado?",
    "¿Cuál es el proceso de baja?",
    "Necesito ayuda con la impresora",
    "El sistema no me deja acceder al módulo de facturación",
    "Explícame el proceso de aprobación de vacaciones",
])
def test_questions_return_question_intent(msg):
    assert classify_intent(msg) == "QUESTION"


def test_question_not_confused_with_greeting():
    # Contains greeting words but is clearly a question
    assert classify_intent("Hola, ¿cómo funciona el proceso de alta?") == "QUESTION"
