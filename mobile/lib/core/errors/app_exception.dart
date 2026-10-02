sealed class AppException implements Exception {
  const AppException(this.message);

  final String message;

  @override
  String toString() => message;
}

final class NetworkException extends AppException {
  const NetworkException(super.message);
}

final class ApiException extends AppException {
  const ApiException(
    super.message, {
    this.statusCode,
    this.code,
  });

  final int? statusCode;
  final String? code;
}

final class StorageException extends AppException {
  const StorageException(super.message);
}
