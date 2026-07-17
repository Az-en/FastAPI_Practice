
class ApplicationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
    

class NotFoundError(ApplicationError):
    """
    args:
    resource: Represents the name of the entity/resource that is missing
    **kwargs: contains unique identifiers of that resource
    """
    def __init__(self, resource: str,**kwargs):
        self.resource = resource
        self.identifiers = kwargs
        if self.identifiers:
            id_string = ", ".join(f"{key} = {value}" for key,value in self.identifiers.items())
            message = f"{resource} not found with {id_string}"
        else:
            message = f"{resource} not found"
        
        super.__init__(message)

class ConflictError(ApplicationError):
    pass


class PermissionDeniedError(ApplicationError):
    pass