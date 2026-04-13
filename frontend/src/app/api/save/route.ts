import { NextRequest, NextResponse } from 'next/server';
import { appendToSheet } from '@/lib/sheets';

export async function POST(req: NextRequest) {
  try {
    const data = await req.json();

    if (!data) {
      return NextResponse.json({ error: 'No data provided' }, { status: 400 });
    }

    // Logic to select the columns we want in the sheet
    const row = {
      'Buyer Name': data.buyer_name,
      'Buyer Address': data.buyer_address,
      'GST No': data.gst_no,
      'Mobile No': data.mobile_no,
      'Bill No': data.bill_no,
      'Date': data.date,
      'Total Amount': data.total_amount,
      'Timestamp': new Date().toISOString(),
      'Status': 'Pending'
    };

    const result = await appendToSheet(row);
    return NextResponse.json(result);
  } catch (error: any) {
    console.error('Save error:', error);
    return NextResponse.json({ error: error.message || 'Error saving to sheet' }, { status: 500 });
  }
}
