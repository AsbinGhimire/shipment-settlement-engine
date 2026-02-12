// shipment_list_screen.dart

import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'login_screen.dart';
import '/screens/shipment_detail_screen.dart';
import '/models/shipment_record.dart';
import 'package:intl/intl.dart';

// Styling constants
const Color primaryColor = Color(0xFF4e2780); // Deep Violet
const Color accentColor = Color(0xFFFFDE59); // Bright Yellow/Gold
const Color cardBackgroundColor = Color(0xFFffffff); // Pure White for cards
const Color successColor = Color(0xFF1a936f); // Success Green for amounts

class ShipmentListScreen extends StatefulWidget {
  final String token;

  const ShipmentListScreen({super.key, required this.token});

  @override
  State<ShipmentListScreen> createState() => _ShipmentListScreenState();
}

class _ShipmentListScreenState extends State<ShipmentListScreen> {
  final ApiService apiService = ApiService();

  List<dynamic> _allShipments = [];
  List<dynamic> _filteredShipments = [];

  bool _isLoading = true;
  final TextEditingController _searchController = TextEditingController();

  DateTime? _startDate;
  DateTime? _endDate;

  @override
  void initState() {
    super.initState();
    _fetchShipments();
    _searchController.addListener(_applyFilters);
  }

  @override
  void dispose() {
    _searchController.removeListener(_applyFilters);
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _logout(BuildContext context) async {
    if (!mounted) return;
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (_) => const LoginScreen()),
      (route) => false,
    );
  }

  Future<void> _confirmLogout(BuildContext context) async {
    final bool? shouldLogout = await showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text(
            'Confirm Logout',
            style: TextStyle(fontWeight: FontWeight.bold, color: primaryColor),
          ),
          content: const Text(
            'Are you sure you want to log out of the application?',
            style: TextStyle(color: Colors.black87),
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(15),
          ),
          actions: <Widget>[
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text(
                'Cancel',
                style: TextStyle(color: primaryColor, fontWeight: FontWeight.w600),
              ),
            ),
            ElevatedButton(
              onPressed: () => Navigator.of(context).pop(true),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: const Text('Logout'),
            ),
          ],
        );
      },
    );

    if (shouldLogout == true) {
      await _logout(context);
    }
  }

  Future<void> _fetchShipments() async {
    if (!mounted) return;
    setState(() => _isLoading = true);
    try {
      final data = await apiService.fetchShipments(widget.token);
      if (mounted) {
        setState(() {
          _allShipments = data;
          _filteredShipments = data;
          _isLoading = false;
        });
      }
    } catch (e) {
      debugPrint('Error fetching shipments: $e');
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Failed to load shipments. Please try again.')),
        );
      }
    }
  }

  Future<void> _refreshData() async {
    _searchController.clear();
    setState(() {
      _startDate = null;
      _endDate = null;
    });
    await _fetchShipments();
  }

  void _applyFilters() {
    final String searchText = _searchController.text.toLowerCase();

    setState(() {
      _filteredShipments = _allShipments.where((shipment) {
        final invoiceNo = shipment['invoice_no']?.toString().toLowerCase() ?? '';
        bool searchMatch = invoiceNo.contains(searchText);

        bool dateMatch = true;
        final etaDate = DateTime.tryParse(shipment['eta_date'] ?? '');

        if (etaDate != null) {
          final recordDate = DateTime(
            etaDate.year,
            etaDate.month,
            etaDate.day,
          );

          if (_startDate != null && recordDate.isBefore(_startDate!)) {
            dateMatch = false;
          }
          if (_endDate != null && recordDate.isAfter(_endDate!)) {
            dateMatch = false;
          }
        }

        return searchMatch && dateMatch;
      }).toList();
    });
  }

  Future<void> _selectDateRange(BuildContext context) async {
    final DateTime now = DateTime.now();
    final DateTime firstDate = now.subtract(const Duration(days: 365 * 5));

    final picked = await showDateRangePicker(
      context: context,
      firstDate: firstDate,
      lastDate: now.add(const Duration(days: 365)),
      initialDateRange: _startDate != null && _endDate != null
          ? DateTimeRange(start: _startDate!, end: _endDate!)
          : null,
      builder: (context, child) {
        return Theme(
          data: ThemeData.light().copyWith(
            primaryColor: primaryColor,
            colorScheme: const ColorScheme.light(primary: primaryColor),
            buttonTheme: const ButtonThemeData(textTheme: ButtonTextTheme.primary),
          ),
          child: child!,
        );
      },
    );

    if (picked != null) {
      setState(() {
        _startDate = DateTime(picked.start.year, picked.start.month, picked.start.day);
        _endDate = DateTime(picked.end.year, picked.end.month, picked.end.day, 23, 59, 59);
      });
      _applyFilters();
    }
  }

  void _resetFilters() {
    _searchController.clear();
    setState(() {
      _startDate = null;
      _endDate = null;
      _filteredShipments = List.from(_allShipments);
    });
  }

  String _formatDate(String? dateString) {
    if (dateString == null || dateString.isEmpty) return 'N/A';
    final DateTime? date = DateTime.tryParse(dateString);
    if (date == null) return 'Invalid Date';
    return DateFormat('MMM dd, yyyy').format(date);
  }

  String _formatAmount(ShipmentRecord record) {
    final number = NumberFormat('#,##0.00');
    switch (record.currency) {
      case 'USD': return '\$ ${number.format(record.amount)}';
      case 'INR': return '₹ ${number.format(record.amount)}';
      case 'NPR': return 'रु ${number.format(record.amount)}';
      default: return '${number.format(record.amount)} ${record.currency}';
    }
  }

  Widget _buildShipmentCard(dynamic shipmentJson) {
    final ShipmentRecord record = ShipmentRecord.fromJson(Map<String, dynamic>.from(shipmentJson));
    final etaDate = _formatDate(shipmentJson['eta_date']);
    final amountFormatted = _formatAmount(record);

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 4, horizontal: 16),
      decoration: BoxDecoration(
        color: cardBackgroundColor,
        borderRadius: BorderRadius.circular(10),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
        border: Border.all(color: Colors.grey.withOpacity(0.1), width: 1),
      ),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => ShipmentDetailScreen(shipment: record),
            ),
          );
        },
        borderRadius: BorderRadius.circular(10),
        child: IntrinsicHeight(
          child: Row(
            children: [
              Container(
                width: 5,
                decoration: const BoxDecoration(
                  color: primaryColor,
                  borderRadius: BorderRadius.only(
                    topLeft: Radius.circular(10),
                    bottomLeft: Radius.circular(10),
                  ),
                ),
              ),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Expanded(
                            child: Text(
                              shipmentJson['invoice_no'] ?? 'N/A',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 15,
                                color: primaryColor,
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          Text(
                            amountFormatted,
                            style: const TextStyle(
                              fontWeight: FontWeight.w800,
                              color: successColor,
                              fontSize: 15,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Expanded(
                            child: Text(
                              shipmentJson['applicant'] ?? 'Unknown Applicant',
                              style: TextStyle(
                                fontSize: 13,
                                color: Colors.black.withOpacity(0.6),
                                fontWeight: FontWeight.w500,
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          Row(
                            children: [
                              Icon(Icons.access_time_rounded, size: 14, color: Colors.black.withOpacity(0.4)),
                              const SizedBox(width: 4),
                              Text(
                                etaDate,
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.black.withOpacity(0.5),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    // Wrap in SafeArea to handle notches and system bars
    return SafeArea(
      child: Scaffold(
        backgroundColor: Colors.grey[50],
        appBar: AppBar(
          title: const Text(
            "Shipments Dashboard",
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
          ),
          backgroundColor: primaryColor,
          foregroundColor: Colors.white,
          elevation: 0,
          actions: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
              child: ElevatedButton.icon(
                onPressed: () => _confirmLogout(context),
                icon: const Icon(Icons.exit_to_app, size: 16),
                label: const Text("Logout"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors. white,
                  foregroundColor: Colors.red,
                  elevation: 0,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                ),
              ),
            ),
          ],
        ),
        body: Column(
          children: [
            // Filter Section
            Container(
              color: primaryColor,
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
              child: Row(
                children: [
                  Expanded(
                    child: SizedBox(
                      height: 45,
                      child: TextField(
                        controller: _searchController,
                        decoration: InputDecoration(
                          hintText: "Search Invoice...",
                          prefixIcon: const Icon(Icons.search, color: primaryColor, size: 20),
                          suffixIcon: _searchController.text.isNotEmpty
                              ? GestureDetector(
                                  onTap: () => _searchController.clear(),
                                  child: const Icon(Icons.clear, color: Colors.grey),
                                )
                              : null,
                          filled: true,
                          fillColor: Colors.white,
                          contentPadding: EdgeInsets.zero,
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: BorderSide.none,
                          ),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Container(
                    height: 45,
                    decoration: BoxDecoration(
                      color: accentColor,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: IconButton(
                      icon: const Icon(Icons.calendar_month, color: primaryColor),
                      onPressed: () => _selectDateRange(context),
                    ),
                  ),
                ],
              ),
              
            ),

            // Active Filter Badge
            if (_startDate != null || _endDate != null)
              Padding(
                padding: const EdgeInsets.all(12.0),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: accentColor.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: accentColor),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.filter_alt, size: 16, color: primaryColor),
                      const SizedBox(width: 8),
                      Flexible(
                        child: Text(
                          'Filter by ETA ${DateFormat('MMM d').format(_startDate!)} - ${DateFormat('MMM d').format(_endDate!)}',
                          style: const TextStyle(color: primaryColor, fontWeight: FontWeight.bold, fontSize: 12),
                        ),
                      ),
                      const SizedBox(width: 8),
                      GestureDetector(
                        onTap: _resetFilters,
                        child: const Icon(Icons.cancel, size: 18, color: Colors.redAccent),
                      ),
                    ],
                  ),
                ),
              ),

            // Main List Area
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator(color: primaryColor))
                  : _filteredShipments.isEmpty
                      ? SingleChildScrollView(
                          physics: const AlwaysScrollableScrollPhysics(),
                          child: Container(
                            height: MediaQuery.of(context).size.height * 0.6,
                            alignment: Alignment.center,
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(Icons.inventory_2_outlined, size: 64, color: Colors.grey[300]),
                                const SizedBox(height: 16),
                                const Text("No shipments found", style: TextStyle(color: Colors.grey, fontSize: 16)),
                                TextButton(onPressed: _resetFilters, child: const Text("Clear Filters")),
                              ],
                            ),
                          ),
                        )
                      : RefreshIndicator(
                          onRefresh: _refreshData,
                          color: primaryColor,
                          child: ListView.builder(
                            padding: const EdgeInsets.only(top: 8, bottom: 20),
                            itemCount: _filteredShipments.length,
                            itemBuilder: (context, index) => _buildShipmentCard(_filteredShipments[index]),
                          ),
                        ),
            ),
          ],
        ),
      ),
    );
  }
}