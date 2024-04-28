class CustomError(Exception):
    """Clase para una excepción personalizada."""
    def __init__(self, mensaje):
        self.mensaje = mensaje
        super().__init__(self.mensaje)