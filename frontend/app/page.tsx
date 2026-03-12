import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import Projects from "./components/Projects";
import FundingCTA from "./components/FundingCTA";
import AboutSection from "./components/AboutSection";
import Footer from "./components/Footer";

export default function Home() {
  return (
    <main className="min-h-screen bg-[#0D0D11] text-white">
      <Navbar />
      <Hero />
      <Projects />
      <FundingCTA />
      <AboutSection />
      <Footer />
    </main>
  );
}
