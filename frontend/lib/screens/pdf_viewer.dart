// pdf_viewer.dart

import 'dart:io';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_pdfview/flutter_pdfview.dart';
import 'package:path_provider/path_provider.dart';
import 'package:http/http.dart' as http;

class FullScreenPdfViewer extends StatefulWidget {
  final String url;
  const FullScreenPdfViewer({super.key, required this.url});

  @override
  _FullScreenPdfViewerState createState() => _FullScreenPdfViewerState();
}

class _FullScreenPdfViewerState extends State<FullScreenPdfViewer> {
  late Future<File> _pdfFileFuture;
  int _totalPages = 0;
  int _currentPage = 0;
  bool _isReady = false;
  String _errorMessage = '';

  @override
  void initState() {
    super.initState();
    _pdfFileFuture = _loadPdfFromNetwork(widget.url);
  }

  Future<File> _loadPdfFromNetwork(String url) async {
    try {
      if (url.isEmpty) throw Exception("PDF URL is empty");

      Uri uri = Uri.parse(url.trim());
      final response = await http.get(uri);

      if (response.statusCode != 200 || response.bodyBytes.isEmpty) {
        throw Exception("Failed to download PDF: Status ${response.statusCode}");
      }

      final dir = await getTemporaryDirectory();
      final fileName = '${DateTime.now().millisecondsSinceEpoch}.pdf';
      final file = File('${dir.path}/$fileName');

      await file.writeAsBytes(response.bodyBytes);
      return file;
    } catch (e) {
      setState(() => _errorMessage = e.toString());
      rethrow;
    }
  }

  @override
  Widget build(BuildContext context) {
    const Color brandPurple = Color(0xFF4e2780);
    const Color brandRed = Colors.red;

    return Scaffold(
      backgroundColor: const Color(0xFF121212), // Dark background for focus
      body: Stack(
        children: [
          // 1. PDF VIEW AREA
          FutureBuilder<File>(
            future: _pdfFileFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return _buildLoader(brandPurple);
              }

              if (snapshot.hasError || snapshot.data == null) {
                return _buildErrorState(brandRed);
              }

              return PDFView(
                filePath: snapshot.data!.path,
                enableSwipe: true,
                swipeHorizontal: false,
                autoSpacing: true,
                pageFling: true,
                onRender: (pages) => setState(() {
                  _totalPages = pages ?? 0;
                  _isReady = true;
                }),
                onPageChanged: (page, _) => setState(() => _currentPage = page ?? 0),
                onError: (error) => setState(() => _errorMessage = error.toString()),
              );
            },
          ),

          // 2. FLOATING TOP BAR (Glassmorphism effect)
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: ClipRect(
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
                child: Container(
                  padding: EdgeInsets.only(top: MediaQuery.of(context).padding.top + 10, bottom: 15),
                  color: brandPurple.withOpacity(0.85),
                  child: Row(
                    children: [
                      IconButton(
                        icon: const Icon(Icons.arrow_back_ios_new, color: Colors.white, size: 20),
                        onPressed: () => Navigator.pop(context),
                      ),
                      const Expanded(
                        child: Text(
                          "Document Preview",
                          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 20),
                        ),
                      ),
                      if (_isReady)
                        Padding(
                          padding: const EdgeInsets.only(right: 20),
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Text(
                              "${_currentPage + 1} / $_totalPages",
                              style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
            ),
          ),

          // 3. BOTTOM FLOATING ACTION (Only show when ready)
          
        ],
      ),
    );
  }

  // --- UI HELPER WIDGETS ---

  Widget _buildLoader(Color color) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          CircularProgressIndicator(valueColor: AlwaysStoppedAnimation<Color>(color)),
          const SizedBox(height: 20),
          const Text("Fetching document securely...", style: TextStyle(color: Colors.white70, fontSize: 14)),
        ],
      ),
    );
  }

  Widget _buildErrorState(Color errorColor) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(30.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.error_outline_rounded, color: errorColor, size: 60),
            const SizedBox(height: 16),
            Text(
              "Unable to load PDF",
              style: TextStyle(color: errorColor, fontWeight: FontWeight.bold, fontSize: 18),
            ),
            const SizedBox(height: 8),
            Text(
              _errorMessage,
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.white54, fontSize: 13),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: Colors.white10),
              onPressed: () => setState(() {
                _errorMessage = '';
                _pdfFileFuture = _loadPdfFromNetwork(widget.url);
              }),
              child: const Text("Retry", style: TextStyle(color: Colors.white)),
            )
          ],
        ),
      ),
    );
  }
}