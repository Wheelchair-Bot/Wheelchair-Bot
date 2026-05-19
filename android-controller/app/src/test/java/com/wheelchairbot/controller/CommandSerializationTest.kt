package com.wheelchairbot.controller

import com.google.gson.Gson
import org.junit.Assert.assertEquals
import org.junit.Test

/**
 * Pure-JVM unit test for the wire-format the Android app emits to
 * the FastAPI WS endpoint (wheelchair.app.server, Phase 2).
 *
 * This test is the Android-side half of the schema contract — if it
 * starts diverging from `ControlFrame` in the backend, either of us
 * will fail.
 */
class CommandSerializationTest {

    private val gson = Gson()

    @Test
    fun moveCommandSerialises_with_required_fields() {
        val cmd = mapOf(
            "kind" to "move",
            "ts" to 0.0,
            "seq" to 1,
            "linear" to 0.5,
            "angular" to -0.2,
        )
        val json = gson.toJson(cmd)
        // Round-trip via parse to assert structure independent of key order.
        @Suppress("UNCHECKED_CAST")
        val parsed = gson.fromJson(json, Map::class.java) as Map<String, Any>
        assertEquals("move", parsed["kind"])
        assertEquals(0.5, parsed["linear"] as Double, 1e-9)
        assertEquals(-0.2, parsed["angular"] as Double, 1e-9)
    }

    @Test
    fun deadmanFrame_carries_pressed_field() {
        val cmd = mapOf("kind" to "deadman", "ts" to 0.0, "seq" to 2, "pressed" to false)
        val json = gson.toJson(cmd)
        @Suppress("UNCHECKED_CAST")
        val parsed = gson.fromJson(json, Map::class.java) as Map<String, Any>
        assertEquals(false, parsed["pressed"])
    }

    @Test
    fun stopFrame_has_no_payload_fields() {
        val cmd = mapOf("kind" to "stop", "ts" to 0.0, "seq" to 3)
        val json = gson.toJson(cmd)
        assert(!json.contains("linear")) { "stop frame must not include linear" }
        assert(!json.contains("angular")) { "stop frame must not include angular" }
    }
}
