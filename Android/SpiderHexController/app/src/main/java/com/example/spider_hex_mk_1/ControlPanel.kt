package com.example.spider_hex_mk_1

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun ControlPanel(
    bleState: BleState,
    onCommand: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    val enabled = bleState == BleState.SERVER_IDLE

    Column(
        modifier = modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Button(onClick = { onCommand("1") }, enabled = enabled) { Text("Forward") }
        Button(onClick = { onCommand("2") }, enabled = enabled) { Text("Backward") }
        Button(onClick = { onCommand("3") }, enabled = enabled) { Text("Turn Left") }
        Button(onClick = { onCommand("4") }, enabled = enabled) { Text("Turn Right") }
        Button(onClick = { onCommand("5") }, enabled = enabled) { Text("Reset") }
        Button(
            onClick = { onCommand("bleManager.retry()") },
            colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error)
        ) {
            Text("Retry BLE")
        }


        Spacer(Modifier.height(8.dp))

        Text(
            text = "State: ${bleState.name}",
            style = MaterialTheme.typography.labelMedium
        )
    }
}
