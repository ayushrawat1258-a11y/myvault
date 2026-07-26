[app]
title = MyVault
package.name = myvault
package.domain = org.example
source.dir = .
source.include_exts = py,kv,png,jpg,atlas
version = 1.0
requirements = python3,kivy,pyjnius,cryptography,pyasn1,cffi

# Android specifics
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,USE_BIOMETRIC,USE_FINGERPRINT
android.api = 33
android.minapi = 26
android.ndk = 25b
android.archs = arm64-v8a
android.gradle_dependencies = androidx.biometric:biometric:1.1.0
android.enable_androidx = True

orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1
