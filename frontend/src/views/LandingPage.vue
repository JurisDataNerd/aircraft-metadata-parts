<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { 
  ShieldCheck, 
  Database, 
  BrainCircuit, 
  Plane, 
  ArrowRight,
  Activity,
  Zap,
  Layers,
  CheckCircle2
} from 'lucide-vue-next';
import { useMouse, useWindowScroll } from '@vueuse/core';

const router = useRouter();
const { x, y } = useMouse();
const { y: scrollY } = useWindowScroll();

const isLoaded = ref(false);

// Carousel State
const activeSlide = ref(0);
const slides = [
    { color: 'bg-blue-50 text-blue-600', title: 'Data Integration', icon: Database },
    { color: 'bg-emerald-50 text-emerald-600', title: 'Safety Guardrails', icon: ShieldCheck },
    { color: 'bg-violet-50 text-violet-600', title: 'Risk Intelligence', icon: BrainCircuit }
];
let carouselInterval: number;

onMounted(() => {
  setTimeout(() => isLoaded.value = true, 100);
  carouselInterval = setInterval(() => {
      activeSlide.value = (activeSlide.value + 1) % slides.length;
  }, 4000);
});

onUnmounted(() => {
    clearInterval(carouselInterval);
});

const navigateToLogin = () => {
  router.push('/login');
};

const features = [
  {
    title: 'Satu Sumber Kebenaran',
    desc: 'Menyatukan data IPD dan Drawing dalam satu database terstruktur yang deterministik.',
    icon: Database,
    color: 'text-blue-600',
    bg: 'bg-blue-100'
  },
  {
    title: 'Pencegahan Kesalahan',
    desc: 'Guardrail system yang mencegah pemilihan part yang salah dengan validasi dokumen.',
    icon: ShieldCheck,
    color: 'text-emerald-600',
    bg: 'bg-emerald-100'
  },
  {
    title: 'Analisis Risiko Cerdas',
    desc: 'Mendeteksi alternatif part dan menghitung skor risiko berdasarkan data historis.',
    icon: BrainCircuit,
    color: 'text-violet-600',
    bg: 'bg-violet-100'
  }
];

const steps = [
  { num: '01', title: 'Cari Konfigurasi', desc: 'Input Line Number atau Part Number aircraft.' },
  { num: '02', title: 'Analisis Otomatis', desc: 'Sistem memfilter effectivity dan mengecek drawing.' },
  { num: '03', title: 'Review Keputusan', desc: 'Lihat preview risiko dan alternatif sebelum konfirmasi.' },
  { num: '04', title: 'Log Tercatat', desc: 'Setiap keputusan tersimpan untuk audit trail.' }
];

const galleryItems = [
    { title: 'Interactive Search', icon: Layers, desc: 'Pencarian cepat dengan filter cerdas' },
    { title: 'Real-time Validation', icon: Zap, desc: 'Validasi instan terhadap dokumen resmi' },
    { title: 'Risk Visualization', icon: Activity, desc: 'Indikator visual untuk potensi masalah' }
];
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 font-sans overflow-x-hidden selection:bg-blue-100 selection:text-blue-900">
    
    <!-- Navbar -->
    <nav class="fixed top-0 w-full z-50 transition-all duration-300 border-b"
         :class="scrollY > 20 ? 'bg-white/90 backdrop-blur-md shadow-sm border-slate-200' : 'bg-transparent border-transparent'">
      <div class="container mx-auto px-6 h-20 flex items-center justify-between">
        <div class="flex items-center gap-3">
           <div class="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-600/20">
             <Plane class="text-white w-6 h-6 transform -rotate-45" />
           </div>
           <span class="text-xl font-bold tracking-tight text-slate-900">Aircraft<span class="font-light text-blue-600">Config</span></span>
        </div>
        <button @click="navigateToLogin" class="px-6 py-2.5 rounded-full bg-slate-900 text-white hover:bg-slate-800 transition-all font-medium flex items-center gap-2 group shadow-lg shadow-slate-900/10">
          Masuk Aplikasi
          <ArrowRight class="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </button>
      </div>
    </nav>

    <!-- Hero Section -->
    <header class="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden">
      <!-- Animated Background Blobs -->
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full -z-10 pointer-events-none opacity-60">
         <div class="absolute top-[-10%] right-[-5%] w-[600px] h-[600px] bg-blue-100 rounded-full blur-[100px] animate-pulse"></div>
         <div class="absolute bottom-[-10%] left-[-10%] w-[500px] h-[500px] bg-indigo-100 rounded-full blur-[100px]" 
              :style="{ transform: `translate(${x * 0.02}px, ${y * 0.02}px)` }"></div>
      </div>

      <div class="container mx-auto px-6 grid lg:grid-cols-2 gap-12 items-center">
        <div class="space-y-8 relative z-10" :class="{'opacity-0 translate-y-10': !isLoaded, 'opacity-100 translate-y-0': isLoaded}" style="transition: all 1s ease-out">
           <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100 border border-blue-200 text-blue-700 text-sm font-medium">
             <Activity class="w-4 h-4" />
             <span>Sistem Cerdas Konfigurasi Pesawat</span>
           </div>
           
           <h1 class="text-5xl lg:text-7xl font-bold leading-tight text-slate-900">
             Kendalikan <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Konfigurasi</span> Tanpa Keraguan
           </h1>
           
           <p class="text-lg text-slate-600 max-w-xl leading-relaxed">
             Platform intelijen yang menyatukan data IPD dan Drawing untuk memberikan panduan keputusan engineering yang akurat, aman, dan deterministik.
           </p>

           <div class="flex flex-col sm:flex-row gap-4 pt-4">
             <button @click="navigateToLogin" class="px-8 py-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold shadow-xl shadow-blue-600/20 transition-all transform hover:-translate-y-1 flex items-center justify-center gap-2">
               Mulai Sekarang
               <ArrowRight class="w-5 h-5" />
             </button>
             <button class="px-8 py-4 rounded-xl bg-white hover:bg-slate-50 text-slate-700 font-medium border border-slate-200 shadow-sm transition-all flex items-center justify-center gap-2">
               Pelajari Dokumentasi
             </button>
           </div>
        </div>

        <!-- Hero Visual (Carousel) -->
        <div class="relative lg:h-[500px] flex items-center justify-center">
           <div class="relative w-full aspect-square max-w-lg perspective-1000">
               <!-- Carousel Container -->
               <div class="relative w-full h-full">
                   <transition-group 
                      enter-active-class="transition duration-1000 ease-out"
                      enter-from-class="opacity-0 translate-x-10 rotate-y-10"
                      enter-to-class="opacity-100 translate-x-0 rotate-y-0"
                      leave-active-class="transition duration-700 ease-in absolute inset-0"
                      leave-from-class="opacity-100 translate-x-0"
                      leave-to-class="opacity-0 -translate-x-10"
                   >
                        <div 
                            v-for="(slide, index) in slides" 
                            :key="index"
                            v-show="activeSlide === index"
                            class="absolute inset-0 bg-white rounded-3xl border border-slate-100 overflow-hidden shadow-2xl skew-y-3 transform transition-all duration-700 w-full"
                        >
                            <!-- Decorative background -->
                            <div class="absolute inset-0 opacity-10" :class="slide.color.split(' ')[0].replace('text', 'bg')"></div>
                            <div class="absolute -right-20 -top-20 w-64 h-64 rounded-full opacity-20 blur-3xl" :class="slide.color.split(' ')[0].replace('text', 'bg')"></div>
                            
                            <!-- Slide Content -->
                            <div class="absolute inset-0 flex flex-col items-center justify-center p-8">
                                <div class="w-32 h-32 rounded-full bg-white flex items-center justify-center mb-8 shadow-xl border border-slate-50">
                                    <component :is="slide.icon" class="w-14 h-14" :class="slide.color.split(' ')[1]" />
                                </div>
                                <h3 class="text-3xl font-bold text-slate-800 mb-2">{{ slide.title }}</h3>
                                <div class="h-1 w-24 rounded-full bg-slate-200"></div>
                            </div>
                        </div>
                   </transition-group>
               </div>
               
               <!-- Carousel Indicators -->
               <div class="absolute -bottom-10 left-1/2 -translate-x-1/2 flex gap-3">
                   <button 
                      v-for="(_, index) in slides" 
                      :key="index"
                      @click="activeSlide = index"
                      class="h-2 rounded-full transition-all duration-300"
                      :class="activeSlide === index ? 'w-8 bg-blue-600' : 'w-2 bg-slate-300'"
                   ></button>
               </div>
           </div>
        </div>
      </div>
    </header>

    <!-- Workflow Section -->
    <section class="py-24 bg-white border-y border-slate-100">
       <div class="container mx-auto px-6">
          <div class="flex flex-col md:flex-row gap-16 items-center">
             <div class="md:w-1/2">
                <span class="text-blue-600 font-bold tracking-wider text-sm uppercase mb-2 block">Workflow</span>
                <h2 class="text-3xl font-bold mb-8 text-slate-900">Alur Kerja Sistem</h2>
                <div class="space-y-8">
                  <div v-for="(step, idx) in steps" :key="idx" class="flex gap-6 relative group">
                     <!-- Connector Line -->
                     <div v-if="idx !== steps.length - 1" class="absolute left-[1.65rem] top-12 bottom-[-2rem] w-px bg-slate-200 group-hover:bg-blue-200 transition-colors"></div>
                     
                     <div class="w-14 h-14 rounded-full bg-white border-4 border-slate-50 flex items-center justify-center shrink-0 z-10 font-bold text-slate-700 shadow-md group-hover:border-blue-50 group-hover:text-blue-600 transition-all">
                       {{ step.num }}
                     </div>
                     <div>
                       <h4 class="text-xl font-bold text-slate-800 mb-2 group-hover:text-blue-600 transition-colors">{{ step.title }}</h4>
                       <p class="text-slate-500">{{ step.desc }}</p>
                     </div>
                  </div>
                </div>
             </div>
             
             <!-- Workflow Feature Highlight -->
             <div class="md:w-1/2 relative">
                <div class="aspect-[4/3] bg-gradient-to-tr from-slate-50 to-white rounded-2xl border border-slate-200 p-8 shadow-2xl relative overflow-hidden">
                    <div class="absolute top-0 right-0 w-32 h-32 bg-blue-500/5 rounded-bl-full"></div>
                    
                    <div class="space-y-4">
                       <div class="h-8 w-1/3 bg-slate-200 rounded animate-pulse"></div>
                       <div class="h-4 w-2/3 bg-slate-100 rounded"></div>
                       <div class="h-32 w-full bg-slate-50 rounded-lg border border-slate-200 p-4 border-dashed border-2 flex items-center justify-center">
                          <span class="text-slate-400 font-medium text-sm">Document Verification Zone</span>
                       </div>
                    </div>

                    <!-- Floating Badge -->
                    <div class="absolute bottom-8 right-8 bg-white p-4 rounded-xl border border-slate-100 shadow-xl flex items-center gap-3 animate-bounce">
                        <CheckCircle2 class="text-emerald-500 w-8 h-8" />
                        <div>
                           <div class="text-xs text-slate-400 font-bold uppercase">Status</div>
                           <div class="font-bold text-slate-800">Verified</div>
                        </div>
                    </div>
                </div>
             </div>
          </div>
       </div>
    </section>

    <!-- Features Grid -->
    <section class="py-24">
        <div class="container mx-auto px-6">
            <div class="text-center mb-16">
              <span class="text-blue-600 font-bold tracking-wider text-sm uppercase mb-2 block">Capabilities</span>
              <h2 class="text-3xl font-bold mb-4 text-slate-900">Fitur Utama</h2>
              <p class="text-slate-500 max-w-2xl mx-auto">Dirancang untuk kecepatan dan akurasi, menggunakan teknologi terbaru untuk mendukung keputusan engineering.</p>
            </div>

            <div class="grid md:grid-cols-3 gap-8">
              <div v-for="(feat, idx) in features" :key="idx" 
                   class="p-8 rounded-2xl bg-white border border-slate-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all group">
                 <div class="w-14 h-14 rounded-xl flex items-center justify-center mb-6 transition-colors" :class="[feat.bg, feat.color, 'group-hover:scale-110 duration-300']">
                   <component :is="feat.icon" class="w-7 h-7" />
                 </div>
                 <h3 class="text-xl font-bold mb-3 text-slate-900">{{ feat.title }}</h3>
                 <p class="text-slate-500 leading-relaxed">{{ feat.desc }}</p>
              </div>
            </div>
            
            <!-- Gallery Visuals List -->
            <div class="mt-20 grid grid-cols-1 md:grid-cols-3 gap-6">
                <div v-for="(item, i) in galleryItems" :key="i" class="relative group overflow-hidden rounded-2xl aspect-video bg-white border border-slate-100 shadow-sm hover:shadow-lg transition-all">
                    <div class="absolute inset-0 bg-slate-50/50 group-hover:bg-blue-50/30 transition-colors"></div>
                    <div class="absolute inset-0 opacity-10 group-hover:opacity-20 transition-opacity bg-[radial-gradient(#3b82f6_1px,transparent_1px)] [background-size:16px_16px]"></div>
                    
                    <div class="absolute bottom-0 left-0 p-6 z-20">
                         <div class="w-10 h-10 rounded-lg bg-white shadow-sm text-blue-600 flex items-center justify-center mb-2">
                             <component :is="item.icon" class="w-5 h-5" />
                         </div>
                         <h4 class="font-bold text-lg text-slate-900">{{ item.title }}</h4>
                         <p class="text-xs text-slate-500">{{ item.desc }}</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="py-12 border-t border-slate-200 bg-white text-center text-slate-400 text-sm">
       <p>&copy; 2026 Aircraft Configuration Intelligence Platform. Restricted Access.</p>
    </footer>
  </div>
</template>

<style scoped>
.perspective-1000 {
    perspective: 1000px;
}
.rotate-y-10 {
    transform: rotateY(10deg);
}
.rotate-y-0 {
    transform: rotateY(0deg);
}
</style>
