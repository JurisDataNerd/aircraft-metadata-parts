export interface Document {
    document_id: string;
    document_type: 'IPD' | 'DRAWING';
    document_number: string;
    revision: string;
    issue_date: string;
    aircraft_model: string;
    source_pdf_path: string;
}

export interface IPDPart {
    ipd_part_id: string;
    document_id: string;
    change_type: 'ADD' | 'MODIFY' | 'DELETE';
    figure: string;
    item: string;
    part_number: string;
    nomenclature: string;
    supplier_code?: string;
    effectivity_type: 'LIST' | 'RANGE';
    effectivity_values: string[];
    effectivity_range?: { from: string; to: string };
    upa?: string;
    sb_reference?: string;
    page_number?: number;
}

export interface DrawingItem {
    drawing_item_id: string;
    document_id: string;
    item_number: string;
    part_number: string;
    title: string;
    sheet_number: string;
    material_spec?: string;
    approval_authority?: string;
    font_type?: string;
    artwork_reference?: string;
    notes?: string;
}

export interface PartMaster {
    part_number: string;
    linked_ipd_parts: IPDPart[];
    linked_drawing_items: DrawingItem[];
}

export interface RiskProfile {
    part_number: string;
    risk_score: number;
    volatility_index: 'Low' | 'Medium' | 'High';
    similar_part_count: number;
    warning_count_30d: number;
    error_report_count: number;
    last_updated: string;
}
