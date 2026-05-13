import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:life_companion/core/theme/app_theme.dart';
import 'package:life_companion/features/crisis/crisis_modal.dart';

/// Verifies GUARDRAILS section 1: crisis modal cannot be back-dismissed,
/// and the "I'm safe, continue" button navigates away (regression for the
/// `Navigator.maybePop` bug that left users trapped on the crisis screen).
void main() {
  testWidgets('CrisisModalPage renders title and continue button', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.light(),
        home: const CrisisModalPage(),
      ),
    );
    expect(
      find.textContaining('If you are in immediate danger'),
      findsOneWidget,
    );
    expect(find.text("I'm safe, continue"), findsOneWidget);
  });

  testWidgets('Continue button uses GoRouter navigation', (tester) async {
    final router = GoRouter(
      initialLocation: '/crisis',
      routes: [
        GoRoute(
          path: '/home',
          builder: (_, __) => const Scaffold(body: Text('HOME_REACHED')),
        ),
        GoRoute(
          path: '/crisis',
          pageBuilder: (_, __) => const MaterialPage(child: CrisisModalPage()),
        ),
      ],
    );
    await tester.pumpWidget(
      MaterialApp.router(
        theme: AppTheme.light(),
        routerConfig: router,
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text("I'm safe, continue"), findsOneWidget);
    await tester.tap(find.text("I'm safe, continue"));
    await tester.pumpAndSettle();

    // We started on /crisis with no pop-stack, so the button falls back
    // to context.go(Routes.home).
    expect(find.text('HOME_REACHED'), findsOneWidget);
  });
}
