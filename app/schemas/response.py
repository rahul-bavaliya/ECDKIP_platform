from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseEnvelope(BaseModel, Generic[T]):
    success: bool = Field(
        ...,
        description="This is success or failure.",
        examples=[True, False],  # 💡 MUST be a valid boolean
    )
    message: str = Field(
        ...,
        description="The message response from the API endpoint.",
        examples=["Positive message.", "Negative message."],  # 💡
    )
    data: T | None = Field(
        ...,
        description="The data response from the API endpoint.",
        examples=[],  # 💡 MUST be a valid 36-character UUID string
    )
    error: Any | None = Field(
        ...,
        description="The message error from the API endpoint.",
        examples=[],  # 💡 MUST be a valid 36-character UUID string
    )

    @classmethod
    def success_response(
        cls, data: T = None, message: str = "Success"
    ) -> ResponseEnvelope[T]:
        return cls(success=True, message=message, data=data, error=None)

    @classmethod
    def error_response(cls, message: str, error: Any = None) -> ResponseEnvelope[None]:
        return cls(success=False, message=message, data=None, error=error)
