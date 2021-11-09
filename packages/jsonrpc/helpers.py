from typing import Callable
from inspect import signature, iscoroutinefunction
from .protocol import JSONRPCSuccessResponse


def unwrap_success_response_message(func):
    func_signature = signature(func)

    async def async_wrapper(*args, **kwargs):
        return JSONRPCSuccessResponse[func_signature.return_annotation](**await func(*args, **kwargs)).result

    return async_wrapper if iscoroutinefunction(func) else \
        lambda *args, **kwargs: JSONRPCSuccessResponse[func_signature.return_annotation](**func(*args, **kwargs)).result