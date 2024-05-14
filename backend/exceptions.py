class CustomError(Exception):
    """Clase para una excepción personalizada."""
    def __init__(self, mensaje):
        self.mensaje = mensaje
        super().__init__(self.mensaje)

    def __dict__(self):
        """
        This method defines how the CustomError object is represented as a dictionary.
        This allows Flask's jsonify to serialize the error information to JSON.
        """
        return {"message": self.mensaje, "error_type": "CustomError"}  # Return a dictionary