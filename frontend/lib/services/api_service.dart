import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  final String baseUrl ="http://192.168.18.17:8000/shipments";
  // final String baseUrl = "http://10.0.2.2:8000";


  Future<String> login(String username, String password) async {
    final url = Uri.parse("$baseUrl/api/mobile/login/");

    final response = await http.post(
      url,
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "username": username,
        "password": password,
      }),
    );

    print("STATUS: ${response.statusCode}");
    print("BODY: ${response.body}");

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['token'];
    } else {
      throw Exception("Login failed: ${response.body}");
    }
  }

  Future<List<dynamic>> fetchShipments(String token) async {
    final url = Uri.parse("$baseUrl/api/mobile/shipments/");

    final response = await http.get(
      url,
      headers: {
        "Authorization": "Token $token",
      },
    );

    print("STATUS: ${response.statusCode}");
    print("BODY: ${response.body}");

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Failed to load shipments: ${response.body}");
    }
  }
}
