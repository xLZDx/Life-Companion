import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/auth/auth_providers.dart';
import '../../features/auth/auth_screen.dart';
import '../../features/crisis/crisis_modal.dart';
import '../../features/home/home_screen.dart';
import 'routes.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final auth = ref.watch(authStateProvider);
  return GoRouter(
    initialLocation: Routes.splash,
    redirect: (context, state) {
      final isSignedIn = auth.maybeWhen(
        data: (user) => user != null,
        orElse: () => false,
      );
      final goingToAuth = state.matchedLocation == Routes.auth;
      final goingToCrisis = state.matchedLocation == Routes.crisis;
      if (goingToCrisis) return null; // crisis route is always reachable
      if (!isSignedIn && !goingToAuth) return Routes.auth;
      if (isSignedIn && goingToAuth) return Routes.home;
      return null;
    },
    routes: [
      GoRoute(
        path: Routes.splash,
        redirect: (_, __) => Routes.home,
      ),
      GoRoute(
        path: Routes.auth,
        builder: (_, __) => const AuthScreen(),
      ),
      GoRoute(
        path: Routes.home,
        builder: (_, __) => const HomeScreen(),
      ),
      GoRoute(
        path: Routes.crisis,
        pageBuilder: (_, __) => const CrisisModalPage(),
      ),
    ],
  );
});
