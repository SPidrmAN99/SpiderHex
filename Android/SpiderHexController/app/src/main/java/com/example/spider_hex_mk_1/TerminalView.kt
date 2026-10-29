package com.example.spider_hex_mk_1

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp

@Composable
fun TerminalView(
    logs: List<String>,
    modifier: Modifier = Modifier
) {
    val scrollState = rememberScrollState()

    LaunchedEffect(logs.size) {
        scrollState.animateScrollTo(scrollState.maxValue)
    }

    Column(
        modifier = modifier
            .background(Color.Black)
            .verticalScroll(scrollState)
            .padding(8.dp)
    ) {
        logs.forEach { line ->
            Text(
                text = line,
                color = Color(0xFF00FF7F),
                fontFamily = FontFamily.Monospace,
                style = MaterialTheme.typography.bodySmall
            )
        }
    }
}
