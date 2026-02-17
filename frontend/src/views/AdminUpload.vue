<script setup lang="ts">
import { ref } from 'vue';
import { usePartsStore } from '@/stores/parts';
import { UploadCloud, FileText, X, CheckCircle, Loader2 } from 'lucide-vue-next';

const partsStore = usePartsStore();
const isDragging = ref(false);
const files = ref<File[]>([]);
const documentType = ref<'ipd' | 'drawing'>('ipd');
const pollingIntervals = ref<Record<string, number>>({});
const fileInput = ref<HTMLInputElement | null>(null);

const triggerFileInput = () => {
  fileInput.value?.click();
};

const onDragOver = (e: DragEvent) => {
  e.preventDefault();
  isDragging.value = true;
};

const onDragLeave = (e: DragEvent) => {
  e.preventDefault();
  isDragging.value = false;
};

const onDrop = (e: DragEvent) => {
  e.preventDefault();
  isDragging.value = false;
  if (e.dataTransfer?.files) {
    addFiles(Array.from(e.dataTransfer.files));
  }
};

const onFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement;
  if (input.files) {
    addFiles(Array.from(input.files));
  }
};

const addFiles = (newFiles: File[]) => {
  newFiles.forEach(file => {
    if (!files.value.find(f => f.name === file.name)) {
      files.value.push(file);
      partsStore.uploadStatus[file.name] = 'pending';
      partsStore.uploadProgress[file.name] = 0;
    }
  });
};

const removeFile = (fileName: string) => {
  files.value = files.value.filter(f => f.name !== fileName);
  delete partsStore.uploadStatus[fileName];
  delete partsStore.uploadProgress[fileName];
  if (pollingIntervals.value[fileName]) {
      clearInterval(pollingIntervals.value[fileName]);
      delete pollingIntervals.value[fileName];
  }
};

const uploadFiles = async () => {
  for (const file of files.value) {
    if (partsStore.uploadStatus[file.name] === 'success' || partsStore.uploadStatus[file.name] === 'uploading') continue;
    
    // Upload the file
    await partsStore.uploadDocument(file);
  }
};
</script>

<template>
  <div class="space-y-8 animate-fade-in">
    <div>
        <h1 class="text-3xl font-bold text-slate-800 mb-2">Upload Dokumen</h1>
        <p class="text-slate-500">Unggah dokumen IPD (PDF) ke sistem untuk ekstraksi otomatis.</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Upload Zone -->
        <div class="lg:col-span-2 space-y-6">
            
            <!-- Type Selector -->
            <div class="flex gap-4 p-1 bg-slate-100 rounded-xl inline-flex">
                <button 
                   @click="documentType = 'ipd'"
                   class="px-6 py-2.5 rounded-lg text-sm font-bold transition-all"
                   :class="documentType === 'ipd' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
                >
                   Dokumen IPD
                </button>
                 <!-- Drawing support planned for later phases -->
                <button 
                   disabled
                   class="px-6 py-2.5 rounded-lg text-sm font-bold transition-all text-slate-400 cursor-not-allowed"
                >
                   Engineering Drawing (Soon)
                </button>
            </div>

            <!-- Drop Zone -->
            <div 
                class="border-2 border-dashed rounded-2xl p-12 flex flex-col items-center justify-center text-center transition-all cursor-pointer bg-slate-50 hover:bg-white"
                :class="isDragging ? 'border-blue-500 bg-blue-50/50' : 'border-slate-300 hover:border-blue-400'"
                @dragover="onDragOver"
                @dragleave="onDragLeave"
                @drop="onDrop"
                @click="triggerFileInput"
            >
                <input type="file" ref="fileInput" class="hidden" multiple accept=".pdf" @change="onFileSelect" />
                
                <div class="w-20 h-20 bg-white rounded-full flex items-center justify-center mb-6 shadow-sm border border-slate-100">
                    <UploadCloud class="w-10 h-10 text-blue-600" />
                </div>
                
                <h3 class="text-xl font-bold text-slate-800 mb-2">
                    Drag & Drop file PDF di sini
                </h3>
                <p class="text-slate-500 mb-6">atau klik untuk memilih file dari komputer</p>
                
                <div class="text-xs text-slate-400 font-medium px-4 py-2 bg-slate-100 rounded-full">
                    Support: PDF (Max 100MB)
                </div>
            </div>
        </div>

        <!-- File List -->
        <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm h-fit">
            <h3 class="font-bold text-slate-800 mb-4 flex items-center justify-between">
                <span>Antrian Upload</span>
                <span class="text-xs font-normal text-slate-500">{{ files.length }} file</span>
            </h3>

            <div v-if="files.length === 0" class="text-center py-12 text-slate-400 border-2 border-dashed border-slate-100 rounded-lg">
                <FileText class="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p class="text-sm">Belum ada file dipilih</p>
            </div>

            <div v-else class="space-y-3 mb-6">
                <div v-for="file in files" :key="file.name" class="bg-slate-50 p-3 rounded-lg border border-slate-100 relative group">
                    <div class="flex items-start gap-3">
                        <div class="p-2 bg-white rounded border border-slate-200 text-slate-500">
                            <FileText class="w-5 h-5" />
                        </div>
                        <div class="flex-1 min-w-0">
                            <p class="text-sm font-medium text-slate-800 truncate" :title="file.name">{{ file.name }}</p>
                            <div class="flex items-center gap-2 mt-1">
                                <span class="text-xs text-slate-500">{{ (file.size / 1024 / 1024).toFixed(2) }} MB</span>
                                <span v-if="partsStore.uploadStatus[file.name] === 'error'" class="text-xs text-red-500 font-medium">Gagal</span>
                                <span v-if="partsStore.uploadStatus[file.name] === 'success'" class="text-xs text-emerald-600 font-medium">Uploaded</span>
                                <span v-if="partsStore.uploadStatus[file.name] === 'parsing'" class="text-xs text-blue-600 font-medium flex items-center gap-1">
                                    <Loader2 class="w-3 h-3 animate-spin" /> Parsing...
                                </span>
                            </div>
                            
                            <!-- Progress Bar -->
                            <div v-if="partsStore.uploadStatus[file.name] === 'uploading'" class="h-1 w-full bg-slate-200 rounded-full mt-2 overflow-hidden">
                                <div class="h-full bg-blue-600 transition-all duration-200" :style="{ width: `${partsStore.uploadProgress[file.name]}%` }"></div>
                            </div>
                        </div>
                        
                        <button 
                            v-if="partsStore.uploadStatus[file.name] === 'pending'"
                            @click="removeFile(file.name)" 
                            class="text-slate-400 hover:text-red-500 p-1 opacity-0 group-hover:opacity-100 transition-all"
                        >
                            <X class="w-4 h-4" />
                        </button>
                         <div v-else-if="partsStore.uploadStatus[file.name] === 'success' || partsStore.uploadStatus[file.name] === 'parsing'" class="text-emerald-500 p-1">
                            <CheckCircle class="w-4 h-4" />
                        </div>
                    </div>
                </div>
            </div>

            <button 
                @click="uploadFiles"
                :disabled="files.length === 0"
                class="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md shadow-blue-600/20"
            >
                Mulai Upload
            </button>
        </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
