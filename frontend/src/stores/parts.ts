import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { IPDPart, RiskProfile } from '../types';
import { PartsService } from '@/services/partsService';

export const usePartsStore = defineStore('parts', () => {
    // State
    const searchResults = ref<IPDPart[]>([]);
    const selectedPart = ref<IPDPart | null>(null);
    const loading = ref(false);
    const riskProfile = ref<RiskProfile | null>(null);

    // Actions
    const searchParts = async (query: string) => {
        loading.value = true;
        try {
            searchResults.value = await PartsService.searchParts(query);
        } catch (error) {
            console.error('Search failed', error);
            searchResults.value = [];
        } finally {
            loading.value = false;
        }
    };

    const selectPart = async (part: IPDPart) => {
        selectedPart.value = part;
        try {
            riskProfile.value = await PartsService.getRiskProfile(part.part_number);
        } catch (error) {
            console.error('Failed to load risk profile', error);
        }
    };

    const clearSelection = () => {
        selectedPart.value = null;
        riskProfile.value = null;
    };

    return {
        searchResults,
        selectedPart,
        loading,
        riskProfile,
        searchParts,
        selectPart,
        clearSelection,
    };
});
