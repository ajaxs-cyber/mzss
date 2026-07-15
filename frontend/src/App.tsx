import FractalCanvas from '@/components/FractalCanvas';
import Navigation from '@/components/Navigation';
import HeroSection from '@/sections/HeroSection';
import FeatureSection from '@/sections/FeatureSection';
import GallerySection from '@/sections/GallerySection';
import FooterSection from '@/sections/FooterSection';

function App() {
  return (
    <div className="relative min-h-screen" style={{ background: '#050505' }}>
      {/* WebGL Background */}
      <FractalCanvas />

      {/* Navigation */}
      <Navigation />

      {/* Content */}
      <main className="relative">
        <HeroSection />
        <FeatureSection />
        <GallerySection />
        <FooterSection />
      </main>
    </div>
  );
}

export default App;
