package com.example.lightguard_app

import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    private val channelName = "kr.example.lightguard/local_cases"
    private val storageKey = "lightguard.inspection_outcomes.v1"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, channelName)
            .setMethodCallHandler { call, result ->
                val preferences = getSharedPreferences("lightguard_local", MODE_PRIVATE)
                when (call.method) {
                    "load" -> result.success(preferences.getString(storageKey, "{}"))
                    "save" -> {
                        val raw = call.arguments as? String
                        if (raw == null) result.error("invalid_data", "Case data is missing", null)
                        else if (preferences.edit().putString(storageKey, raw).commit()) result.success(null)
                        else result.error("storage_error", "Could not save local cases", null)
                    }
                    else -> result.notImplemented()
                }
            }
    }
}
