import 'package:flutter/material.dart';
import 'package:frontend/screens/pdf_viewer.dart';
import 'package:intl/intl.dart';
import '../models/shipment_record.dart';

const Color primaryColor = Color(0xFF4e2780);
const Color accentColor = Color(0xFFFFDE59);
const Color financialGreen = Color(0xFF1a936f);
const Color cardBackgroundColor = Color(0xFFfcfcff);

class ShipmentDetailScreen extends StatelessWidget {
  final ShipmentRecord shipment;

  const ShipmentDetailScreen({super.key, required this.shipment});

  // ---------------- PDF VIEWER ----------------
  void _openPdfViewer(BuildContext context, String url) {
    if (!url.startsWith('http')) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Invalid PDF URL")),
      );
      return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => FullScreenPdfViewer(url: url),
      ),
    );
  }

  // ---------------- VIEW CHITTIS BUTTON ----------------
  Widget _buildChittiButton(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 8, 12, 12),
      child: SizedBox(
        width: double.infinity,
        height: 48,
        child: ElevatedButton(
          onPressed: () {
            _showChittiList(context);
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: primaryColor,
            elevation: 3,
            shadowColor: primaryColor.withOpacity(0.3),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10),
            ),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: const [
              Icon(Icons.picture_as_pdf, size: 20, color: Colors.white),
              SizedBox(width: 8),
              Text(
                "View Docs",
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 0.3,
                  color: Colors.white,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ---------------- LIST OF PDFs ----------------
  void _showChittiList(BuildContext context) {
    final List<ChittiRecord> pdfList = shipment.chittis;

    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (_) {
        // ---------------- EMPTY STATE ----------------
        if (pdfList.isEmpty) {
          return SizedBox(
            height: 200,
            child: Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: const [
                  Icon(
                    Icons.picture_as_pdf_outlined,
                    size: 44,
                    color: Colors.grey,
                  ),
                  SizedBox(height: 10),
                  Text(
                    "No shipment docs available",
                    style: TextStyle(
                      fontSize: 15,
                      color: Colors.grey,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
          );
        }

        // ---------------- PDF LIST ----------------
        return ListView.separated(
          shrinkWrap: true,
          itemCount: pdfList.length,
          separatorBuilder: (_, __) => const Divider(height: 1),
          itemBuilder: (context, index) {
            final chitti = pdfList[index];
            return ListTile(
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              leading: const Icon(Icons.picture_as_pdf, color: Colors.red, size: 28),
              title: Text(
                chitti.displayName,
                style: const TextStyle(fontWeight: FontWeight.w500),
              ),
              subtitle: Text(
                chitti.date,
                style: const TextStyle(fontSize: 13),
              ),
              trailing: const Icon(Icons.arrow_forward_ios, size: 14),
              onTap: () {
                Navigator.pop(context);
                _openPdfViewer(context, chitti.url);
              },
            );
          },
        );
      },
    );
  }

  // ---------------- DETAIL ROW ----------------
  Widget _buildDetailRow(String label, String value,
      {Color valueColor = Colors.black87, FontWeight valueWeight = FontWeight.normal}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0, horizontal: 12.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            flex: 2,
            child: Text(
              label,
              style: const TextStyle(
                fontWeight: FontWeight.w500,
                color: Colors.blueGrey,
                fontSize: 14,
              ),
            ),
          ),
          Expanded(
            flex: 3,
            child: Text(
              value,
              textAlign: TextAlign.right,
              style: TextStyle(
                fontSize: 14,
                fontWeight: valueWeight,
                color: valueColor,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDateCard(String label, DateTime? date) {
    String formattedDate = 'N/A';
    Color dateColor = Colors.grey;

    if (date != null) {
      formattedDate = DateFormat('MMM dd, yyyy').format(date);
      dateColor = primaryColor;
    }

    return Expanded(
      child: Card(
        color: cardBackgroundColor,
        elevation: 2,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
          side: BorderSide(color: dateColor.withOpacity(0.15), width: 1),
        ),
        child: Padding(
          padding: const EdgeInsets.all(12.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: Colors.blueGrey,
                ),
              ),
              const SizedBox(height: 6),
              Row(
                children: [
                  Icon(Icons.calendar_month, size: 16, color: dateColor),
                  const SizedBox(width: 6),
                  Flexible(
                    child: Text(
                      formattedDate,
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.bold,
                        color: dateColor,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ---------------- BUILD ----------------
  @override
  Widget build(BuildContext context) {
    final amountText = "${shipment.amount} ${shipment.currency}";

    return Scaffold(
      backgroundColor: Colors.grey.shade100,
      appBar: AppBar(
        title: const Text("Shipment Details"),
        backgroundColor: primaryColor,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // HEADER
              Container(
                width: double.infinity,
                padding: const EdgeInsets.fromLTRB(16, 16, 16, 16),
                decoration: BoxDecoration(
                  color: primaryColor.withOpacity(0.9),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "Invoice ID",
                      style: TextStyle(
                        fontSize: 13,
                        color: accentColor,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      shipment.invoiceNo,
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.w900,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      "Applicant: ${shipment.applicant}",
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                        color: Colors.white.withOpacity(0.85),
                      ),
                    ),
                  ],
                ),
              ),

              // AMOUNT CARD
              Padding(
                padding: const EdgeInsets.fromLTRB(12, 12, 12, 8),
                child: Card(
                  elevation: 3,
                  color: cardBackgroundColor,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                    side: BorderSide(color: financialGreen.withOpacity(0.25), width: 1.5),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(14.0),
                    child: Row(
                      children: [
                        const Icon(Icons.account_balance_wallet, size: 26, color: financialGreen),
                        const SizedBox(width: 12),
                        Flexible(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                "Total Shipment Value",
                                style: TextStyle(
                                  color: Colors.blueGrey,
                                  fontSize: 13,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                              const SizedBox(height: 3),
                              Text(
                                amountText,
                                style: const TextStyle(
                                  fontSize: 20,
                                  fontWeight: FontWeight.w900,
                                  color: financialGreen,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),

              // DATE CARDS
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 8.0),
                child: Row(
                  children: [
                    _buildDateCard("Dispatch Date", shipment.dispatchDate),
                    const SizedBox(width: 8),
                    _buildDateCard("Doc Received", shipment.docReceivedDate),
                  ],
                ),
              ),

              // DETAILS CARD
              Padding(
                padding: const EdgeInsets.fromLTRB(12, 8, 12, 16),
                child: Card(
                  elevation: 3,
                  color: cardBackgroundColor,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  child: Column(
                    children: [
                      const Padding(
                        padding: EdgeInsets.fromLTRB(12, 14, 12, 8),
                        child: Text(
                          "Shipping & Financial Data",
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: primaryColor,
                          ),
                        ),
                      ),
                      const Divider(height: 12, indent: 12, endIndent: 12),

                      _buildDetailRow("Bank", shipment.bankName ?? "—"),
                      _buildDetailRow("Bank Ref No", shipment.bankRefNo ?? "—"),
                      _buildDetailRow("Price Terms", shipment.priceTerms),
                      _buildDetailRow("Payment Terms", shipment.paymentTerms),
                      _buildDetailRow(
                        "Settlement Date",
                        shipment.settlementDate != null
                            ? DateFormat('MMM dd, yyyy').format(shipment.settlementDate!)
                            : "Pending",
                      ),
                      _buildDetailRow(
                        "ETA Date",
                        shipment.etaDate != null
                            ? DateFormat('MMM dd, yyyy').format(shipment.etaDate!)
                            : "Pending",
                      ),
                      _buildDetailRow(
                        "Customs Entry Date",
                        shipment.customsEntryDate != null
                            ? DateFormat('MMM dd, yyyy').format(shipment.customsEntryDate!)
                            : "Pending",
                      ),
                      _buildDetailRow("PP No", shipment.ppNo ?? "—"),
                      _buildDetailRow("Insurance", shipment.insuranceCompany ?? "—"),

                      // BUTTON TO VIEW CHITTIS
                      _buildChittiButton(context),
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
}