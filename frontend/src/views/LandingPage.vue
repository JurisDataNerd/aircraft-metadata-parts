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
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  MousePointer2
} from 'lucide-vue-next';
import { useMouse, useWindowScroll } from '@vueuse/core';

const router = useRouter();
const { x, y } = useMouse();
const { y: scrollY } = useWindowScroll();

const isLoaded = ref(false);

// Carousel State
const activeSlide = ref(0);
let carouselInterval: any;

onMounted(() => {
  setTimeout(() => isLoaded.value = true, 100);
  carouselInterval = setInterval(() => {
      activeSlide.value = (activeSlide.value + 1) % heroImages.length;
  }, 5000);
});

onUnmounted(() => {
    clearInterval(carouselInterval);
});

const navigateToLogin = () => {
  router.push('/login');
};

const heroImages = [
    { 
      src: '/hero1.webp', 
      title: 'Boeing 787-8', 
      tag: 'Advanced Composite',
      desc: 'Efisiensi bahan bakar maksimal dengan material mutakhir.' 
    },
    { 
      src: '/hero2.webp', 
      title: 'Precision Eng.', 
      tag: 'State-of-the-Art',
      desc: 'Manajemen konfigurasi dengan tingkat akurasi 99.9%.' 
    },
    { 
      src: '/hero3.webp', 
      title: 'Aviation Intelligence', 
      tag: 'Next-Gen',
      desc: 'Integrasi data real-time untuk keputusan kritis.' 
    }
];

const nextSlide = () => {
    activeSlide.value = (activeSlide.value + 1) % heroImages.length;
};

const prevSlide = () => {
    activeSlide.value = (activeSlide.value - 1 + heroImages.length) % heroImages.length;
};

const features = [
  {
    title: 'Satu Sumber Kebenaran',
    desc: 'Menyatukan data IPD dan Drawing dalam satu database terstruktur yang deterministik.',
    icon: Database,
    color: 'text-blue-600',
    bg: 'bg-blue-50',
    border: 'border-blue-100'
  },
  {
    title: 'Pencegahan Kesalahan',
    desc: 'Guardrail system yang mencegah pemilihan part yang salah dengan validasi dokumen.',
    icon: ShieldCheck,
    color: 'text-emerald-600',
    bg: 'bg-emerald-50',
    border: 'border-emerald-100'
  },
  {
    title: 'Analisis Risiko Cerdas',
    desc: 'Mendeteksi alternatif part dan menghitung skor risiko berdasarkan data historis.',
    icon: BrainCircuit,
    color: 'text-violet-600',
    bg: 'bg-violet-50',
    border: 'border-violet-100'
  }
];

const steps = [
  { num: '01', title: 'Cari Konfigurasi', desc: 'Input Line Number atau Part Number aircraft.' },
  { num: '02', title: 'Analisis Otomatis', desc: 'Sistem memfilter effectivity dan mengecek drawing.' },
  { num: '03', title: 'Review Keputusan', desc: 'Lihat preview risiko dan alternatif sebelum konfirmasi.' },
  { num: '04', title: 'Log Tercatat', desc: 'Setiap keputusan tersimpan untuk audit trail.' }
];

const galleryItems = [
    { title: 'Interactive Search', icon: Layers, desc: 'Pencarian cepat cerdas' },
    { title: 'Real-time Validation', icon: Zap, desc: 'Validasi instan resmi' },
    { title: 'Risk Visualization', icon: Activity, desc: 'Indikator visual potensi' }
];
</script>

<template>
  <div class="min-h-screen bg-[#F8FAFC] text-slate-900 font-sans overflow-x-hidden selection:bg-blue-600 selection:text-white">
    
    <nav class="fixed top-0 w-full z-[100] transition-all duration-500"
         :class="scrollY > 20 ? 'py-3' : 'py-6'">
      <div class="container mx-auto px-6">
        <div class="bg-white/70 backdrop-blur-xl border border-white shadow-[0_8px_32px_rgba(0,0,0,0.04)] rounded-2xl px-6 py-3 flex items-center justify-between transition-all">
          <div class="flex items-center gap-2 group cursor-pointer">
             <div class="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-600/20 group-hover:rotate-12 transition-transform duration-500">
               <Plane class="text-white w-5 h-5 -rotate-45" />
             </div>
             <span class="text-xl font-black tracking-tighter text-slate-900 uppercase">Aircraft<span class="text-blue-600 italic">Config</span></span>
          </div>
          
          <button @click="navigateToLogin" class="flex items-center gap-2 px-6 py-2.5 bg-slate-900 text-white rounded-xl font-bold hover:bg-blue-600 transition-all duration-300 group shadow-lg shadow-slate-900/10 hover:shadow-blue-600/20">
            Masuk Aplikasi
            <ArrowRight class="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </div>
    </nav>

    <header class="relative pt-40 pb-20 lg:pt-48 lg:pb-32 overflow-hidden bg-white">
      <div class="absolute top-0 right-0 w-1/2 h-full bg-blue-50/50 skew-x-12 translate-x-24 -z-10"></div>
      <div class="absolute -top-24 -left-24 w-96 h-96 bg-blue-600/5 rounded-full blur-[100px] -z-10"></div>

      <div class="container mx-auto px-6">
        <div class="grid lg:grid-cols-12 gap-12 items-center">
          
          <div class="lg:col-span-5 space-y-8" :class="isLoaded ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-10'" style="transition: all 1s ease-out">
            <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-600/10 border border-blue-600/10 text-blue-700 text-xs font-black uppercase tracking-widest">
              <span class="relative flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-blue-600"></span>
              </span>
              Intelligence Platform 2026
            </div>

            <h1 class="text-6xl lg:text-[5.5rem] font-black leading-[0.9] text-slate-900 tracking-tighter">
              MANAGE <br/>
              <span class="text-blue-600">CONFIG</span> <br/>
              WITH PRIDE.
            </h1>

            <p class="text-lg text-slate-500 max-w-md leading-relaxed">
              Sinkronisasi deterministik antara data <span class="text-slate-900 font-bold">IPD & Drawing</span>. Presisi tinggi untuk standar keamanan penerbangan global.
            </p>

            <div class="flex flex-col sm:flex-row gap-4">
              <button @click="navigateToLogin" class="h-14 px-10 rounded-2xl bg-blue-600 text-white font-black hover:bg-slate-900 transition-all duration-300 shadow-xl shadow-blue-600/20 flex items-center justify-center gap-3 group">
                Mulai Sekarang
                <ArrowRight class="w-5 h-5 group-hover:translate-x-2 transition-transform" />
              </button>
              <div class="flex -space-x-3 items-center">
                <div v-for="i in 4" :key="i" class="w-10 h-10 rounded-full border-4 border-white bg-slate-200"></div>
                <span class="pl-6 text-sm font-bold text-slate-400">+1.2k Users</span>
              </div>
            </div>
          </div>

          <div class="lg:col-span-7 relative h-[500px] lg:h-[600px]" :class="isLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'" style="transition: all 1s 0.2s ease-out">
            
            <div class="absolute inset-0 z-20 group">
               <transition-group name="slide-fade">
                <div v-for="(slide, index) in heroImages" 
                     v-show="activeSlide === index" 
                     :key="index"
                     class="absolute inset-0 bg-white rounded-[2.5rem] overflow-hidden shadow-[0_32px_64px_rgba(0,0,0,0.1)] border-8 border-white">
                  <img :src="slide.src" :alt="slide.title" class="w-full h-full object-cover scale-105 group-hover:scale-110 transition-transform duration-[4s]" />
                  <div class="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-transparent to-transparent"></div>
                  
                  <div class="absolute bottom-8 left-8 right-8 flex items-end justify-between">
                    <div class="text-white space-y-1">
                      <span class="px-3 py-1 bg-blue-600 rounded-lg text-[10px] font-black uppercase tracking-widest">{{ slide.tag }}</span>
                      <h3 class="text-3xl font-black italic uppercase leading-none pt-2">{{ slide.title }}</h3>
                      <p class="text-white/70 text-sm max-w-[200px] leading-tight">{{ slide.desc }}</p>
                    </div>
                    
                    <div class="flex gap-2">
                      <button @click.stop="prevSlide" class="w-12 h-12 rounded-xl bg-white/10 backdrop-blur-md border border-white/20 flex items-center justify-center text-white hover:bg-white hover:text-blue-600 transition-all">
                        <ChevronLeft class="w-6 h-6" />
                      </button>
                      <button @click.stop="nextSlide" class="w-12 h-12 rounded-xl bg-white/10 backdrop-blur-md border border-white/20 flex items-center justify-center text-white hover:bg-white hover:text-blue-600 transition-all">
                        <ChevronRight class="w-6 h-6" />
                      </button>
                    </div>
                  </div>
                </div>
               </transition-group>
            </div>

            <div class="absolute top-8 -right-8 w-full h-full bg-blue-100 rounded-[2.5rem] -z-10 rotate-3"></div>
            <div class="absolute -bottom-4 -left-4 w-48 h-48 bg-white rounded-3xl shadow-xl z-30 p-6 flex flex-col justify-between border border-slate-50 animate-float">
                <div class="w-10 h-10 rounded-full bg-emerald-500 flex items-center justify-center text-white shadow-lg shadow-emerald-500/20">
                  <CheckCircle2 class="w-6 h-6" />
                </div>
                <div>
                  <div class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Verification</div>
                  <div class="text-lg font-black text-slate-900">100% Valid</div>
                </div>
            </div>

            <div class="absolute -top-10 right-10 w-40 h-40 bg-slate-900 rounded-3xl shadow-2xl z-30 p-6 flex flex-col justify-center items-center text-center animate-float-delayed">
                <Activity class="text-blue-400 w-8 h-8 mb-2" />
                <div class="text-2xl font-black text-white leading-none">2.4s</div>
                <div class="text-[10px] font-bold text-slate-500 uppercase mt-1">Response Time</div>
            </div>
          </div>

        </div>
      </div>
    </header>

    <section class="relative py-32 lg:py-48 overflow-hidden group">
       <div class="absolute inset-0 z-0 scale-110 group-hover:scale-100 transition-transform duration-[10s]">
          <img src="/hanggar.webp" alt="Aircraft Hangar" class="w-full h-full object-cover" />
          <div class="absolute inset-0 bg-gradient-to-b from-white via-transparent to-slate-900"></div>
          <div class="absolute inset-0 bg-blue-900/40 mix-blend-multiply"></div>
       </div>
       
       <div class="container mx-auto px-6 relative z-10">
          <div class="max-w-4xl mx-auto text-center space-y-8">
             <div class="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white/10 backdrop-blur-md border border-white/20 text-white font-bold uppercase tracking-[0.2em] text-xs">
               Precision Hangar Environment
             </div>
             <h2 class="text-5xl lg:text-7xl font-black text-white tracking-tighter italic uppercase">
                Trust by <span class="text-blue-400">Engineering</span> Professionals
             </h2>
             <p class="text-slate-200 text-xl max-w-2xl mx-auto font-medium">
                Sistem kami bekerja di balik layar fasilitas pemeliharaan terbesar, memastikan setiap baut dan komponen terdaftar dengan sempurna.
             </p>
             
             <div class="grid grid-cols-2 lg:grid-cols-4 gap-8 pt-12">
                <div v-for="stat in [{v:'10k+', l:'Parts'}, {v:'500+', l:'Docs'}, {v:'99.9%', l:'Accuracy'}, {v:'24/7', l:'Active'}]" :key="stat.l" 
                     class="p-6 rounded-2xl bg-white/5 backdrop-blur-lg border border-white/10 group/stat hover:bg-white/20 transition-all">
                  <div class="text-4xl font-black text-white group-hover/stat:scale-110 transition-transform">{{ stat.v }}</div>
                  <div class="text-blue-300 text-[10px] font-black uppercase tracking-widest mt-2">{{ stat.l }}</div>
                </div>
             </div>
          </div>
       </div>
    </section>

    <section class="py-32 bg-white">
      <div class="container mx-auto px-6">
        <div class="flex flex-col lg:flex-row lg:items-end justify-between mb-20 gap-8">
          <div class="max-w-2xl space-y-4">
            <span class="text-blue-600 font-black tracking-[0.3em] uppercase text-xs">Capabilities</span>
            <h2 class="text-5xl font-black text-slate-900 tracking-tighter uppercase italic">Engineered for <br/> Absolute Safety.</h2>
          </div>
          <p class="text-slate-500 max-w-sm lg:text-right">Setiap fitur dirancang untuk menghilangkan ambiguitas dalam pengambilan keputusan engineering.</p>
        </div>

        <div class="grid md:grid-cols-3 gap-8">
          <div v-for="(feat, idx) in features" :key="idx" 
               class="p-10 rounded-[2.5rem] border bg-white hover:shadow-[0_32px_64px_rgba(0,0,0,0.06)] hover:-translate-y-2 transition-all duration-500 group"
               :class="feat.border">
            <div class="w-16 h-16 rounded-2xl flex items-center justify-center mb-8 transition-transform duration-500 group-hover:rotate-[15deg]" :class="feat.bg">
              <component :is="feat.icon" class="w-8 h-8" :class="feat.color" />
            </div>
            <h3 class="text-2xl font-black mb-4 text-slate-900 uppercase italic leading-none">{{ feat.title }}</h3>
            <p class="text-slate-500 leading-relaxed">{{ feat.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="py-32 bg-slate-50">
      <div class="container mx-auto px-6">
        <div class="bg-white rounded-[3rem] p-8 lg:p-20 shadow-sm border border-slate-200 grid lg:grid-cols-2 gap-20 items-center">
          <div class="space-y-12">
            <div>
              <h2 class="text-4xl font-black text-slate-900 uppercase tracking-tighter">System Workflow</h2>
              <p class="text-slate-400 mt-2">Integrasi seamless dari input data hingga laporan final.</p>
            </div>
            
            <div class="space-y-10">
              <div v-for="(step, idx) in steps" :key="idx" class="flex gap-6 group">
                <div class="text-5xl font-black text-slate-100 group-hover:text-blue-100 transition-colors duration-300 leading-none">{{ step.num }}</div>
                <div>
                  <h4 class="text-xl font-black text-slate-900 uppercase italic">{{ step.title }}</h4>
                  <p class="text-slate-500">{{ step.desc }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="relative">
             <div class="aspect-square bg-slate-50 rounded-[3rem] border border-slate-100 p-12 flex items-center justify-center">
                <div class="relative w-full h-full bg-white rounded-3xl shadow-xl border border-slate-100 p-8 flex flex-col justify-center text-center animate-pulse">
                   <div class="w-20 h-20 bg-blue-600 rounded-full mx-auto flex items-center justify-center text-white mb-6 shadow-xl shadow-blue-600/30">
                      <Zap class="w-10 h-10" />
                   </div>
                   <h3 class="text-2xl font-black uppercase text-slate-900 tracking-tighter">Analyzing Data...</h3>
                   <div class="mt-8 space-y-3">
                      <div class="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                        <div class="h-full bg-blue-600 w-2/3"></div>
                      </div>
                      <div class="flex justify-between text-[10px] font-black text-slate-400 uppercase tracking-widest">
                        <span>Drawing Sync</span>
                        <span>88%</span>
                      </div>
                   </div>
                </div>
                <div class="absolute top-0 right-0 p-4 bg-emerald-500 text-white rounded-2xl shadow-xl rotate-12 flex items-center gap-2 font-bold text-sm">
                   <CheckCircle2 class="w-5 h-5" /> Verified
                </div>
             </div>
          </div>
        </div>
      </div>
    </section>

    <footer class="py-20 bg-white border-t border-slate-100">
       <div class="container mx-auto px-6 text-center">
          <div class="flex items-center justify-center gap-2 mb-8 opacity-30 grayscale">
             <Plane class="text-slate-900 w-6 h-6 -rotate-45" />
             <span class="text-xl font-black tracking-tighter text-slate-900 uppercase italic">Aircraft<span class="text-blue-600">Config</span></span>
          </div>
          <p class="text-slate-400 text-xs font-bold uppercase tracking-[0.3em]">&copy; 2026 Aircraft Configuration Intelligence Platform. Restricted Access.</p>
       </div>
    </footer>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

:deep(body) {
  font-family: 'Inter', sans-serif;
}

/* Slide Fade Transition */
.slide-fade-enter-active {
  transition: all 0.8s ease-out;
}
.slide-fade-leave-active {
  transition: all 0.6s cubic-bezier(1, 0.5, 0.8, 1);
}
.slide-fade-enter-from {
  transform: translateX(20px) rotate(2deg);
  opacity: 0;
}
.slide-fade-leave-to {
  transform: translateX(-20px) rotate(-2deg);
  opacity: 0;
}

/* Floating Animations */
@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-15px) rotate(2deg); }
}

@keyframes float-delayed {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-10px) rotate(-2deg); }
}

.animate-float {
  animation: float 5s ease-in-out infinite;
}

.animate-float-delayed {
  animation: float-delayed 6s ease-in-out infinite;
  animation-delay: 1s;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: #f1f5f9;
}
::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
  background: #3b82f6;
}
</style>