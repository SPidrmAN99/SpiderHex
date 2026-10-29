package com.example.spider_hex_mk_1

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class BleLogBuffer {

    private val _logs = MutableStateFlow<List<String>>(emptyList())
    val logs: StateFlow<List<String>> = _logs

    private val _state = MutableStateFlow(BleState.DISCONNECTED)
    val state: StateFlow<BleState> = _state

    fun append(message: String) {
        _logs.value = _logs.value + message
    }

    fun updateState(newState: BleState) {
        _state.value = newState
    }
}
