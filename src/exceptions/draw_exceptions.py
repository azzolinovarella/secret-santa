class DrawException(Exception):
    """Exceção base para erros de sorteio."""

    pass


class NoValidCycleException(DrawException):
    """Não foi possível formar um ciclo válido respeitando as restrições."""

    pass


class DrawTimeoutException(DrawException):
    """Sorteio não convergiu dentro do tempo limite."""

    pass


class InvalidRestrictionsException(DrawException):
    """Restrições inválidas ou impossíveis."""

    pass
