from pydantic import BaseModel


class ServiceName(BaseModel):
    name: str

    def __str__(self):
        return self.name
