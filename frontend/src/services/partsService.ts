import type { IPDPart, RiskProfile } from '@/types';

// Mock Data
const MOCK_PARTS: IPDPart[] = [
    {
        ipd_part_id: '1',
        document_id: 'doc-1',
        change_type: 'ADD',
        figure: '10-20-44',
        item: '010',
        part_number: 'BACN10J-4',
        nomenclature: 'NUT, SELF-LOCKING',
        effectivity_type: 'RANGE',
        effectivity_range: { from: '001', to: '999' },
        effectivity_values: [],
        upa: '1',
        page_number: 44
    },
    {
        ipd_part_id: '2',
        document_id: 'doc-1',
        change_type: 'MODIFY',
        figure: '10-20-44',
        item: '020',
        part_number: 'NAS1149F0363P',
        nomenclature: 'WASHER, FLAT',
        effectivity_type: 'LIST',
        effectivity_values: ['001', '005', '010'],
        upa: '2',
        sb_reference: 'SB-73-1022'
    },
    {
        ipd_part_id: '3',
        document_id: 'doc-1',
        change_type: 'DELETE',
        figure: '10-20-44',
        item: '030',
        part_number: 'MS24665-151',
        nomenclature: 'COTTER PIN',
        effectivity_type: 'LIST',
        effectivity_values: ['001'],
        upa: '1'
    }
];

const MOCK_RISK_PROFILE: RiskProfile = {
    part_number: 'BACN10J-4',
    risk_score: 15,
    volatility_index: 'Low',
    similar_part_count: 2,
    warning_count_30d: 0,
    error_report_count: 0,
    last_updated: new Date().toISOString()
};

const MOCK_HIGH_RISK_PROFILE: RiskProfile = {
    part_number: 'NAS1149F0363P',
    risk_score: 75,
    volatility_index: 'High',
    similar_part_count: 12,
    warning_count_30d: 5,
    error_report_count: 2,
    last_updated: new Date().toISOString()
};

export const PartsService = {
    async searchParts(query: string): Promise<IPDPart[]> {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 600));

        // Simple filter for mock
        if (!query) return [];

        // In real app, backend handles this. Here we return all mocks if query matches anything relatively
        // or just return all for demo if query is "all"
        return MOCK_PARTS.filter(p =>
            p.part_number.toLowerCase().includes(query.toLowerCase()) ||
            p.nomenclature.toLowerCase().includes(query.toLowerCase()) ||
            p.item.includes(query)
        );
    },

    async getRiskProfile(partNumber: string): Promise<RiskProfile> {
        await new Promise(resolve => setTimeout(resolve, 400));
        if (partNumber === 'NAS1149F0363P') return MOCK_HIGH_RISK_PROFILE;
        return { ...MOCK_RISK_PROFILE, part_number: partNumber };
    }
};
