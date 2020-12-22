#!/usr/bin/python
import asyncio
from collections import defaultdict
from pathlib import Path

from mopidy_async_client import MopidyClient

_BASE = """
class _BaseController:
    def __init__(self, request_handler):
        self._request_handler_ = request_handler

    async def mopidy_request(self, method, **kwargs):
        return await self._request_handler_(method, **kwargs)

"""


def get_controllers(description):
    def get_controller_code():
        functions_ = "\n".join(functions)
        return f'''
class {controller_name.capitalize()}Controller(_BaseController):
{functions_}

    '''

    controllers = defaultdict(list)

    for endpoint_name, method_info in description.items():
        *_, controller_name, method_name = endpoint_name.split('.')
        func_code = get_func_code(endpoint_name, method_name, method_info)
        controllers[controller_name].append(func_code)

    result = ""
    for controller_name, functions in controllers.items():
        result += get_controller_code()
    return result


def get_func_code(endpoint_name, method_name, method_info):
    def get_arg(param):
        return ("{name}={default}".format(**param) if 'default' in param else param['name']) + ', '

    def get_usage(param):
        return "{name}={name}, ".format(**param)

    def get_deprecated():
        for el in docs.split(".. deprecated::")[1:]:
            _, desc, *_ = el.split("\n")
            yield f"\n    # DEPRECATED {desc.strip()}"

    docs = method_info['description'].replace("\n\n", "\n").replace("\n", "\n        ")
    args = "".join([get_arg(p) for p in method_info['params']])
    usage = "".join([get_usage(p) for p in method_info['params']])
    deprecated = "".join(get_deprecated())

    return f'''{deprecated}
    async def {method_name}(self, {args}**options):
        """{docs}"""
        return await self.mopidy_request('{endpoint_name}', {usage}**options)'''


async def main():
    async with MopidyClient() as client:
        description = await client.core.describe()

    description['core.describe'] = {'description': "Get all endpoints", 'params': []}

    code = _BASE + get_controllers(description)
    path = Path(__file__).parent / "mopidy_async_client" / "mopidy_api.py"
    with open(path, 'w') as file:
        file.write(code)


if __name__ == '__main__':
    asyncio.run(main())
