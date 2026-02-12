import 'package:flutter/material.dart';
import 'screens/login_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const AccountEaseMobile());
}

class AccountEaseMobile extends StatelessWidget {
  const AccountEaseMobile({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AccountEase Mobile',
      theme: ThemeData(primarySwatch: Colors.blue),
      debugShowCheckedModeBanner: false,
      home: const LoginScreen(),
    );
  }
}
