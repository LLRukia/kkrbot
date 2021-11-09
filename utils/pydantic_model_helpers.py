from typing import Optional
from pydantic.main import ModelMetaclass

lower_first_character = lambda str: str[0].lower() + str[1:]


class AllOptional(ModelMetaclass):
    """
    see https://stackoverflow.com/questions/67699451/make-every-fields-as-optional-with-pydantic#answer-67733889
    """

    def __new__(self, name, bases, namespaces, **kwargs):
        annotations = namespaces.get('__annotations__', {})
        for base in bases:
            annotations = {**annotations, **(base.__annotations__ if hasattr(base, '__annotations__') else {})}
        for field in annotations:
            if not field.startswith('__'):
                annotations[field] = Optional[annotations[field]]
        namespaces['__annotations__'] = annotations
        return super().__new__(self, name, bases, namespaces, **kwargs)


class UnderscoreToDashConfig:
    alias_generator = lambda str: str.replace('_', '-')

class UnderscoreToCamelConfig:
    alias_generator = lambda str: lower_first_character(''.join(word.capitalize() for word in str.split('_')))