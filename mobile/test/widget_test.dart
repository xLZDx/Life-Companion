import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:life_companion/core/theme/app_theme.dart';
import 'package:life_companion/features/auth/auth_screen.dart';

void main() {
  testWidgets('Auth screen displays Life Companion title and sign-in button',
      (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          theme: AppTheme.light(),
          home: const AuthScreen(),
        ),
      ),
    );
    expect(find.text('Life Companion'), findsOneWidget);
    expect(find.text('Continue (anonymous)'), findsOneWidget);
  });
}
