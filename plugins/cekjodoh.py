from command import cekjodoh_cmd
from helpers import CMD

__MODULES__ = "Jodoh"
__HELP__ = """<blockquote>Command Help <b>Jodoh</b></blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can check jodoh or compatibility between you and someone else**
        `{0}cekjodoh` (reply/username/name)</blockquote>
<b>   {1}</b>
"""

IS_PRO = True

@CMD.UBOT("cekjodoh")
async def _(client, message):
    return await cekjodoh_cmd(client, message)