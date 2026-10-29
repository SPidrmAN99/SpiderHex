# Android SpiderHex controller

Native Android BLE controller for Spider-Hex, built with Kotlin and Jetpack Compose.

## Open and run

Open this directory in Android Studio, let Gradle sync, then run the `app` configuration on an Android device running API 31 or later. Android Studio supplies the local SDK path; `local.properties` is machine-specific and is not tracked.

The app scans for the BLE device `Spider-Hex` and uses the Nordic UART-style service. Its server-ready response parsing matches an earlier firmware iteration. Experimental V5 currently emits a different ready string, so protocol alignment is needed before pairing this app with V5.
