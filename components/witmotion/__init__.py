from esphome import automation
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import ble_client, time
from esphome.const import (
    CONF_ID,
    CONF_ON_UPDATE,
    CONF_TIME_ID,
    CONF_TRIGGER_ID,
)

CODEOWNERS = ["@jpmv27"]
DEPENDENCIES = ["ble_client"]
MULTI_CONF = True

witmotion_ns = cg.esphome_ns.namespace("witmotion")
WitMotion = witmotion_ns.class_("WitMotion", cg.Component, ble_client.BLEClientNode)

# Triggers
UpdateTrigger = witmotion_ns.class_("UpdateTrigger", automation.Trigger.template())
CONF_TRIGGER_EVERY = "trigger_every"

CONF_WITMOTION_ID = "witmotion_id"

CONF_UPDATE_RATE = "update_rate"

WitMotionUpdateRate = witmotion_ns.enum("RateArg")
UPDATE_RATES = {
    "0.2 Hz": WitMotionUpdateRate.RATE_0_2HZ,
    "0.5 Hz": WitMotionUpdateRate.RATE_0_5HZ,
    "1 Hz":   WitMotionUpdateRate.RATE_1HZ,
    "2 Hz":   WitMotionUpdateRate.RATE_2HZ,
    "5 Hz":   WitMotionUpdateRate.RATE_5HZ,
    "10 Hz":  WitMotionUpdateRate.RATE_10HZ,
    "20 Hz":  WitMotionUpdateRate.RATE_20HZ,
    "50 Hz":  WitMotionUpdateRate.RATE_50HZ,
    "100 Hz": WitMotionUpdateRate.RATE_100HZ,
    "200 Hz": WitMotionUpdateRate.RATE_200HZ,
}

CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(WitMotion),
            cv.Optional(CONF_UPDATE_RATE, default="0.2 Hz"): cv.enum(UPDATE_RATES, upper=False),
            cv.Optional(CONF_TRIGGER_EVERY, default=1): cv.positive_not_null_int,
            cv.Optional(CONF_TIME_ID): cv.use_id(time.RealTimeClock),
            cv.Optional(CONF_ON_UPDATE): automation.validate_automation(
                {
                    cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(UpdateTrigger),
                }
            ),
        }
    )
    .extend(cv.COMPONENT_SCHEMA)
    .extend(ble_client.BLE_CLIENT_SCHEMA)
)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await ble_client.register_ble_node(var, config)

    if CONF_UPDATE_RATE in config:
        cg.add(var.set_update_rate(config[CONF_UPDATE_RATE]))

    if CONF_TRIGGER_EVERY in config:
        cg.add(var.set_trigger_every(config[CONF_TRIGGER_EVERY]))

    if time_id := config.get(CONF_TIME_ID):
        time_ = await cg.get_variable(time_id)
        cg.add(var.set_time_id(time_))

    for conf in config.get(CONF_ON_UPDATE, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID])
        cg.add(var.register_onupdate_trigger(trigger))
        await automation.build_automation(trigger, [], conf)
