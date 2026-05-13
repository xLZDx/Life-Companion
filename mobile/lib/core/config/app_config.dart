/// Compile-time configuration injected via `--dart-define-from-file`.
///
/// Build invocation:
///   flutter run --dart-define-from-file=env/dev.json
///   flutter build apk --dart-define-from-file=env/prod.json
class AppConfig {
  static const String backendBaseUrl = String.fromEnvironment(
    'BACKEND_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000', // Android emulator -> host machine
  );

  static const String appEnv = String.fromEnvironment(
    'APP_ENV',
    defaultValue: 'development',
  );

  static const bool enableCrashReporting = bool.fromEnvironment(
    'ENABLE_CRASH_REPORTING',
    defaultValue: false,
  );
}
