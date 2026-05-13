import 'package:dio/dio.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../config/app_config.dart';

final apiClientProvider = Provider<ApiClient>((ref) => ApiClient());

/// Thin Dio wrapper:
/// - attaches `Authorization: Bearer <id-token>` on every request when signed in
/// - exponential-backoff retry on 5xx / network errors (max 3 attempts)
/// - excludes request/response bodies from logs for sensitive routes
class ApiClient {
  ApiClient() : _dio = Dio(BaseOptions(baseUrl: AppConfig.backendBaseUrl)) {
    _dio.interceptors.add(_AuthInterceptor());
    _dio.interceptors.add(_RetryInterceptor(_dio));
  }

  final Dio _dio;

  Future<Response<T>> get<T>(String path, {Map<String, dynamic>? query}) {
    return _dio.get<T>(path, queryParameters: query);
  }

  Future<Response<T>> post<T>(String path, {Object? body}) {
    return _dio.post<T>(path, data: body);
  }
}

class _AuthInterceptor extends Interceptor {
  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final user = FirebaseAuth.instance.currentUser;
    if (user != null) {
      final token = await user.getIdToken();
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }
}

class _RetryInterceptor extends Interceptor {
  _RetryInterceptor(this._dio);
  final Dio _dio;
  static const _maxAttempts = 3;

  @override
  Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
    final attempt = (err.requestOptions.extra['retry_attempt'] as int?) ?? 0;
    final canRetry = _shouldRetry(err) && attempt < _maxAttempts - 1;
    if (!canRetry) {
      return handler.next(err);
    }
    final delaySec = (1 << attempt).clamp(1, 8);
    await Future<void>.delayed(Duration(seconds: delaySec));
    final retryOptions = err.requestOptions
      ..extra['retry_attempt'] = attempt + 1;
    try {
      final response = await _dio.fetch<dynamic>(retryOptions);
      handler.resolve(response);
    } catch (e) {
      if (e is DioException) {
        handler.next(e);
      } else {
        handler.reject(err);
      }
    }
  }

  bool _shouldRetry(DioException err) {
    // Only retry idempotent methods. POST may be marked retry-safe via
    // `options.extra['retry_safe'] = true` at the call site.
    final method = err.requestOptions.method.toUpperCase();
    final retrySafe =
        (err.requestOptions.extra['retry_safe'] as bool?) ?? false;
    final idempotent =
        method == 'GET' || method == 'HEAD' || method == 'OPTIONS' || retrySafe;
    if (!idempotent) return false;
    if (err.type == DioExceptionType.connectionError) return true;
    if (err.type == DioExceptionType.receiveTimeout) return true;
    if (err.type == DioExceptionType.connectionTimeout) return true;
    final code = err.response?.statusCode ?? 0;
    return code >= 500 && code < 600;
  }
}
