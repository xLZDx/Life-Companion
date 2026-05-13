import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/services/auth_service.dart';

/// Stream of Firebase auth state. Routes redirect based on the latest value.
final authStateProvider = StreamProvider<User?>((ref) {
  final service = ref.watch(authServiceProvider);
  return service.authStateChanges();
});

/// Convenience accessor: current user or null.
final currentUserProvider = Provider<User?>((ref) {
  return ref.watch(authStateProvider).maybeWhen(
        data: (user) => user,
        orElse: () => null,
      );
});
