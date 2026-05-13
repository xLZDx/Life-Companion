import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/router/router.dart';
import 'core/theme/app_theme.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Firebase init is best-effort in dev (no config = run in offline mode);
  // production builds inject firebase_options.dart via flutterfire CLI.
  try {
    await Firebase.initializeApp();
  } catch (_) {
    // Run without Firebase in dev when no config present.
  }
  runApp(const ProviderScope(child: LifeCompanionApp()));
}

class LifeCompanionApp extends ConsumerWidget {
  const LifeCompanionApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);
    return MaterialApp.router(
      title: 'Life Companion',
      theme: AppTheme.light(),
      darkTheme: AppTheme.dark(),
      themeMode: ThemeMode.system,
      routerConfig: router,
      debugShowCheckedModeBanner: false,
    );
  }
}
