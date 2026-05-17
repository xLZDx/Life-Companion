import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final authServiceProvider = Provider<AuthService>((ref) => AuthService());

class AuthService {
  final FirebaseAuth? _auth;

  AuthService() : _auth = _tryGetAuth();

  static FirebaseAuth? _tryGetAuth() {
    try {
      return FirebaseAuth.instance;
    } catch (_) {
      // Works with offline dev mode + unit/widget tests where Firebase isn't
      // configured/initialized.
      return null;
    }
  }

  Stream<User?> authStateChanges() {
    final auth = _auth;
    if (auth == null) return const Stream<User?>.empty();
    return auth.authStateChanges();
  }

  User? get currentUser => _auth?.currentUser;

  Future<void> signInAnonymously() async {
    final auth = _auth;
    if (auth == null) {
      throw StateError('FirebaseAuth is not available (Firebase not initialized).');
    }
    await auth.signInAnonymously();
  }

  Future<void> signOut() async {
    final auth = _auth;
    if (auth == null) {
      throw StateError('FirebaseAuth is not available (Firebase not initialized).');
    }
    await auth.signOut();
  }
}
