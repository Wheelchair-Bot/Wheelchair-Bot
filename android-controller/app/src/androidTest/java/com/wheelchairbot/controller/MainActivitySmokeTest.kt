package com.wheelchairbot.controller

import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Smoke instrumentation test exercised by the Android CI workflow
 * added for audit gap G-18.
 *
 * Real tele-op-handshake tests against the FastAPI WS endpoint land
 * in a follow-up PR once the server image from G-21 is wired into a
 * docker-in-docker step. This test only confirms the build wiring +
 * the test runner config so CI is green on day one.
 */
@RunWith(AndroidJUnit4::class)
class MainActivitySmokeTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun activityLaunches() {
        activityRule.scenario.onActivity { activity ->
            assertEquals(
                "com.wheelchairbot.controller",
                activity.packageName,
            )
        }
    }

    @Test
    fun targetContextPackageIsCorrect() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        assertEquals("com.wheelchairbot.controller", context.packageName)
    }
}
