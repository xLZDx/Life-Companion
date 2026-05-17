import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/auth/auth_providers.dart';
import '../../features/auth/auth_screen.dart';
import '../../features/crisis/crisis_modal.dart';
import '../../features/home/home_screen.dart';
import 'routes.dart';

/// Bridges Riverpod's authStateProvider into GoRouter's refreshListenable so
/// the router instance itself is stable across auth state changes - we just
/// re-run `redirect` on each tick instead of rebuilding the whole router.
class _AuthRefreshNotifier extends ChangeNotifier {
  _AuthRefreshNotifier(Ref ref) {
    _sub = ref.listen(
      authStateProvider,
      (_, __) => notifyListeners(),
      fireImmediately: false,
    );
  }
  // ignore: unused_field
  late final ProviderSubscription<Object?> _sub;
}

final routerProvider = Provider<GoRouter>((ref) {
  final notifier = _AuthRefreshNotifier(ref);
  ref.onDispose(notifier.dispose);

  return GoRouter(
    initialLocation: Routes.splash,
    refreshListenable: notifier,
    redirect: (context, state) {
      // ref.read here - does NOT create a watch dependency.
      final auth = ref.read(authStateProvider);
      // Loading: don't bounce - leave user where they are.
      if (auth.isLoading) return null;
      final isSignedIn = auth.maybeWhen(
        data: (user) => user != null,
        orElse: () => false,
      );
      final goingToCrisis = state.matchedLocation == Routes.crisis;
      if (goingToCrisis) return null; // crisis route always reachable
      final goingToAuth = state.matchedLocation == Routes.auth;
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
        builder: (_, __) => const CrisisModalPage(),
      ),
    ],
  );
});
