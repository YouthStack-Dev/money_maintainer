import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../errors/app_exception.dart';

class SecureStorage {
  SecureStorage({FlutterSecureStorage? storage})
      : _storage = storage ?? const FlutterSecureStorage();

  final FlutterSecureStorage _storage;

  Future<void> write(String key, String value) async {
    try {
      await _storage.write(key: key, value: value);
    } catch (error) {
      throw StorageException('Unable to save secure data: $error');
    }
  }

  Future<String?> read(String key) async {
    try {
      return await _storage.read(key: key);
    } catch (error) {
      throw StorageException('Unable to read secure data: $error');
    }
  }

  Future<void> delete(String key) async {
    try {
      await _storage.delete(key: key);
    } catch (error) {
      throw StorageException('Unable to delete secure data: $error');
    }
  }

  Future<void> writeJson(String key, Map<String, dynamic> value) {
    return write(key, jsonEncode(value));
  }

  Future<Map<String, dynamic>?> readJson(String key) async {
    final value = await read(key);
    if (value == null) return null;

    try {
      return Map<String, dynamic>.from(jsonDecode(value) as Map);
    } catch (error) {
      throw StorageException('Stored data is not valid JSON: $error');
    }
  }
}
