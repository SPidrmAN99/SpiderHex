@file:Suppress(
    "MissingPermission",
    "DEPRECATION",
    "SpellCheckingInspection"
)

package com.example.spider_hex_mk_1

import android.bluetooth.*
import android.bluetooth.le.*
import android.content.Context
import android.os.Handler
import android.os.Looper
import java.nio.charset.Charset
import java.util.UUID

class BleUartManager(
    private val context: Context,
    private val onState: (BleState) -> Unit,
    private val onLog: (String) -> Unit
) {

    companion object {
        private const val DEVICE_NAME = "Spider-Hex"

        private val UART_SERVICE_UUID =
            UUID.fromString("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
        private val UART_RX_UUID =
            UUID.fromString("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
        private val UART_TX_UUID =
            UUID.fromString("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")
        private val CCCD_UUID =
            UUID.fromString("00002902-0000-1000-8000-00805F9B34FB")
    }

    private val bluetoothManager =
        context.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
    private val adapter = bluetoothManager.adapter
    private val scanner = adapter.bluetoothLeScanner
    private val handler = Handler(Looper.getMainLooper())

    private var gatt: BluetoothGatt? = null
    private var rxChar: BluetoothGattCharacteristic? = null
    private var txChar: BluetoothGattCharacteristic? = null

    private var scanAttempt = 0
    private var discoverAttempts = 0

    private enum class BlePhase {
        IDLE,
        CONNECTED,
        SUBSCRIBING,
        SUBSCRIBED,
        HANDSHAKE_SENT,
        WAITING_FOR_SERVER,
        READY
    }

    private var phase = BlePhase.IDLE


    /* ===================== ENTRY ===================== */

    fun start() {
        if (!adapter.isEnabled) {
            onLog("[BLE] Waiting for Bluetooth...")
            onState(BleState.DISCONNECTED)
            return
        }

        onLog("[BLE] Bluetooth ON, warming up...")
        handler.postDelayed({ startScan() }, 2000)
    }

    /* ===================== SCAN ===================== */

    private fun startScan() {
        scanAttempt++
        onLog("[BLE] Scan started (attempt $scanAttempt)")
        onState(BleState.SCANNING)

        scanner.startScan(scanCallback)

        handler.postDelayed({
            if (gatt == null) {
                scanner.stopScan(scanCallback)
                onLog("[BLE] Scan timeout, retrying...")
                handler.postDelayed({ startScan() }, 2000)
            }
        }, 60_000)
    }

    private val scanCallback = object : ScanCallback() {

        override fun onScanResult(type: Int, result: ScanResult) {
            val device = result.device ?: return

            if (device.name == DEVICE_NAME) {
                handler.removeCallbacksAndMessages(null)
                scanner.stopScan(this)
                onLog("[BLE] Found Spider-Hex, connecting...")
                connect(device)
            }
        }
    }

    /* ===================== CONNECT ===================== */

    private fun connect(device: BluetoothDevice) {
        onState(BleState.CONNECTED)
        gatt = device.connectGatt(context, false, gattCallback)
    }

    private val gattCallback = object : BluetoothGattCallback() {

        override fun onConnectionStateChange(
            gatt: BluetoothGatt,
            status: Int,
            newState: Int
        ) {
            when (newState) {
                BluetoothProfile.STATE_CONNECTED -> {
                    phase = BlePhase.CONNECTED
                    onLog("[BLE] Connected")
                    discoverAttempts = 0
                    gatt.discoverServices()
                }

                BluetoothProfile.STATE_DISCONNECTED -> {
                    onLog("[BLE] Disconnected, retrying...")
                    cleanup()
                    handler.postDelayed({ startScan() }, 2000)
                }
            }
        }

        override fun onServicesDiscovered(gatt: BluetoothGatt, status: Int) {
            val service = gatt.getService(UART_SERVICE_UUID)

            if (service == null && discoverAttempts < 5) {
                discoverAttempts++
                onLog("[BLE] Service discovery retry ($discoverAttempts)")
                gatt.discoverServices()
                return
            }

            if (service == null) {
                onLog("[BLE] UART service not found, restarting scan")
                cleanup()
                startScan()
                return
            }

            rxChar = service.getCharacteristic(UART_RX_UUID)
            txChar = service.getCharacteristic(UART_TX_UUID)

            phase = BlePhase.SUBSCRIBING
            onLog("[BLE] Subscribing to notifications...")
            enableNotifications()

        }

        override fun onDescriptorWrite(
            gatt: BluetoothGatt,
            descriptor: BluetoothGattDescriptor,
            status: Int
        ) {
            if (descriptor.uuid == CCCD_UUID && status == BluetoothGatt.GATT_SUCCESS) {
                phase = BlePhase.SUBSCRIBED
                onLog("[BLE] Notifications subscribed")

                onLog("[BLE] Sending CLIENT_READY")
                sendClientReady()
            }
        }

        override fun onCharacteristicWrite(
            gatt: BluetoothGatt,
            characteristic: BluetoothGattCharacteristic,
            status: Int
        ) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                onLog("[BLE] Message delivered to server")
            }
        }



        @Suppress("DEPRECATION")
        @Deprecated("Required for BLE notifications on Android < 13")
        override fun onCharacteristicChanged(
            gatt: BluetoothGatt,
            characteristic: BluetoothGattCharacteristic
        )
        {
            val msg = characteristic.value
                ?.toString(Charset.defaultCharset())
                ?.trim()
                ?: return

            if (phase == BlePhase.WAITING_FOR_SERVER) {
                onLog("[BLE] Server response received")
            }


            onLog(msg)

            when {
                msg.contains("SERVER_READY") -> {
                    phase = BlePhase.READY
                    onState(BleState.SERVER_READY)
                }
                msg.contains("SERVER_IDLE") -> {
                    phase = BlePhase.READY
                    onState(BleState.SERVER_IDLE)
                }
                msg.contains("SERVER_BUSY") -> {
                    onState(BleState.SERVER_BUSY)
                }
            }

        }
    }

    /* ===================== NOTIFY ===================== */

    private fun enableNotifications() {
        val tx = txChar ?: return

        gatt?.setCharacteristicNotification(tx, true)
        val cccd = tx.getDescriptor(CCCD_UUID)
        cccd.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
        gatt?.writeDescriptor(cccd)

        onLog("[BLE] Notifications enabled")
        onLog("[BLE] Sending CLIENT_READY")
        send("CLIENT_READY")
    }

    private fun sendClientReady() {
        if (phase != BlePhase.SUBSCRIBED) return

        phase = BlePhase.HANDSHAKE_SENT
        rxChar?.value = "CLIENT_READY\n".toByteArray()
        gatt?.writeCharacteristic(rxChar)

        onLog("[BLE] CLIENT_READY sent, waiting for server response...")
        phase = BlePhase.WAITING_FOR_SERVER
    }



    /* ===================== SEND ===================== */

    fun send(command: String) {

        if (phase != BlePhase.READY) {
            onLog("[BLE] Command blocked — server not ready")
            return
        }


        val rx = rxChar ?: return
        rx.value = "$command\n".toByteArray(Charsets.UTF_8)
        gatt?.writeCharacteristic(rx)
        onLog("[CMD] $command")
    }

    /* ===================== CLEANUP ===================== */

    fun disconnect() {
        cleanup()
    }

    private fun cleanup() {
        gatt?.close()
        gatt = null
        rxChar = null
        txChar = null
        onState(BleState.DISCONNECTED)
    }

    fun retry() {
        onLog("[BLE] Manual retry initiated")

        scanner.stopScan(scanCallback)
        handler.removeCallbacksAndMessages(null)

        phase = BlePhase.IDLE
        cleanup()

        handler.postDelayed({ start() }, 1500)
    }


}
