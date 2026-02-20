import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import "./terms.css";

const SECTIONS = [
  {
    title: "1. Acceptance of Terms",
    body: `By accessing or using E.V.E. (Execution Versatility Engine), you agree to be bound by these Terms and Conditions. If you do not agree to any part of these terms, you may not use the service. These terms apply to all visitors, users, and others who access or use the platform.`,
  },
  {
    title: "2. Description of Service",
    body: `E.V.E. is an AI-powered multi-agent orchestration platform developed by NAICO ITS. The service provides intelligent task distribution, natural language processing, image generation, code assistance, and related AI-driven capabilities. Features may be updated, modified, or discontinued at any time without prior notice.`,
  },
  {
    title: "3. User Accounts",
    body: `You are responsible for maintaining the confidentiality of your account credentials. You must provide accurate and complete information when registering. You are solely responsible for all activities that occur under your account. Notify us immediately of any unauthorised use. We reserve the right to suspend or terminate accounts that violate these terms.`,
  },
  {
    title: "4. Acceptable Use",
    body: `You agree not to use E.V.E. to generate, distribute, or promote content that is unlawful, harmful, abusive, defamatory, or otherwise objectionable. You may not attempt to reverse-engineer, scrape, or probe the platform's infrastructure. Automated access beyond the provided API is prohibited without written consent.`,
  },
  {
    title: "5. Intellectual Property",
    body: `All platform code, design, branding, and underlying models remain the property of NAICO ITS and its licensors. Content you submit remains yours; however, you grant E.V.E. a non-exclusive licence to process it for the purpose of providing the service. AI-generated outputs are provided as-is and carry no IP warranty.`,
  },
  {
    title: "6. Privacy & Data",
    body: `We collect and process data as described in our Privacy Policy. Conversation history is stored to enable continuity across sessions and may be used to improve service quality in aggregated, anonymised form. We do not sell personal data to third parties. You may request deletion of your data at any time by contacting us.`,
  },
  {
    title: "7. Disclaimers",
    body: `E.V.E. is provided "as is" without warranties of any kind. AI-generated responses may be inaccurate, incomplete, or outdated. The platform is not a substitute for professional advice — legal, medical, financial, or otherwise. We do not guarantee uninterrupted or error-free service.`,
  },
  {
    title: "8. Limitation of Liability",
    body: `To the fullest extent permitted by law, NAICO ITS shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising from your use of, or inability to use, the service — even if advised of the possibility of such damages.`,
  },
  {
    title: "9. Changes to Terms",
    body: `We reserve the right to update these Terms at any time. Continued use of the service after changes are posted constitutes acceptance of the revised terms. We will make reasonable efforts to notify registered users of material changes via email or in-platform notice.`,
  },
  {
    title: "10. Contact",
    body: `For questions regarding these Terms, contact us at ignite.techteam33@gmail.com or visit naicoits.com. Our support team will respond within a reasonable timeframe.`,
  },
];

export default function TermsAndConditions() {
  const navigate = useNavigate();

  useEffect(() => {
    window.scrollTo({ top: 0 });
  }, []);

  return (
    <div className="terms-page">
      <div className="terms-inner">

        {/* ── Back button ── */}
        <button className="terms-back" onClick={() => navigate(-1)}>
          <ArrowLeft size={15} />
          <span>Back</span>
        </button>

        {/* ── Header ── */}
        <header className="terms-header">
          <p className="terms-eyebrow">Legal</p>
          <h1 className="terms-title">Terms &amp; Conditions</h1>
          <p className="terms-updated">Last updated: February 2026</p>
        </header>

        {/* ── Intro ── */}
        <p className="terms-intro">
          Please read these terms carefully before using E.V.E. They govern your
          access to and use of the platform provided by{" "}
          <a href="https://naicoits.com/" target="_blank" rel="noopener noreferrer">
            NAICO ITS
          </a>
          .
        </p>

        {/* ── Sections ── */}
        <div className="terms-sections">
          {SECTIONS.map((s) => (
            <section key={s.title} className="terms-section">
              <h2 className="terms-section-title">{s.title}</h2>
              <p className="terms-section-body">{s.body}</p>
            </section>
          ))}
        </div>

        {/* ── Footer note ── */}
        <p className="terms-footer-note">
          By using E.V.E., you acknowledge that you have read, understood, and
          agree to be bound by these Terms and Conditions.
        </p>

      </div>
    </div>
  );
}