package com.example.spider_hex_mk_1

import android.Manifest
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothManager
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.example.spider_hex_mk_1.ui.theme.SpiderHexMk1Theme

class MainActivity : ComponentActivity() {

    private lateinit var bluetoothAdapter: BluetoothAdapter
    private lateinit var bleManager: BleUartManager
    private val logBuffer = BleLogBuffer()

    private val blePermissions = arrayOf(
        Manifest.permission.BLUETOOTH_SCAN,
        Manifest.permission.BLUETOOTH_CONNECT,
        Manifest.permission.ACCESS_FINE_LOCATION,
        Manifest.permission.ACCESS_COARSE_LOCATION
    )

    private val permissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { perms ->
            if (perms.values.all { it }) ensureBluetoothEnabled()
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val btManager = getSystemService(BLUETOOTH_SERVICE) as BluetoothManager
        bluetoothAdapter = btManager.adapter

        bleManager = BleUartManager(
            context = this,
            onLog = { logBuffer.append(it) },
            onState = { logBuffer.updateState(it) }
        )

        enableEdgeToEdge()

        setContent {
            SpiderHexMk1Theme {

                val logs by logBuffer.logs.collectAsState()
                val state by logBuffer.state.collectAsState()

                Scaffold { padding ->
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(padding)
                    ) {

                        TerminalView(
                            logs = logs,
                            modifier = Modifier
                                .weight(1f)
                                .fillMaxWidth()
                        )

                        HorizontalDivider()

                        ControlPanel(
                            bleState = state,
                            onCommand = {
                                if (it == "RETRY") {
                                    bleManager.retry()
                                } else {
                                    bleManager.send(it)
                                }
                            },
                            modifier = Modifier.padding(8.dp)
                        )

                    }
                }
            }
        }

        requestBlePermissionsIfNeeded()
    }

    private fun requestBlePermissionsIfNeeded() {
        val missing = blePermissions.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }

        if (missing.isNotEmpty()) {
            permissionLauncher.launch(missing.toTypedArray())
        } else {
            ensureBluetoothEnabled()
        }
    }

    private fun ensureBluetoothEnabled() {
        if (ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.BLUETOOTH_CONNECT
            ) != PackageManager.PERMISSION_GRANTED
        ) return

        if (!bluetoothAdapter.isEnabled) {
            startActivity(Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE))
        }

        bleManager.start()

    }

    override fun onDestroy() {
        bleManager.disconnect()
        super.onDestroy()
    }
}
