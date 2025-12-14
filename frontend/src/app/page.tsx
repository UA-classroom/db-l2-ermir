import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[#0f0f1a]">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0f0f1a]/80 backdrop-blur-lg border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between h-20 items-center">
            <Link href="/" className="flex items-center gap-2">
              <span className="text-2xl font-light tracking-wider text-white">
                Comfort<span className="font-semibold text-[#d4af37]">Booking</span>
              </span>
            </Link>
            <div className="hidden md:flex items-center gap-8">
              <Link
                href="/browse"
                className="text-gray-400 hover:text-white font-light tracking-wide transition-colors"
              >
                Discover
              </Link>
              <Link
                href="/login"
                className="text-gray-400 hover:text-white font-light tracking-wide transition-colors"
              >
                Sign In
              </Link>
              <Link
                href="/register/customer"
                className="px-6 py-2.5 border border-[#d4af37] text-[#d4af37] font-light tracking-wide rounded hover:bg-[#d4af37] hover:text-[#0f0f1a] transition-all duration-300"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#0f0f1a] via-[#1a1a2e] to-[#16213e]"></div>

        {/* Decorative elements */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#d4af37]/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-[#d4af37]/10 rounded-full blur-3xl"></div>

        {/* Content */}
        <div className="relative z-10 max-w-5xl mx-auto px-6 text-center">
          <p className="text-[#d4af37] text-sm tracking-[0.3em] uppercase mb-6 animate-fadeIn">
            Premium Booking Experience
          </p>
          <h1 className="text-5xl md:text-7xl font-light text-white leading-tight mb-8">
            Book Your Moment
            <br />
            <span className="text-gold-gradient font-semibold">of Comfort</span>
          </h1>
          <p className="text-xl text-gray-400 font-light max-w-2xl mx-auto mb-12 leading-relaxed">
            Discover and book exclusive services from premium salons, spas,
            and wellness centers. Your perfect appointment awaits.
          </p>
          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <Link
              href="/browse"
              className="group px-10 py-4 bg-gradient-to-r from-[#d4af37] to-[#b8960f] text-[#0f0f1a] font-medium tracking-wide rounded hover:shadow-[0_0_30px_rgba(212,175,55,0.4)] transition-all duration-300"
            >
              Explore Services
              <span className="ml-2 group-hover:ml-4 transition-all">→</span>
            </Link>
            <Link
              href="/register/provider"
              className="px-10 py-4 border border-white/20 text-white font-light tracking-wide rounded hover:bg-white/5 hover:border-white/40 transition-all duration-300"
            >
              List Your Business
            </Link>
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
          <div className="w-6 h-10 border border-white/20 rounded-full flex items-start justify-center p-2">
            <div className="w-1 h-2 bg-[#d4af37] rounded-full"></div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-32 bg-[#1a1a2e]">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="text-center mb-20">
            <p className="text-[#d4af37] text-sm tracking-[0.3em] uppercase mb-4">
              The Experience
            </p>
            <h2 className="text-4xl md:text-5xl font-light text-white">
              Effortless Elegance
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="group p-8 bg-[#16213e]/50 border border-white/5 rounded-lg hover:border-[#d4af37]/30 transition-all duration-500">
              <div className="w-14 h-14 mb-6 rounded-full bg-[#d4af37]/10 flex items-center justify-center">
                <span className="text-2xl text-[#d4af37]">✦</span>
              </div>
              <h3 className="text-xl font-light text-white mb-3">
                Curated Selection
              </h3>
              <p className="text-gray-400 font-light leading-relaxed">
                Handpicked premium service providers, vetted for excellence and quality.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="group p-8 bg-[#16213e]/50 border border-white/5 rounded-lg hover:border-[#d4af37]/30 transition-all duration-500">
              <div className="w-14 h-14 mb-6 rounded-full bg-[#d4af37]/10 flex items-center justify-center">
                <span className="text-2xl text-[#d4af37]">◈</span>
              </div>
              <h3 className="text-xl font-light text-white mb-3">
                Seamless Booking
              </h3>
              <p className="text-gray-400 font-light leading-relaxed">
                Book your perfect slot in seconds. Real-time availability, instant confirmation.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="group p-8 bg-[#16213e]/50 border border-white/5 rounded-lg hover:border-[#d4af37]/30 transition-all duration-500">
              <div className="w-14 h-14 mb-6 rounded-full bg-[#d4af37]/10 flex items-center justify-center">
                <span className="text-2xl text-[#d4af37]">❖</span>
              </div>
              <h3 className="text-xl font-light text-white mb-3">
                Premium Experience
              </h3>
              <p className="text-gray-400 font-light leading-relaxed">
                From booking to service, every touchpoint designed for your comfort.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 bg-[#0f0f1a] relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-[#d4af37]/5 to-transparent"></div>
        <div className="relative max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-4xl md:text-5xl font-light text-white mb-6">
            Elevate Your Business
          </h2>
          <p className="text-xl text-gray-400 font-light mb-12 max-w-2xl mx-auto">
            Join our exclusive network of premium service providers.
            Let discerning clients discover your exceptional services.
          </p>
          <Link
            href="/register/provider"
            className="inline-flex px-12 py-4 bg-[#d4af37] text-[#0f0f1a] font-medium tracking-wide rounded hover:bg-[#e8c547] transition-all duration-300"
          >
            Become a Partner
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-16 bg-[#0a0a12] border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-8">
            <div>
              <span className="text-xl font-light tracking-wider text-white">
                Comfort<span className="font-semibold text-[#d4af37]">Booking</span>
              </span>
              <p className="text-gray-500 text-sm mt-2">Premium booking experiences</p>
            </div>
            <div className="flex gap-8 text-sm text-gray-400">
              <Link href="/about" className="hover:text-[#d4af37] transition-colors">About</Link>
              <Link href="/contact" className="hover:text-[#d4af37] transition-colors">Contact</Link>
              <Link href="/privacy" className="hover:text-[#d4af37] transition-colors">Privacy</Link>
              <Link href="/terms" className="hover:text-[#d4af37] transition-colors">Terms</Link>
            </div>
            <div className="text-sm text-gray-500">
              © 2024 ComfortBooking
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
