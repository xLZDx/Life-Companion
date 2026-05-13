import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../core/router/routes.dart';
import '../../core/theme/app_colors.dart';

/// Crisis modal. Phase 2 wires the real hotline list + dial intent;
/// Phase 1 ships the structural scaffold so the GoRouter route exists.
///
/// GUARDRAILS:
/// - PopScope(canPop: false) - hardware back / iOS swipe-back disabled
/// - Requires explicit "I'm safe, continue" tap before resuming
/// - Uses GoRouter context.pop / context.go to guarantee navigation works
/// - No paywall, no auth requirement
class CrisisModalPage extends StatelessWidget {
  const CrisisModalPage({super.key});

  @override
  Widget build(BuildContext context) {
    final semantic = Theme.of(context).extension<AppSemanticColors>();
    final crisisColor = semantic?.crisis ?? AppColors.crisisRed;
    return PopScope(
      canPop: false,
      child: Scaffold(
        backgroundColor: crisisColor.withValues(alpha: 0.05),
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Icon(Icons.support, color: crisisColor, size: 56),
                const SizedBox(height: 16),
                Text(
                  'If you are in immediate danger, please call your local hotline now.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: crisisColor,
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 24),
                const Text(
                  'This app cannot help in an emergency.',
                  textAlign: TextAlign.center,
                ),
                const Spacer(),
                FilledButton(
                  onPressed: () {
                    if (context.canPop()) {
                      context.pop();
                    } else {
                      context.go(Routes.home);
                    }
                  },
                  child: const Text("I'm safe, continue"),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
