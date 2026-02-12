class ChittiRecord {
  final int id;
  final String url; // FULL URL
  final String displayName;
  final String date;

  ChittiRecord({
    required this.id,
    required this.url,
    required this.displayName,
    required this.date,
  });

  factory ChittiRecord.fromJson(Map<String, dynamic> json, {String? baseUrl}) {
    String fileUrl = json['url'] ?? '';
    if (baseUrl != null && !fileUrl.startsWith('http')) {
      fileUrl = baseUrl + fileUrl; // prepend domain if relative
    }
    return ChittiRecord(
      id: json['id'],
      url: fileUrl,
      displayName: json['display_name'] ?? 'Chitti.pdf',
      date: json['date'] ?? '',
    );
  }
}

class ShipmentRecord {
  final int id;
  final String priceTerms;
  final String invoiceNo;
  final String? bankName;
  final String? bankRefNo;
  final double amount;
  final String currency;
  final DateTime? dispatchDate;
  final DateTime? docReceivedDate;
  final DateTime? etaDate;
  final DateTime? settlementDate;
  final DateTime? customsEntryDate;
  final String? ppNo;
  final String paymentTerms;
  final String applicant;
  final String? insuranceCompany;
  final List<ChittiRecord> chittis;

  ShipmentRecord({
    required this.id,
    required this.priceTerms,
    required this.invoiceNo,
    required this.bankName,
    required this.bankRefNo,
    required this.amount,
    required this.currency,
    required this.dispatchDate,
    required this.docReceivedDate,
    required this.etaDate,
    required this.settlementDate,
    required this.customsEntryDate,
    required this.ppNo,
    required this.paymentTerms,
    required this.applicant,
    required this.insuranceCompany,
    required this.chittis,
  });

  factory ShipmentRecord.fromJson(Map<String, dynamic> json, {String? baseUrl}) {
    return ShipmentRecord(
      id: json['id'],
      priceTerms: json['price_terms'],
      invoiceNo: json['invoice_no'],
      bankName: json['bank_name'],
      bankRefNo: json['bank_ref_no'],
      amount: double.tryParse(json['amount'].toString()) ?? 0.0,
      currency: json['currency'] ?? 'USD',
      dispatchDate: json['dispatch_date'] != null ? DateTime.parse(json['dispatch_date']) : null,
      docReceivedDate: json['doc_received_date'] != null ? DateTime.parse(json['doc_received_date']) : null,
      etaDate: json['eta_date'] != null ? DateTime.parse(json['eta_date']) : null,
      settlementDate: json['settlement_date'] != null ? DateTime.parse(json['settlement_date']) : null,
      customsEntryDate: json['customs_entry_date'] != null ? DateTime.parse(json['customs_entry_date']) : null,
      ppNo: json['pp_no'],
      paymentTerms: json['payment_terms'],
      applicant: json['applicant'],
      insuranceCompany: json['insurance_company'],
      chittis: json['chitti_files'] != null
          ? List<ChittiRecord>.from(
              json['chitti_files'].map((x) => ChittiRecord.fromJson(x, baseUrl: baseUrl)))
          : [],
    );
  }
}
