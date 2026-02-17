import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { IPDPart, RiskProfile } from '@/types';
import apiClient from '@/api/client';

export const usePartsStore = defineStore('parts', () => {
    // State
    const searchResults = ref<IPDPart[]>([]);
    const selectedPart = ref<IPDPart | null>(null);
    const loading = ref(false);
    const riskProfile = ref<RiskProfile | null>(null);

    // Statistics & History State
    const statistics = ref<any>(null);
    const documents = ref<any[]>([]);
    const uploadProgress = ref<Record<string, number>>({});
    const uploadStatus = ref<Record<string, string>>({});

    // Actions
    const fetchDocuments = async () => {
        try {
            const response = await apiClient.get('/documents/');
            documents.value = response.data.items;
        } catch (error) {
            console.error('Failed to fetch documents', error);
        }
    };

    const searchParts = async (query: string) => {
        loading.value = true;
        try {
            if (query === 'stickers') {
                const response = await apiClient.get('/filter/browse?type=sticker');
                searchResults.value = response.data.items.map((p: any) => ({
                    ...p,
                    effectivity_values: p.effectivity_values || [],
                    effectivity_range: p.effectivity_range || null
                }));
            }
            // Check if query is numeric (Line Number)
            else if (/^\d+$/.test(query)) {
                const response = await apiClient.get(`/filter/line/${query}`);

                // Map backend response matching types/index.ts
                searchResults.value = response.data.applicable_parts.map((p: any) => ({
                    ...p,
                    effectivity_values: p.effectivity?.values || [],
                    effectivity_range: p.effectivity?.range || null,
                    effectivity_type: p.effectivity?.type || p.effectivity_type
                }));
            } else {
                // Determine if part search is supported or not in this phase
                console.warn("Part number search not fully implemented in backend yet");
                searchResults.value = [];
            }
        } catch (error) {
            console.error('Search failed', error);
            searchResults.value = [];
        } finally {
            loading.value = false;
        }
    };

    const selectPart = async (part: IPDPart) => {
        selectedPart.value = part;
        // Mock risk data for now as backend doesn't have specific risk endpoint yet
        // In real implementations, this would call an endpoint
        riskProfile.value = {
            part_number: part.part_number,
            risk_score: Math.floor(Math.random() * 100),
            volatility_index: ['Low', 'Medium', 'High'][Math.floor(Math.random() * 3)] as 'Low' | 'Medium' | 'High',
            similar_parts: [],
            similar_part_count: 0,
            warning_count_30d: 0,
            error_report_count: 0,
            last_updated: new Date().toISOString()
        };
    };

    const clearSelection = () => {
        selectedPart.value = null;
        riskProfile.value = null;
    };

    const fetchStatistics = async () => {
        try {
            const response = await apiClient.get('/filter/statistics');
            statistics.value = response.data;
        } catch (error) {
            console.error('Failed to fetch stats', error);
        }
    };

    const uploadDocument = async (file: File) => {
        const formData = new FormData();
        formData.append('file', file);

        try {
            uploadStatus.value[file.name] = 'uploading';

            await apiClient.post('/documents/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                onUploadProgress: (progressEvent) => {
                    const progress = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
                    uploadProgress.value[file.name] = progress;
                }
            });

            uploadStatus.value[file.name] = 'success';

            // Refresh stats to show immediate updates
            await fetchStatistics();
            await fetchDocuments();
        } catch (error) {
            console.error('Upload failed', error);
            uploadStatus.value[file.name] = 'error';
        }
    };

    return {
        searchResults,
        selectedPart,
        loading,
        riskProfile,
        statistics,
        documents,
        uploadProgress,
        uploadStatus,
        searchParts,
        selectPart,
        clearSelection,
        fetchStatistics,
        fetchDocuments,
        uploadDocument
    };
});
