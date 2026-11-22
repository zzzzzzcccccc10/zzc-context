import asyncio, importlib.util, json, sys, traceback

sys.path.insert(0, "/AstrBot")

from astrbot.core.message.components import Plain
from astrbot.core.message.message_event_result import MessageEventResult, ResultContentType
from astrbot.core.pipeline.result_decorate.stage import ResultDecorateStage
from astrbot.core.pipeline.respond.stage import RespondStage
from astrbot.core.pipeline.context import PipelineContext
import astrbot.core.pipeline.result_decorate.stage as rds
from astrbot.core.star.star_handler import EventType

CFG = {
    "platform_settings": {
        "reply_prefix": "",
        "reply_with_mention": False,
        "reply_with_quote": False,
        "forward_threshold": 100,
        "path_mapping": [],
        "segmented_reply": {
            "enable": False,
            "only_llm_result": False,
            "interval_method": "log",
            "log_base": 2.6,
            "interval": "1.5,3.5",
            "words_count_threshold": 1,
            "split_mode": "regex",
            "regex": "",
            "split_words": [],
            "content_cleanup_rule": "",
        },
    },
    "t2i_word_threshold": 150,
    "t2i_strategy": "local",
    "t2i_active_template": "",
    "t2i": False,
    "provider_tts_settings": {"trigger_probability": 0, "enable": False},
    "content_safety": {"also_use_in_response": False},
    "provider_settings": {"display_reasoning_text": False},
}


class StarInfo:
    activated = True
    name = "harness"
    reserved = False


class FakePMContext:
    async def get_using_tts_provider_async(self, *args, **kwargs):
        return None


class FakePluginManager:
    context = FakePMContext()


class FakeRegistry:
    def __init__(self, handlers):
        self.handlers = handlers

    def get_handlers_by_event_type(self, event_type, only_activated=True, plugins_name=None):
        if event_type == EventType.OnDecoratingResultEvent:
            return self.handlers
        return []


class HandlerWrap:
    handler_module_path = "harness_mod"
    handler_name = "guard"

    def __init__(self, fn):
        self._fn = fn

    async def handler(self, event):
        await self._fn(event)


class FakeEvent:
    def __init__(self, text):
        self._result = MessageEventResult().message(text)
        self._result.result_content_type = ResultContentType.LLM_RESULT
        self._stopped = False
        self._extras = {}
        self.sent = []
        self.plugins_name = ["*"]
        self.unified_msg_origin = "harness"
        self.session_id = "harness"
        self._trace = []

    def get_result(self):
        return self._result

    def is_stopped(self):
        return self._stopped

    def stop_event(self):
        self._stopped = True

    def get_extra(self, key, default=None):
        return self._extras.get(key, default)

    def set_extra(self, key, value):
        self._extras[key] = value

    def get_sender_name(self):
        return "harness"

    def get_sender_id(self):
        return "0"

    def get_platform_id(self):
        return "harness"

    def get_platform_name(self):
        return "harness"

    def _outline_chain(self, chain):
        return "".join(getattr(c, "text", "") for c in chain)

    def clear_result(self):
        self._result = None

    async def send(self, chain):
        comps = getattr(chain, "chain", chain)
        self.sent.append("".join(getattr(c, "text", "") for c in comps))

    async def send_streaming(self, gen, *args, **kwargs):
        self.sent.append("STREAMING")


def load_plugin(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def boom(*args, **kwargs):
    raise RuntimeError("injected")


async def run_case(mod, text, inject=None):
    orig_finalize, orig_marker = mod.finalize_text, mod.has_marker
    if inject == "finalize":
        mod.finalize_text = boom
    elif inject == "marker":
        mod.has_marker = boom
    try:
        return await _run_case(mod, text)
    finally:
        mod.finalize_text = orig_finalize
        mod.has_marker = orig_marker


async def _run_case(mod, text):
    inst = mod.ToolXmlGuard.__new__(mod.ToolXmlGuard)
    inst.cfg = {}
    guard = inst.guard

    old_reg, old_map = rds.star_handlers_registry, rds.star_map
    rds.star_handlers_registry = FakeRegistry([HandlerWrap(guard)])
    rds.star_map = {"harness_mod": StarInfo()}
    try:
        ctx = PipelineContext(astrbot_config=CFG, plugin_manager=FakePluginManager(), astrbot_config_id="h")
        dec = ResultDecorateStage()
        await dec.initialize(ctx)
        resp = RespondStage()
        await resp.initialize(ctx)

        ev = FakeEvent(text)
        try:
            gen = dec.process(ev)
            if hasattr(gen, "__aiter__"):
                async for _ in gen:
                    pass
            else:
                await gen
        except BaseException as e:
            return {"dec_error": type(e).__name__, "detail": str(e), "tb": traceback.format_exc()[-700:], "stopped": ev.is_stopped(), "sent": ev.sent}
        if ev.is_stopped():
            return {"stopped": True, "sent": ev.sent}
        try:
            await resp.process(ev)
        except BaseException as e:
            return {"resp_error": type(e).__name__, "detail": str(e), "tb": traceback.format_exc()[-700:], "stopped": ev.is_stopped(), "sent": ev.sent}
        return {"stopped": ev.is_stopped(), "sent": ev.sent}
    finally:
        rds.star_handlers_registry, rds.star_map = old_reg, old_map


async def main():
    out = {}
    for ver, path in [("v6", "/tmp/rbtest_m2/v6.py"), ("v14", "/tmp/rbtest_m2/v14.py")]:
        try:
            mod = load_plugin(path, f"harness_{ver}")
            out[ver] = {
                "normal": await run_case(mod, "前缀A <｜｜DSML｜｜ calls> 后缀B"),
                "finalize_error": await run_case(mod, "前缀A <｜｜DSML｜｜ calls> 后缀B", inject="finalize"),
                "marker_error": await run_case(mod, "前缀A <｜｜DSML｜｜ calls> 后缀B", inject="marker"),
                "empty_after_clean": await run_case(mod, "<｜｜DSML｜｜ calls>"),
            }
        except BaseException as e:
            out[ver] = {"fatal": type(e).__name__, "detail": str(e), "tb": traceback.format_exc()[-1500:]}
    print(json.dumps(out, ensure_ascii=False, indent=2))


asyncio.run(main())
